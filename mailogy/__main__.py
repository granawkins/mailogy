import argparse
import ast
from pathlib import Path

from mailogy.initialize import initialize
from mailogy.llm_client import get_llm_client


parser = argparse.ArgumentParser(description='A smart assistant for processing mbox files.')
parser.add_argument('mbox_file_path', nargs='?', default=None, help='Path to the mbox file (optional)')
parser.add_argument('--limit', '-l', type=int, default=5, help='Limit the number of emails to process')
args = parser.parse_args()
mbox_file_path = args.mbox_file_path
limit = args.limit


# Main conversation loop
def run(prompt: str = None):
    if prompt is None:
        print("\nWhat can I do for you? (say 'q' to quit)")
        prompt = input("> ").strip()
    if prompt.lower() == "q":
        raise KeyboardInterrupt()
    script = get_llm_client().get_script(prompt)
    try:
        ast.parse(script)
        exec(script, globals())
    except SyntaxError:
        print(f"Invalid response: {script}")
    except Exception as e:
        print(f"An error occurred while running the program: {e}")


# Control flow
initialize(mbox_file_path, limit=limit)
while True:
    try:
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        break
