import sqlite3

conn = sqlite3.connect("career_copilot.db")
cur = conn.cursor()

cur.execute("""
    SELECT email_id, company, role, location, deadline, job_type
    FROM job_opportunities
""")
rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()