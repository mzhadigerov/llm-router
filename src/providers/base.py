class LLMProvider:
    def __init__(self, provider_name, config, api_key=None):
        self.name = provider_name
        self.config = config
        self.api_key = api_key
        
        # Extract configuration
        self.base_url = config.get("base_url", "")
        self.rate_limits = config.get("rate_limits", {})
        self.available_models = config.get("models", {})
        
    async def generate(self, prompt, model_name, options=None):
        """Generate a response using the specified model"""
        raise NotImplementedError
        
    def get_rate_limit_info(self):
        """Return rate limit information for this provider"""
        return self.rate_limits
        
    def check_availability(self):
        """Check if this provider is currently available"""
        raise NotImplementedError
        
    def supports_model(self, model_name):
        """Check if this provider supports the specified model"""
        return model_name in self.available_models