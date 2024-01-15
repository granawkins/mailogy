import ast
import json
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv, set_key
from openai import OpenAI
from litellm import completion, completion_cost

from mailogy.utils import mailogy_dir, get_user_email
from mailogy.prompts import script_prompt, script_examples, script_tips

class LLMClient:
    def __init__(self, log_path, model="gpt-4"):
        self.log_path = log_path
        self.model = model
        self.client = None
        self.conversation = []

        self._setup_client()
        
    def _setup_client(self):
        env_path = mailogy_dir / ".env"
        load_dotenv(env_path)
        all_models = []
        while self.client is None:
            try:
                self.client = OpenAI()
                all_models = {m.id for m in self.client.models.list().data}
            except Exception as e:
                print(f"Couldn't initialize OpenAI client: {e}")
                self.client = None
                api_key = input("Enter your OpenAI API key: ").strip()
                set_key(env_path, 'OPENAI_API_KEY', api_key)
                load_dotenv(env_path)
        while self.model not in all_models:
            print(f"Model {self.model} not available. Available models:")
            print(all_models)
            self.model = input("Enter a model name: ").strip()

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
            response = completion(
                model=selected_model,
                messages=messages,
                temperature=temperature,
            )
            cost = completion_cost(completion_response=response)
            print(f"Cost for completion call: {selected_model}", f"${float(cost):.10f}")
            text = (response.choices[0].message.content) or ""
            log["response"] = text
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
