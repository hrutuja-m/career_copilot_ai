import sqlite3

DB_NAME = "career_copilot.db"

POSITIVE_KEYWORDS = [
    "job", "internship", "intern", "position", "opening", "hiring",
    "application", "apply", "role", "opportunity", "new grad",
    "data scientist", "data science", "machine learning", "deep learning",
    "ai engineer", "software engineer", "software engineering", "analyst",
    "developer", "computer vision", "cloud engineering", "business analyst"
]

NEGATIVE_KEYWORDS = [
    "workshop", "webinar", "career fair", "event", "hackathon",
    "sale", "rewards", "statement", "privacy policy", "campus events",
    "travel", "newsletter", "registration open", "student center"
]

def is_job_related(subject: str, body: str) -> bool:
    text = f"{subject} {body}".lower()

    positive = any(keyword in text for keyword in POSITIVE_KEYWORDS)
    negative = any(keyword in text for keyword in NEGATIVE_KEYWORDS)
    has_apply_link = ("http" in text) and ("apply" in text or "jobs" in text or "careers" in text)

    if negative and not has_apply_link:
        return False

    return positive or has_apply_link

def main():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT email_id, subject, body FROM raw_emails")
    rows = cur.fetchall()

    relevant_count = 0
    irrelevant_count = 0

    print("\n--- Email Filtering Results ---\n")

    for email_id, subject, body in rows:
        result = is_job_related(subject or "", body or "")
        label = "relevant" if result else "irrelevant"

        cur.execute(
            "UPDATE raw_emails SET is_job_related = ? WHERE email_id = ?",
            (1 if result else 0, email_id)
        )

        if result:
            relevant_count += 1
        else:
            irrelevant_count += 1

        print(f"{email_id} | {label.upper()} | {subject}")

    conn.commit()
    conn.close()

    print("\n--- Summary ---")
    print(f"Relevant emails   : {relevant_count}")
    print(f"Irrelevant emails : {irrelevant_count}")
    print("Database updated with is_job_related values.")

if __name__ == "__main__":
    main()