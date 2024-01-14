import argparse
from mailogy.initialize import initialize
from mailogy.run import run

# Parse arguments
parser = argparse.ArgumentParser(description='A smart assistant for processing mbox files.')
parser.add_argument('mbox_file_path', help='Path to the mbox file')
parser.add_argument('--limit', '-l', type=int, default=5, help='Limit the number of emails to process')
args = parser.parse_args()
mbox_file_path = args.mbox_file_path
limit = args.limit

# Run program
initialize(mbox_file_path, limit=limit)
while True:
    try:
        run()
    except KeyboardInterrupt:
        print("Exiting...")
        break
