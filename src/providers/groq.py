# src/providers/groq.py
import httpx
import time
import json
from .base import LLMProvider

class GroqProvider(LLMProvider):
    def __init__(self, config, api_key=None):
        super().__init__("groq", config, api_key)
        self.request_history = []
        
    async def generate(self, prompt, model_name, options=None):
        if not self.supports_model(model_name):
            raise ValueError(f"Model {model_name} not supported by {self.name}")
            
        options = options or {}
        
        # Prepare the request payload
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": options.get("max_tokens", 1024),
            "temperature": options.get("temperature", 0.7),
            "stream": options.get("stream", False)
        }
        
        # Add system message if provided
        if "system_message" in options:
            payload["messages"].insert(0, {
                "role": "system", 
                "content": options["system_message"]
            })
        
        # Set up headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Record this request attempt
        self._record_request()
        
        # Make the API call
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=options.get("timeout", 30)
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract and return the generated text
                return {
                    "text": data["choices"][0]["message"]["content"],
                    "provider": self.name,
                    "model": model_name,
                    "usage": data.get("usage", {}),
                    "raw_response": data
                }
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limit exceeded
                    return {"error": "rate_limit_exceeded", "provider": self.name}
                else:
                    return {"error": f"API error: {str(e)}", "provider": self.name}
            except httpx.RequestError as e:
                return {"error": f"Request error: {str(e)}", "provider": self.name}
    
    def check_availability(self):
        """Check if we're below rate limits"""
        current_time = time.time()
        one_minute_ago = current_time - 60
        
        # Count requests in the last minute
        recent_requests = [r for r in self.request_history if r > one_minute_ago]
        
        requests_limit = self.rate_limits.get("requests_per_minute", 30)
        return len(recent_requests) < requests_limit
    
    def _record_request(self):
        """Record a timestamp for a request to track rate limits"""
        self.request_history.append(time.time())
        
        # Clean up old history (older than 5 minutes)
        five_minutes_ago = time.time() - 300
        self.request_history = [r for r in self.request_history if r > five_minutes_ago]