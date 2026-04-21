import sqlite3
from datetime import datetime

DB_NAME = "career_copilot.db"

PREFERRED_ROLES = [
    "data scientist",
    "data science",
    "machine learning",
    "ai engineer",
    "data analyst",
    "deep learning",
    "computer vision"
]

PREFERRED_JOB_TYPES = [
    "internship",
    "new graduate",
    "full-time"
]

REMOTE_PREFERRED = True

def score_deadline(deadline_text):
    if not deadline_text:
        return 10

    try:
        deadline_date = datetime.strptime(deadline_text, "%B %d, %Y")
        today = datetime(2026, 3, 31)
        days_left = (deadline_date - today).days

        if days_left < 0:
            return -30
        elif days_left <= 7:
            return 35
        elif days_left <= 14:
            return 28
        elif days_left <= 30:
            return 20
        else:
            return 10
    except Exception:
        return 10

def score_role(role):
    role_lower = (role or "").lower()

    for keyword in PREFERRED_ROLES:
        if keyword in role_lower:
            return 30

    if role_lower != "unknown role":
        return 18

    return 8

def score_job_type(job_type):
    job_type_lower = (job_type or "").lower()

    if "internship" in job_type_lower:
        return 20
    if "new graduate" in job_type_lower:
        return 18
    if "full-time" in job_type_lower:
        return 16
    return 8

def score_location(location):
    location_lower = (location or "").lower()

    if REMOTE_PREFERRED and "remote" in location_lower:
        return 15
    if location:
        return 10
    return 5

def score_completeness(role, deadline, location):
    score = 0

    if role and role != "Unknown Role":
        score += 5
    if deadline:
        score += 3
    if location:
        score += 2

    return score

def cap_score(score):
    return min(score, 100)

def assign_priority_label(score, deadline):
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, "%B %d, %Y")
            today = datetime(2026, 3, 31)
            if deadline_date < today:
                return "Expired"
        except Exception:
            pass

    if score >= 80:
        return "High"
    elif score >= 55:
        return "Medium"
    return "Low"

def main():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT job_id, company, role, location, deadline, job_type
        FROM job_opportunities
    """)
    rows = cur.fetchall()

    print("\n--- Job Priority Results ---\n")

    for job_id, company, role, location, deadline, job_type in rows:
        total_score = 0
        total_score += score_deadline(deadline)
        total_score += score_role(role)
        total_score += score_job_type(job_type)
        total_score += score_location(location)
        total_score += score_completeness(role, deadline, location)

        total_score = cap_score(total_score)
        priority_label = assign_priority_label(total_score, deadline)

        cur.execute("""
            UPDATE job_opportunities
            SET priority_score = ?, priority_label = ?
            WHERE job_id = ?
        """, (total_score, priority_label, job_id))

        print(f"{company} | {role} | Score: {total_score} | Priority: {priority_label}")

    conn.commit()
    conn.close()

    print("\nPriority scoring complete.")

if __name__ == "__main__":
    main()