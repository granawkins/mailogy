import argparse
from mailogy.initialize import initialize
from mailogy.llm_client import get_llm_client
from mailogy.run import run

# Parse arguments
parser = argparse.ArgumentParser(description='A smart assistant for processing mbox files.')
parser.add_argument('mbox_file_path', nargs='?', default=None, help='Path to the mbox file (optional)')
parser.add_argument('--limit', '-l', type=int, default=5, help='Limit the number of emails to process')
args = parser.parse_args()
mbox_file_path = args.mbox_file_path
limit = args.limit


# Run program
initialize(mbox_file_path, limit=limit)  # Will prompt for mbox file path if not found

def run(prompt: str = None):
    if prompt is None:
        print("\nWhat can I do for you?")
        prompt = input("> ").strip()
    response = get_llm_client().get_response(prompt)
    print(response)
    
while True:
    try:
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        break
