import ast
import json
import os
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
from litellm import completion, completion_cost

from mailogy.utils import (
    mailogy_dir, 
    get_user_email, 
    get_llm_base_url, 
    get_llm_api_key, 
    get_llm_model,
    set_base_url,
    set_llm_api_key,
    set_llm_model
)
from mailogy.prompts import script_prompt, script_examples, script_tips

class LLMClient:
    def __init__(self, log_path, model="gpt-4"):
        self.log_path = log_path
        self.model = get_llm_model() or model
        self.conversation = []
        self.base_url = get_llm_base_url() or None
        self.api_key = get_llm_api_key() or None
        self._setup_client()
        
    def _setup_client(self):
        env_path = mailogy_dir / ".env"
        load_dotenv(env_path)
        self.base_url = get_llm_base_url() or 'https://api.openai.com/v1'
        set_base_url(self.base_url)
        self.model = get_llm_model() or 'gpt-4'
        set_llm_model(self.model)
        self.api_key = get_llm_api_key() or os.getenv("OPENAI_API_KEY")
        while self.api_key is None:
            print(f"API Key {self.api_key} not found. ")
            self.api_key = input("Enter API Key (e.g. OpenAI): ").strip()
            set_llm_api_key(self.api_key)

    def get_response(
        self, model: str = None, 
        messages: list[dict[str, str]] = None, 
        temperature: float = 1.,
        agent_name: str = "",
    ) -> str:
        log = {
            "model": model or self.model,
            "prompt": messages[-1]["content"],
            "temperature": temperature,
            "agent_name": agent_name,
            "cost": None,
        }

        try:
            selected_model = model or self.model
            base_url = self.base_url or "https://api.openai.com/v1"
            response = completion(
                base_url=base_url,
                api_key=self.api_key,
                model=selected_model,
                messages=messages,
                temperature=temperature,
            )
            text = (response.choices[0].message.content) or ""
            log["response"] = text
            cost = completion_cost(completion_response=response) or 0
            print(f"Cost for completion call: {selected_model}", f"${float(cost):.10f}")
            log["cost"] = f"{float(cost):.10f}"
            return text
        except Exception as e:
            log["error"] = str(e)
            print(f"Error:\n", str(log))
            raise e
        finally:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log) + "\n")
        
    script_messages = []
    def get_script(self, prompt: str):
        # Load the text of the file 'database.py" in the same dir as this file
        if not self.script_messages:
            db_api = (Path(__file__).parent / "database.py").read_text()
            self.script_messages = [
                {"role": "system", "content": script_prompt + f"\nThe customer's email address is {get_user_email()}"},
                {"role": "system", "content": script_examples},
                {"role": "system", "content": f"DATABASE API:\n{db_api}"},
                {"role": "system", "content": script_tips},
            ]                
        self.script_messages.append({"role": "user", "content": f"PROMPT:\n{prompt}"})
        response = self.get_response(
            model=self.model,
            messages=self.script_messages.copy(),
            temperature=1,
            agent_name="get_script",
        )
        # Check if there are two instances of  "@@"
        message = ""  # Anything before @@, or the invalid script
        script = ""  # An apparently valid script
        content = ""  # What gets added to conversation; include useful info on errors
        message, script, content = "", "", ""
        if response.count("@@") == 2:
            message, script = response.split("@@")[:2]
        elif response.count("```") == 2:
            message, script = response.split("```")[:2]
        else:
            message, script = response, ""
        content = message
        if script:
            script = dedent(script).strip()
            if script.startswith("python"):
                script = script[6:].strip()
            try:
                script = json.loads(script)
            except Exception as e:
                pass
            try:
                ast.parse(script)
                content += f"\n@@\n{script}\n@@"
            except SyntaxError as e:
                message, script = response, ""
                content += f"\nINVALID SCRIPT: \n@@\n{script}\n@@\n\nERROR MESSAGE: {e}"
        self.script_messages.append({"role": "assistant", "content": content})
        return message, script
        
_llm_client_instance = None
_client_log_path = mailogy_dir / "logs.jsonl"
def get_llm_client():
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient(_client_log_path)
    return _llm_client_instance
