# test_local.py
import asyncio
import os
from dotenv import load_dotenv
from src.router import LLMRouter

async def test():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys (only include the ones you have)
    api_keys = {}
    if os.getenv("GROQ_API_KEY"):
        api_keys["groq"] = os.getenv("GROQ_API_KEY")
    if os.getenv("PERPLEXITY_API_KEY"):
        api_keys["perplexity"] = os.getenv("PERPLEXITY_API_KEY")
    if os.getenv("OPENROUTER_API_KEY"):
        api_keys["openrouter"] = os.getenv("OPENROUTER_API_KEY")
    
    if not api_keys:
        print("No API keys found in .env file. Please add at least one API key.")
        return
    
    # Create router with your API keys
    router = LLMRouter(api_keys)
    
    # Show available models
    available_models = router.list_available_models()
    print(f"Available models: {available_models}")
    
    # Test with a simple prompt
    print("\nTesting generation...")
    result = await router.generate(
        prompt="What's the capital of France?",
        options={"max_tokens": 100}  # Keep response short for testing
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        if "details" in result:
            print("Details:", result["details"])
    else:
        print(f"Success! Response from {result['provider']} using {result['model']}:")
        print("-" * 40)
        print(result['text'])
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test())