import argparse
import ast
from pathlib import Path

from mailogy.initialize import initialize
from mailogy.llm_client import get_llm_client
from mailogy.utils import validate_imports


parser = argparse.ArgumentParser(description='A smart assistant for processing email data.')
parser.add_argument('mbox_file_path', nargs='?', default=None, help='Path to the mbox file (optional)')
args = parser.parse_args()
mbox_file_path = args.mbox_file_path


# Main conversation loop
def run(prompt: str = None):
    if prompt is None:
        print("\nWhat can I do for you? (say 'q' to quit)")
        prompt = input(">>> ").strip()
    if prompt.lower() == "q":
        raise KeyboardInterrupt()
    message, script = get_llm_client().get_script(prompt)
    print(message)
    if script is not None:
        try:
            ast.parse(script)
            # validate_imports(script)
            exec(script, globals())
        except SyntaxError:
            print(f"Invalid response: {script}")
        except Exception as e:
            print(f"An error occurred while running the script: {e}\n\nFull script:\n\n{script}")


# Control flow
initialize(mbox_file_path)
while True:
    try:
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        break
