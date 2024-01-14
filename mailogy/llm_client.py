import json
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv, set_key
from openai import OpenAI

from mailogy.utils import mailogy_dir

script_prompt = """
You are a customer service representative for a company called Mailogy. 
You are chatting with a customer who is asking you to do something for them.
The customer will ask you a question or make a request.
Using the API described below, you will return a PYTHON SCRIPT to fulfill the request.
Tasks might include:
- Asking how many messages I received from a particular person
- Generating a .csv files for all messages containing some keyword
- Returning a list of email addresses matching some criteria
- Asking a general question, such as the number of messages in the database.

Follow this procedure:
1. Read the API description carefully.
2. Read the customer's request carefully.
3. Write a python script to fulfill the request.
4. Double check that you've included the proper import statements and print statements
5. Return the script inside two @@ symbols.

Below you'll be shown the DATABASE_API, 

### DATABASE API
{database_api}

### EXAMPLES

PROMPT: Get the number of messages in the database
RESPONSE:
@@
from mailogy.database import get_db
message_count = get_db().summary()["message_count"]
print(f"There are {message_count} messages in the database.")
@@

PROMPT: How many messages have I sent to brett@bartlett.com?
RESPONSE:
@@
from mailogy.database import get_db
db = get_db()
with db.conn:
    target = brett@bartlett.com
    message_count = db.conn.execute(
        "SELECT COUNT(*) FROM messages WHERE from_email = ?;", (target,)
    ).fetchone()[0]
print(f"You've sent {message_count} messages to {target}.")
@@
"""

class LLMClient:
    def __init__(self, client_path, model="gpt-3.5-turbo-1106"):
        self.client_path = client_path
        self.model = model
        self.client = None
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
        while self.model not in all_models:
            print(f"Model {self.model} not available. Available models:")
            print(all_models)
            self.model = input("Enter a model name: ").strip()

    def get_response(
        self, model: str = None, 
        messages: list[dict[str, str]] = None, 
        temperature: float = 1.
    ) -> str:
        log = {
            "model": model or self.model,
            "prompt": messages[-1]["content"],
            "temperature": temperature,
        }
        # TODO: Calculate cost
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            log["error"] = str(e)
            raise e
        finally:
            with open(self.client_path / "logs.jsonl", "a") as f:
                f.write(json.dumps(log) + "\n")
        
    def get_script(self, prompt: str):
        # Load the text of the file 'database.py" in the same dir as this file
        db_api = (Path(__file__).parent / "database.py").read_text()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": dedent("""\
                        You are a customer service representative for a company called Mailogy. 
                        You are chatting with a customer who is asking you to do something for them.
                        The customer will ask you a question or make a request.
                        Using the API described below, you will return a PYTHON SCRIPT to fulfill the request.
                        Tasks might include:
                        - Asking how many messages I received from a particular person
                        - Generating a .csv files for all messages containing some keyword
                        - Returning a list of email addresses matching some criteria
                        - Asking a general question, such as the number of messages in the database.

                        Follow this procedure:
                        1. Read the DATABASE API and EXAMPLES below carefully.
                        2. Read the customer's PROMPT carefully.
                        3. Write a python script to fulfill the request.
                        4. Double check that you've included all your imports, and enough print statements to satify the customer.
                        5. Return the script inside two @@ symbols."""),
                },
                {
                    "role": "system",
                    "content": f"DATABASE API:\n{db_api}"
                },
                {
                    "role": "system",
                    "content": dedent("""\
                        EXAMPLES:
                                      
                        PROMPT: Get the number of messages in the database
                        RESPONSE:
                        @@
                        from mailogy.database import get_db
                        message_count = get_db().summary()["message_count"]
                        print(f"There are {message_count} messages in the database.")
                        @@

                        PROMPT: How many messages have I sent to brett@bartlett.com?
                        RESPONSE:
                        @@
                        from mailogy.database import get_db
                        db = get_db()
                        with db.conn:
                            target = brett@bartlett.com
                            message_count = db.conn.execute(
                                "SELECT COUNT(*) FROM messages WHERE from_email = ?;", (target,)
                            ).fetchone()[0]
                        print(f"You've sent {message_count} messages to {target}.")
                        @@"""),
                },
                {
                    "role": "user",
                    "content": f"PROMPT:\n{prompt}",
                },
            ],
            temperature=1,
        )
        text = response.choices[0].message.content
        script = text.split("@@")[1].strip()
        return script
        
_llm_client_instance = None
_client_path = mailogy_dir / "llm_client.json"
def get_llm_client():
    global _llm_client_instance
    if _llm_client_instance is None:
        _llm_client_instance = LLMClient(_client_path)
    return _llm_client_instance
