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
