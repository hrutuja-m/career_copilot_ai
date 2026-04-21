import sqlite3

DB_NAME = "career_copilot.db"

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def update_schema():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if not column_exists(cur, "raw_emails", "is_job_related"):
        cur.execute("ALTER TABLE raw_emails ADD COLUMN is_job_related INTEGER")
        print("Added column: is_job_related")
    else:
        print("Column already exists: is_job_related")

    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()