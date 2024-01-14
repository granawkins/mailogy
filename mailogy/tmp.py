from mailogy.database import get_db
db = get_db()
target = "granthawkins88@gmail.com"
with db.conn:
    top_recipients = db.conn.execute(
        "SELECT to_email, COUNT(*) as count FROM messages WHERE from_email = ? GROUP BY to_email ORDER BY count DESC LIMIT 10;", (target,)
    ).fetchall()
print(f"The top 10 people {target} has sent emails to recently are:")
for recipient, count in top_recipients:
    print(f"{recipient}: {count} emails")