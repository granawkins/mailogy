from mailogy.database import get_db
db = get_db()
with db.conn:
    target = "granthawkins88@gmail.com"
    top_recipients = db.conn.execute(
        """
        SELECT to_email, COUNT(*) as email_count
        FROM messages
        WHERE from_email = ?
        GROUP BY to_email
        ORDER BY email_count DESC
        LIMIT 10;
        """, (target,)
    ).fetchall()

print(f"The top 10 people {target} has sent emails to recently are:")
for recipient, email_count in top_recipients:
    print(f"{recipient}: {email_count} emails")