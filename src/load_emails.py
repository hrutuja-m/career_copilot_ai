import sqlite3
import pandas as pd

DB_NAME = "career_copilot.db"
CSV_FILE = "data/sample_emails.csv"

def load_emails():
    df = pd.read_csv(CSV_FILE)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            INSERT OR REPLACE INTO raw_emails
            (email_id, sender, subject, received_date, body, label)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["email_id"],
            row["sender"],
            row["subject"],
            row["date"],
            row["body"],
            row["label"]
        ))

    conn.commit()
    conn.close()
    print(f"{len(df)} emails loaded successfully.")

if __name__ == "__main__":
    load_emails()