import yaml
import os
from pathlib import Path

def get_config_path():
    """Get the path to the config directory"""
    # Try to find config in various locations
    possible_locations = [
        Path.cwd() / "config",  # Current working directory
        Path(__file__).parent.parent.parent / "config",  # Relative to this file
    ]
    
    for location in possible_locations:
        if location.exists():
            return location
    
    # If no config directory found, raise error
    raise FileNotFoundError("Config directory not found")

def load_provider_config():
    """Load provider configuration from YAML file"""
    config_path = get_config_path() / "providers.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Provider config file not found at {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config.get("providers", {})