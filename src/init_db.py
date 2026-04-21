import sqlite3

DB_NAME = "career_copilot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_emails (
        email_id TEXT PRIMARY KEY,
        sender TEXT,
        subject TEXT,
        received_date TEXT,
        body TEXT,
        label TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_opportunities (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT,
        company TEXT,
        role TEXT,
        location TEXT,
        deadline TEXT,
        apply_link TEXT,
        job_type TEXT,
        priority_score REAL,
        priority_label TEXT,
        source_subject TEXT,
        received_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (email_id) REFERENCES raw_emails(email_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database created successfully.")

if __name__ == "__main__":
    init_db()