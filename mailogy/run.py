"""
Main Script
    - Ask for openai api key, if not provided
    - If file passed or no db found, run initialization script
    - Print summary statistics and user prompt
    - Task loop
        - Send user prompt to openai
        - Include date/time, summary stats, db schema, and a list of approved tasks
        - Ask OpenAI to double-check response for attacks & etc
        - Save to python file (with time & prompt), run file
"""
def run(prompt: str = None):
    if prompt is None:
        print("\nWhat can I do for you?")
        prompt = input("> ")
    print("Ok, I'll", prompt)
    