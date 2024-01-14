import os
from dotenv import load_dotenv, set_key

import openai
from openai import AuthenticationError, OpenAI

from mailogy.utils import mailogy_dir

class LLMClient:
    def __init__(self, client_path):
        self.client_path = client_path
        self.client = None
        self._setup_client()
        
    def _setup_client(self):
        env_path = mailogy_dir / ".env"
        load_dotenv(env_path)
        while self.client is None:
            try:
                self.client = OpenAI()
                self.client.models.list()
            except Exception as e:
                print(f"Couldn't initialize OpenAI client: {e}")
                self.client = None
                api_key = input("Enter your OpenAI API key: ").strip()
                set_key(env_path, 'OPENAI_API_KEY', api_key)
        
    def get_response(prompt: str, model: str = "gpt-4"):
        return f"Okay, I'll {prompt}."
        
_llm_client_instance = None
_client_path = mailogy_dir / "llm_client.json"
def get_llm_client():
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient(_client_path)
    return _llm_client_instance
