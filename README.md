# Free LLM Router

A Python library that routes requests to free LLM API providers, prioritizing models by quality and ensuring high availability by automatically handling rate limits and fallbacks.

## Features

- **Always Free**: Uses only free-tier API services
- **Smart Routing**: Automatically routes requests to the best available API
- **Rate Limit Management**: Avoids rate limits by intelligently routing between providers
- **Quality Ranking**: Prioritizes higher-quality models when available
- **Easy Integration**: Simple API that works with any Python application

## Installation

```bash
pip install free-llm-router

## Quick Start

```
import asyncio
from free_llm_router import LLMRouter

async def main():
    # Initialize the router with only the API keys you have
    # You don't need keys for all providers - just use what you have
    router = LLMRouter({
        "groq": "your-groq-api-key",
        # Add other API keys if you have them
        # "perplexity": "your-perplexity-api-key",
        # "openrouter": "your-openrouter-api-key"
    })
    
    # Generate text using the best available model
    result = await router.generate(
        prompt="Explain quantum computing in simple terms"
    )
    
    print(f"Result from {result['provider']} using {result['model']}:")
    print(result['text'])

if __name__ == "__main__":
    asyncio.run(main())
```

## API Keys

You'll need to sign up for API keys from at least one of these providers:

- Groq
- Perplexity
- OpenRouter

The library will only use the providers for which you supply API keys. You don't need to have keys for all providers - just add the ones you have access to.

## Configuration

You can customize the provider configurations in config/providers.yaml:

```yaml
providers:
  groq:
    models:
      llama3-8b-8192: 6
      llama3-70b-8192: 8
      # ...
  
  perplexity:
    models:
      sonar-small-online: 6
      sonar-medium-online: 7
      # ...
      
  openrouter:
    models:
      anthropic/claude-3-haiku: 7
      anthropic/claude-3-sonnet: 8
      # ...
```

The numbers represent quality scores (higher is better).

## License

MIT
