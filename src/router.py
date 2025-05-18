# src/router.py
import heapq
import time
import logging
from typing import Dict, List, Tuple, Any, Optional
from .providers.factory import create_all_providers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_router")

class LLMRouter:
    def __init__(self, api_keys=None):
        self.providers = {}  # name: provider_instance
        self.model_map = {}  # model_name: list of providers that support it
        self.provider_health = {}  # provider_name: health metrics
        
        # Initialize providers from config
        self._initialize_providers(api_keys)
        
    def _initialize_providers(self, api_keys=None):
        """Initialize all providers from configuration"""
        providers = create_all_providers(api_keys)
        
        for provider in providers:
            self.add_provider(provider)
            # Initialize health metrics
            self.provider_health[provider.name] = {
                "success_count": 0,
                "error_count": 0,
                "last_success_time": 0,
                "last_error_time": 0,
                "consecutive_errors": 0
            }
    
    def add_provider(self, provider):
        """Add a provider to the router"""
        self.providers[provider.name] = provider
        
        # Update model map
        for model_name in provider.available_models:
            if model_name not in self.model_map:
                self.model_map[model_name] = []
            self.model_map[model_name].append(provider.name)
            
    def remove_provider(self, provider_name):
        """Remove a provider from the router"""
        if provider_name in self.providers:
            provider = self.providers[provider_name]
            
            # Update model map
            for model_name in provider.available_models:
                if model_name in self.model_map and provider_name in self.model_map[model_name]:
                    self.model_map[model_name].remove(provider_name)
                    
            # Remove provider and health metrics
            del self.providers[provider_name]
            if provider_name in self.provider_health:
                del self.provider_health[provider_name]
    
    def list_available_models(self):
        """List all available models across providers"""
        return list(self.model_map.keys())
    
    def _update_provider_health(self, provider_name, success=True, error_message=None):
        """Update health metrics for a provider"""
        if provider_name not in self.provider_health:
            return
            
        current_time = time.time()
        health = self.provider_health[provider_name]
        
        if success:
            health["success_count"] += 1
            health["last_success_time"] = current_time
            health["consecutive_errors"] = 0
        else:
            health["error_count"] += 1
            health["last_error_time"] = current_time
            health["consecutive_errors"] += 1
            logger.warning(f"Provider {provider_name} error: {error_message}")
    
    def _get_provider_score(self, provider_name, model_name):
        """Calculate a score for provider selection based on quality and health"""
        if provider_name not in self.providers:
            return float('-inf')
            
        provider = self.providers[provider_name]
        if not provider.check_availability():
            return float('-inf')
            
        # Base score is the model quality
        quality_score = provider.available_models.get(model_name, 0)
        
        # Adjust for health
        health = self.provider_health[provider_name]
        health_penalty = min(health["consecutive_errors"] * 2, 10)
        
        # Calculate final score
        score = quality_score - health_penalty
        
        return score
    
    def get_best_provider_for_model(self, model_name):
        """Get the best available provider for a specific model"""
        if model_name not in self.model_map:
            return None
            
        # Find all providers that support this model
        candidate_providers = []
        for provider_name in self.model_map[model_name]:
            provider = self.providers[provider_name]
            score = self._get_provider_score(provider_name, model_name)
            
            if score > float('-inf'):  # Provider is available
                # Using negative score because heapq is a min-heap
                candidate_providers.append((-score, provider_name))
        
        if not candidate_providers:
            return None
            
        # Get the provider with the highest score
        heapq.heapify(candidate_providers)
        _, best_provider_name = heapq.heappop(candidate_providers)
        return self.providers[best_provider_name]
    
    async def generate(self, prompt, model_name=None, options=None):
        """Generate a response using the best available provider"""
        options = options or {}
        
        if model_name:
            # Specific model requested
            return await self._generate_with_model(prompt, model_name, options)
        else:
            # No specific model requested, use the best available model
            return await self._generate_with_best_model(prompt, options)
    
    async def _generate_with_model(self, prompt, model_name, options):
        """Generate with a specific model, trying providers in order of preference"""
        if model_name not in self.model_map:
            return {"error": f"Model {model_name} not available"}
            
        # Get all providers that support this model in order of quality score
        provider_names = self.model_map[model_name]
        provider_scores = [(self._get_provider_score(name, model_name), name) 
                         for name in provider_names]
        
        # Sort by score, highest first
        provider_scores.sort(reverse=True)
        
        # Try providers in order
        for score, provider_name in provider_scores:
            if score <= float('-inf'):  # Provider not available
                continue
                
            provider = self.providers[provider_name]
            logger.info(f"Trying {provider_name} for model {model_name}")
            
            try:
                result = await provider.generate(prompt, model_name, options)
                
                if "error" in result:
                    self._update_provider_health(provider_name, False, result["error"])
                    # Rate limit errors should be handled specially
                    if result["error"] == "rate_limit_exceeded":
                        logger.info(f"Rate limit exceeded for {provider_name}, trying next provider")
                        continue
                else:
                    self._update_provider_health(provider_name, True)
                    return result
            except Exception as e:
                self._update_provider_health(provider_name, False, str(e))
                logger.exception(f"Error generating with {provider_name}: {e}")
        
        return {"error": f"All providers for model {model_name} failed or unavailable"}
    
    async def _generate_with_best_model(self, prompt, options):
        """Generate using the best available model across all providers"""
        all_models = self.list_available_models()
        
        # Create a list of (model, best provider, quality score)
        model_provider_pairs = []
        for model in all_models:
            provider = self.get_best_provider_for_model(model)
            if provider:
                score = provider.available_models[model]
                model_provider_pairs.append((-score, model, provider))
        
        if not model_provider_pairs:
            return {"error": "No available providers"}
            
        # Sort by quality score (negative because we want highest first)
        heapq.heapify(model_provider_pairs)
        
        # Try models in order
        errors = []
        while model_provider_pairs:
            _, best_model, best_provider = heapq.heappop(model_provider_pairs)
            
            logger.info(f"Trying {best_provider.name} with model {best_model}")
            
            try:
                result = await best_provider.generate(prompt, best_model, options)
                
                if "error" in result:
                    self._update_provider_health(best_provider.name, False, result["error"])
                    errors.append(f"{best_provider.name}/{best_model}: {result['error']}")
                    
                    # Rate limit errors should be handled specially
                    if result["error"] == "rate_limit_exceeded":
                        logger.info(f"Rate limit exceeded for {best_provider.name}, trying next model")
                        continue
                else:
                    self._update_provider_health(best_provider.name, True)
                    return result
            except Exception as e:
                self._update_provider_health(best_provider.name, False, str(e))
                errors.append(f"{best_provider.name}/{best_model}: {str(e)}")
                logger.exception(f"Error generating with {best_provider.name}: {e}")
        
        return {
            "error": "All models and providers failed",
            "details": errors
        }