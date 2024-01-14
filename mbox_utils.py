from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
import time
import mailbox


def process_mbox(mbox_path, limit=5):
    mbox = mailbox.mbox(mbox_path)
    for i, message in enumerate(mbox):
        parsed = process_mbox_message(message)
        with open(f"parsed_mbox_{limit}.txt", "a") as f:
            f.write(str(parsed) + "\n")
        if i + 1 == limit:
            break


def process_mbox_message(message):
    result = {
        "ID": message.get("Message-ID", "N/A"),
        "Date": parsedate_to_datetime(message.get("Date")).isoformat() if message.get("Date") else "N/A",
        "From": message.get("From", "N/A"),
        "Subject": message.get("Subject", "N/A"),
        "Text Content": "",
        "Attachments": {}
    }

    def parse_part(part):
        content_type = part.get_content_type()
        content_disposition = part.get("Content-Disposition", None)

        if content_type.startswith('text/plain') and not content_disposition:
            # Add plain text content
            result["Text Content"] += part.get_payload(decode=True).decode('utf-8', errors='replace') + "\n"
        elif content_type.startswith('text/html') and not content_disposition:
            # Convert HTML to plain text
            html_content = part.get_payload(decode=True).decode('utf-8', errors='replace')
            soup = BeautifulSoup(html_content, 'html.parser')
            result["Text Content"] += soup.get_text() + "\n"
        elif content_disposition:
            # Handle attachments
            filename = part.get_filename()
            if filename:
                if content_type not in result["Attachments"]:
                    result["Attachments"][content_type] = []
                result["Attachments"][content_type].append(filename)

    if message.is_multipart():
        for part in message.walk():
            parse_part(part)
    else:
        parse_part(message)

    return result
