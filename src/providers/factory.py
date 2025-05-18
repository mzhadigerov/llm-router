from .groq import GroqProvider
from .openrouter import OpenRouterProvider  # You'll need to implement this
from .perplexity import PerplexityProvider  # You'll need to implement this
from ..utils.config import load_provider_config

# Map provider names to their classes
PROVIDER_CLASSES = {
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "perplexity": PerplexityProvider,
    # Add more providers here
}

def create_provider(provider_name, api_key=None):
    """Create a provider instance from configuration"""
    # Load all provider configs
    provider_configs = load_provider_config()
    
    # Check if provider exists in config
    if provider_name not in provider_configs:
        raise ValueError(f"Provider {provider_name} not found in configuration")
    
    # Check if provider class exists
    if provider_name not in PROVIDER_CLASSES:
        raise ValueError(f"Provider {provider_name} not implemented")
    
    # Get provider config and class
    provider_config = provider_configs[provider_name]
    provider_class = PROVIDER_CLASSES[provider_name]
    
    # Create and return provider instance
    return provider_class(provider_config, api_key)

def create_all_providers(api_keys=None):
    """Create all configured providers
    
    Args:
        api_keys: Dictionary mapping provider names to API keys
    
    Returns:
        List of provider instances
    """
    api_keys = api_keys or {}
    provider_configs = load_provider_config()
    providers = []
    
    for provider_name, config in provider_configs.items():
        if provider_name in PROVIDER_CLASSES:
            api_key = api_keys.get(provider_name)
            provider_class = PROVIDER_CLASSES[provider_name]
            providers.append(provider_class(config, api_key))
    
    return providers