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