from tqdm import tqdm
from textwrap import dedent
import mailbox
from pathlib import Path

from mailogy.database import get_db
from mailogy.llm_client import get_llm_client
from mailogy.parse_message import parse_message
from mailogy.utils import set_user_email


def initialize(mbox_path: Path | None = None, limit: int = 5):
    # Logo source: https://patorjk.com/software/taag
    print(dedent("""\
            __  ___      _ __                 
           /  |/  /___ _(_) /___  ____ ___  __
          / /|_/ / __ `/ / / __ \/ __ `/ / / /
         / /  / / /_/ / / / /_/ / /_/ / /_/ / 
        /_/  /_/\__,_/_/_/\____/\__, /\__, /  
        Mailogy                /____//____/"""))
    
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
    if summary["message_count"] > 0:
        last_index = get_db().summary(mbox_path)["message_count"]
        print(f"Found {last_index} saved messages.")

    # Load new messages into db
    if mbox_path is not None:

        # Determine how many records to add
        limit = None
        added = 0
        print(f"Loading your .mbox file (could take a minute or more)...")
        mbox = mailbox.mbox(mbox_path)
        mbox_size = len(mbox)
        print(f"There are {mbox_size} messages in the mbox file. ")
        print("How many would you like me to load? You can say 'all' or type a number.")
        while limit is None:
            user_input = input("\n>>> ").strip()
            if user_input == "all":
                limit = mbox_size
            else:
                try:
                    limit = int(user_input)
                    assert limit >= 0
                except ValueError:
                    print("\nMust be an integer. try again.")
        limit = min(limit, mbox_size)

        # Load records
        if limit > 0:
            records = []
            # Skip already processed messages
            for _ in range(last_index):
                next(mbox.iteritems())
            for index, message in tqdm(mbox.iteritems(), total=limit, desc="Loading messages"):
                try:
                    record = parse_message(message, index, source=str(mbox_path))
                    records.append(record)
                    added += 1
                    if len(records) > 10:
                        get_db().insert(records)
                        records = []
                    if added == limit:
                        break
                except Exception as e:
                    continue
                except KeyboardInterrupt:
                    break
            if records:
                get_db().insert(records)
            print(f"Added {added} messages to database. Total messages: {get_db().summary()['message_count']}")

    # Get the most common email address
    if summary["email_counts"]:
        most_common_email = summary["email_counts"].most_common(1)[0][0]
        set_user_email(most_common_email)
