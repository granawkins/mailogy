import yaml
from pathlib import Path

# Create a .mailogy directory in the user's home directory
mailogy_dir = Path.home() / ".mailogy"
mailogy_dir.mkdir(exist_ok=True)

# Path to the config file
config_path = mailogy_dir / "config.yaml"

def load_config():
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {}

def save_config(config):
    with open(config_path, 'w') as f:
        yaml.safe_dump(config, f)

def set_user_email(name: str):
    config = load_config()
    config['user_email'] = name
    save_config(config)

def get_user_email():
    config = load_config()
    return config.get('user_email')

def get_llm_base_url():
    config = load_config()
    return config.get('llm_base_url')

def get_llm_model():
    config = load_config()
    return config.get('llm_model')

def get_llm_api_key():
    config = load_config()
    return config.get('llm_api_key')

def set_llm_model(model_name: str):
    config = load_config()
    config['llm_model'] = model_name
    save_config(config)

def set_llm_api_key(api_key: str):
    config = load_config()
    config['llm_api_key'] = api_key
    save_config(config)

def set_base_url(base_url: str):
    config = load_config()
    config['llm_base_url'] = base_url
    save_config(config)