import re
import mailbox
import dateutil
from pathlib import Path
from hashlib import md5
from bs4 import BeautifulSoup

from mailogy.database import get_db

def initialize(mbox_path: Path | None = None, limit: int = 5):
    # Get path to mbox
    while mbox_path is None:
        user_input = input("Enter path to mbox file: ")
        if Path(user_input).exists():
            mbox_path = Path(user_input)
        else:
            print("Invalid path, try again.")

    # Load messages into db
    db = get_db()
    mbox = mailbox.mbox(mbox_path)
    for i, (index, message) in enumerate(mbox.iteritems()):
        try:
            timestamp = message.get("Date")
            try:
                timestamp = dateutil.parser.parse(timestamp)
            except ValueError:
                pass
            def parse_email_and_name(raw: str) -> tuple[str, str]:
                if "<" not in raw:
                    return raw, ""
                name, email = raw.split("<")
                email = email.replace(">", "")
                return email, name
            from_email, from_name = parse_email_and_name(message.get("From", "N/A"))
            to_email, to_name = parse_email_and_name(message.get("To", "N/A"))
            def hash(string: str) -> str:
                return md5(string.encode("utf-8")).hexdigest()
            id = hash(message.get("Message-ID", f"{timestamp}{from_email}{to_email}"))
            subject = message.get("Subject", "N/A")            
            result = {
                "id": id,
                "timestamp": timestamp,
                "from_email": from_email,
                "from_name": from_name,
                "to_email": to_email,
                "to_name": to_name,
                "subject": subject,
                "content": "",
                "links": [],
                "attachments": [],
                "source": str(mbox_path),
                "message_index": index,
            }

            # Split body into text (no HTML), a list of links, and a list of attachments
            def parse_part(part):
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition", None)

                # Add all text intended for humans to content. This includes text/plain and text/html, but exclude html tags
                if content_type in ["text/plain", "text/html"]:
                    soup = BeautifulSoup(part.get_payload(decode=True), features="html.parser")
                    result["content"] += soup.get_text()
                    # Go over it with regex and extract links
                    for link in soup.find_all("a"):
                        result["links"].append(link.get("href"))
                        
                # Add attachments
                elif content_disposition is not None and content_disposition.startswith("attachment"):
                    filename = part.get_filename()
                    if filename is not None:
                        result["attachments"].append(filename)

            if message.is_multipart():
                for part in message.walk():
                    parse_part(part)
            else:
                parse_part(message)

            # Clean up
            result["content"] = re.sub(r"\s+", " ", result["content"]).strip()  # Remove extra whitespace
            result["links"] = list(set(link.split("?")[0] for link in result["links"]))  # Remove query params from links
            result["links"] = ",".join(result["links"])  # TODO: Separate table
            result["attachments"] = ",".join(result["attachments"])  # TODO: Separate table

            db.insert([result])
            if i + 1 == limit:
                break

        except Exception as e:
            continue
        
    # Print a summary
    summary = db.summary()
    print(f"Loaded {summary['message_count']} messages from {summary['email_counts'].keys()}")
    print(f"Top 5 addresses: {summary['top_5']}")
