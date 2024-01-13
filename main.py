import sys
import mailbox

def print_header_names(mbox_path):
    with mailbox.mbox(mbox_path) as mbox:
        for message in mbox:
            headers = message.keys()
            for header in headers:
                print(header)
            break  # Only print headers from the first message

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_mbox_file>")
        sys.exit(1)
    
    mbox_file_path = sys.argv[1]
    print_header_names(mbox_file_path)