import re
import mailbox
from dateutil.parser import parse
from pathlib import Path
from hashlib import md5
from bs4 import BeautifulSoup

from mailogy.database import get_db
from mailogy.llm_client import get_llm_client


def add_message(message, index, source):
    timestamp = message.get("Date")
    try:
        timestamp = parse(timestamp)
    except Exception as e:
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
        "timestamp": timestamp.isoformat(),
        "from_email": from_email,
        "from_name": from_name,
        "to_email": to_email,
        "to_name": to_name,
        "subject": subject,
        "content": "",
        "links": [],
        "attachments": [],
        "source": source,
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

    get_db().insert([result])


def initialize(mbox_path: Path | None = None, limit: int = 5):
    """
    1. Check for an opani key
    2. Check for a database or create one
    3. Get a database summary
    4. Compare to inputs
        - If db, get a set of indexes
        - If db and not inputs, return
        - If not db and not inputs, ask for mbox path
        - Get length of mbox
        - Display summary
        - Process new messages if any
    """
    # Make sure we have an openai key
    get_llm_client()
    summary = get_db().summary()

    # Get path to mbox
    if summary["message_count"] == 0 and mbox_path is None:
        while mbox_path is None:
            user_input = input("Enter path to mbox file: ")
            if Path(user_input).exists():
                mbox_path = Path(user_input)
            else:
                print("Invalid path, try again.")

    # See what we already have form that mbox
    last_index = 0
    if mbox_path and summary["message_count"] > 0:
        last_index = get_db().summary(mbox_path)["message_count"]
        print(f"Found {last_index} messages in the database.")

    # Load new messages into db
    added = 0
    if mbox_path is not None and limit > last_index:
        mbox = mailbox.mbox(mbox_path)
        n_new = limit - last_index
        print(f"Found {len(mbox)} messages in mbox file, adding {n_new} new (this could take a while)")
        for index, message in mbox.iteritems():
            if index < last_index:
                continue
            try:
                if index % 100 == 0:
                    print(f"{added}/{n_new}..")
                add_message(message, index, source=str(mbox_path))
                added += 1
                if index >= limit:
                    break
            except Exception as e:
                continue
            except KeyboardInterrupt:
                break
        print(f"Added {added} messages to database")
