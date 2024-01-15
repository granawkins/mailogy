import re
import importlib
import subprocess
from pathlib import Path

# Create a .mailogy directory in the user's home directory
mailogy_dir = Path.home() / ".mailogy"
mailogy_dir.mkdir(exist_ok=True)

# Singleton for user email
# TODO: replace with config file
user_email = None
def set_user_email(name: str):
    global user_email
    user_email = name

def get_user_email():
    global user_email
    return user_email

def validate_imports(script: str):
    """Check that the script imports everything it needs

    Args:
        script (str): The script to validate
    
    1) Find import lines
    2) Try to import each one
    3) If it fails, use print/input to ask user's approval to install from pip
    """
    # Find import lines
    import_lines = re.findall(r"import\s+[\w\.]+", script)
    import_lines += re.findall(r"from\s+[\w\.]+\s+import\s+[\w\.]+", script)
    import_lines = [line.replace("from ", "").replace(" import ", ".") for line in import_lines]

    # Try to import each one
    for line in import_lines:
        if "get_db" in line:
            continue
        try:
            importlib.import_module(line)
        except ModuleNotFoundError:
            print(f"Could not import {line}.")
            if input(f"Script requires {line}. Install it now using pip? (y/n) ").lower() == "y":
                subprocess.run(["pip", "install", line])
            else:
                raise ModuleNotFoundError(f"Could not import {line}.")
