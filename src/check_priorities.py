import sqlite3

conn = sqlite3.connect("career_copilot.db")
cur = conn.cursor()

cur.execute("""
    SELECT company, role, deadline, job_type, priority_score, priority_label
    FROM job_opportunities
    ORDER BY priority_score DESC
""")

rows = cur.fetchall()

for row in rows:
    print(row)

conn.close()