import sqlite3

DB_NAME = "career_copilot.db"

def completeness_score(row):
    _, email_id, company, role, location, deadline, apply_link, job_type, source_subject, received_date = row

    score = 0
    for value in [company, role, location, deadline, apply_link, job_type]:
        if value:
            score += 1

    if role and role != "Unknown Role":
        score += 2

    if company and company not in {"Linkedin", "Indeed", "Glassdoor", "University"}:
        score += 1

    return score

def main():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT job_id, email_id, company, role, location, deadline,
               apply_link, job_type, source_subject, received_date
        FROM job_opportunities
        ORDER BY received_date ASC
    """)
    rows = cur.fetchall()

    best_records = {}
    duplicate_ids = []

    for row in rows:
        job_id, email_id, company, role, location, deadline, apply_link, job_type, source_subject, received_date = row

        if apply_link:
            key = apply_link
        else:
            key = f"{company}|{role}|{deadline}|{job_type}"

        if key not in best_records:
            best_records[key] = row
        else:
            current_best = best_records[key]
            if completeness_score(row) > completeness_score(current_best):
                duplicate_ids.append(current_best[0])
                best_records[key] = row
            else:
                duplicate_ids.append(job_id)

    for job_id in duplicate_ids:
        cur.execute("DELETE FROM job_opportunities WHERE job_id = ?", (job_id,))

    conn.commit()
    conn.close()

    print(f"Duplicate cleanup complete. Removed {len(duplicate_ids)} duplicate records.")

if __name__ == "__main__":
    main()