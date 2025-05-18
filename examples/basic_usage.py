# examples/basic_usage.py
import asyncio
import os
import logging
from dotenv import load_dotenv
from src.router import LLMRouter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys from environment variables
    api_keys = {
        "groq": os.getenv("GROQ_API_KEY"),
        "perplexity": os.getenv("PERPLEXITY_API_KEY"),
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
    }
    
    # Create router with API keys
    router = LLMRouter(api_keys)
    
    # List available models
    print("Available models:")
    for model in router.list_available_models():
        print(f"- {model}")
    
    # Generate text with specific model
    result = await router.generate(
        prompt="Explain quantum computing in simple terms",
        model_name="llama3-70b-8192",  # Groq's Llama 3 70B model
        options={
            "system_message": "You are a helpful assistant that explains complex topics in simple terms."
        }
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nResult from {result['provider']} using {result['model']}:")
        print(result['text'])
    
    # Generate text with best available model
    result = await router.generate(
        prompt="Write a short poem about artificial intelligence"
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nResult from {result['provider']} using {result['model']}:")
        print(result['text'])

if __name__ == "__main__":
    asyncio.run(main())