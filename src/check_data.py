import sqlite3

conn = sqlite3.connect("career_copilot.db")
cur = conn.cursor()

cur.execute("SELECT email_id, subject, label FROM raw_emails")
rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()