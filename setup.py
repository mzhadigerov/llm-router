# setup.py
from setuptools import setup, find_packages

setup(
    name="free-llm-router",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A library that routes requests to free LLM API providers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/free-llm-router",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)