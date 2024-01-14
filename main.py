import argparse
from mbox_utils import process_mbox

def main():

    """
    1. Initialization Script
        - Ask for path to mbox, if not provided
        - Load 6 fields into a postgres db
        - Show a loading bar while mbox is being processed
    
    2. Main Script
        - Ask for openai api key, if not provided
        - If file passed or no db found, run initialization script
        - Print summary statistics and user prompt
        - Task loop
            - Send user prompt to openai
            - Include date/time, summary stats, db schema, and a list of approved tasks
            - Ask OpenAI to double-check response for attacks & etc
            - Save to python file (with time & prompt), run file

    """

    parser = argparse.ArgumentParser(description='Process mbox files.')
    parser.add_argument('mbox_file_path', help='Path to the mbox file')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Limit the number of emails to process')

    args = parser.parse_args()
    mbox_file_path = args.mbox_file_path
    limit = args.limit
    
    if not mbox_file_path:
        print("Please specify a path to the mbox file")
        return
    process_mbox(mbox_file_path, limit=limit)

if __name__ == "__main__":
    main()
