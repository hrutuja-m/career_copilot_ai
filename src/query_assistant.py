import sqlite3
from datetime import datetime

DB_NAME = "career_copilot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def fetch_rows(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def summarize_jobs():
    total_jobs = fetch_rows("SELECT COUNT(*) FROM job_opportunities")[0][0]
    high_priority = fetch_rows(
        "SELECT COUNT(*) FROM job_opportunities WHERE priority_label = 'High'"
    )[0][0]
    medium_priority = fetch_rows(
        "SELECT COUNT(*) FROM job_opportunities WHERE priority_label = 'Medium'"
    )[0][0]
    low_priority = fetch_rows(
        "SELECT COUNT(*) FROM job_opportunities WHERE priority_label = 'Low'"
    )[0][0]
    internships = fetch_rows(
        "SELECT COUNT(*) FROM job_opportunities WHERE LOWER(job_type) LIKE '%internship%'"
    )[0][0]
    remote_jobs = fetch_rows(
        "SELECT COUNT(*) FROM job_opportunities WHERE LOWER(location) LIKE '%remote%'"
    )[0][0]

    print("\n--- Job Summary ---\n")
    print(f"Total extracted jobs : {total_jobs}")
    print(f"High priority jobs   : {high_priority}")
    print(f"Medium priority jobs : {medium_priority}")
    print(f"Low priority jobs    : {low_priority}")
    print(f"Internships          : {internships}")
    print(f"Remote jobs          : {remote_jobs}")


def show_high_priority_jobs():
    rows = fetch_rows("""
        SELECT company, role, location, deadline, priority_score
        FROM job_opportunities
        WHERE priority_label = 'High'
        ORDER BY priority_score DESC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
    """)

    if not rows:
        print("\nNo high priority jobs found.\n")
        return

    print("\n--- High Priority Jobs ---\n")
    for company, role, location, deadline, score in rows:
        print(f"{company} | {role} | {location} | Deadline: {deadline} | Score: {score}")


def show_top_jobs(limit=5):
    rows = fetch_rows("""
        SELECT company, role, location, deadline, priority_score, priority_label
        FROM job_opportunities
        ORDER BY priority_score DESC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
        LIMIT ?
    """, (limit,))

    if not rows:
        print("\nNo jobs found.\n")
        return

    print(f"\n--- Top {limit} Jobs To Apply First ---\n")
    for company, role, location, deadline, score, label in rows:
        print(f"{company} | {role} | {location} | Deadline: {deadline} | Score: {score} | {label}")


def show_internships():
    rows = fetch_rows("""
        SELECT company, role, location, deadline, priority_score, priority_label
        FROM job_opportunities
        WHERE LOWER(job_type) LIKE '%internship%'
        ORDER BY priority_score DESC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
    """)

    if not rows:
        print("\nNo internships found.\n")
        return

    print("\n--- Internship Opportunities ---\n")
    for company, role, location, deadline, score, label in rows:
        print(f"{company} | {role} | {location} | Deadline: {deadline} | Score: {score} | {label}")


def show_remote_jobs():
    rows = fetch_rows("""
        SELECT company, role, location, deadline, priority_score, priority_label
        FROM job_opportunities
        WHERE LOWER(location) LIKE '%remote%'
        ORDER BY priority_score DESC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
    """)

    if not rows:
        print("\nNo remote jobs found.\n")
        return

    print("\n--- Remote Jobs ---\n")
    for company, role, location, deadline, score, label in rows:
        print(f"{company} | {role} | {location} | Deadline: {deadline} | Score: {score} | {label}")


def show_machine_learning_roles():
    rows = fetch_rows("""
        SELECT company, role, location, deadline, priority_score, priority_label
        FROM job_opportunities
        WHERE LOWER(role) LIKE '%machine learning%'
           OR LOWER(role) LIKE '%deep learning%'
           OR LOWER(role) LIKE '%computer vision%'
           OR LOWER(role) LIKE '%artificial intelligence%'
           OR LOWER(role) LIKE '%ai%'
        ORDER BY priority_score DESC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
    """)

    if not rows:
        print("\nNo machine learning or artificial intelligence roles found.\n")
        return

    print("\n--- Machine Learning and Artificial Intelligence Roles ---\n")
    for company, role, location, deadline, score, label in rows:
        print(f"{company} | {role} | {location} | Deadline: {deadline} | Score: {score} | {label}")


def show_deadlines_coming_soon():
    rows = fetch_rows("""
        SELECT company, role, deadline, priority_score, priority_label
        FROM job_opportunities
        WHERE deadline IS NOT NULL
    """)

    if not rows:
        print("\nNo upcoming deadlines found.\n")
        return

    today = datetime(2026, 3, 31)

    valid_rows = []
    for row in rows:
        company, role, deadline, score, label = row
        parsed_deadline = datetime.strptime(deadline, "%B %d, %Y")

        if parsed_deadline >= today:
            valid_rows.append((company, role, deadline, score, label, parsed_deadline))

    if not valid_rows:
        print("\nNo upcoming deadlines found.\n")
        return

    valid_rows.sort(key=lambda x: x[5])

    print("\n--- Upcoming Deadlines ---\n")
    for company, role, deadline, score, label, _ in valid_rows[:10]:
        print(f"{company} | {role} | Deadline: {deadline} | Score: {score} | {label}")

def explain_top_job():
    rows = fetch_rows("""
        SELECT company, role, location, deadline, job_type, priority_score, priority_label
        FROM job_opportunities
        ORDER BY priority_score DESC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
        LIMIT 1
    """)

    if not rows:
        print("\nNo jobs available to explain.\n")
        return

    company, role, location, deadline, job_type, score, label = rows[0]

    reasons = []

    role_lower = (role or "").lower()
    if any(term in role_lower for term in [
        "data science",
        "data scientist",
        "machine learning",
        "artificial intelligence",
        "ai",
        "deep learning",
        "computer vision"
    ]):
        reasons.append("it matches your target technical area")

    if deadline:
        reasons.append(f"the deadline is clearly defined as {deadline}")

    if job_type and job_type != "Unknown":
        reasons.append(f"it is a {job_type.lower()} opportunity")

    if location and "remote" in location.lower():
        reasons.append("it offers remote flexibility")

    print("\n--- Why This Job Is Ranked Highly ---\n")
    print(f"Top job: {company} | {role}")
    print(f"Priority score: {score} | Priority label: {label}")

    if reasons:
        print("Reasoning:")
        for reason in reasons:
            print(f"- {reason}")
    else:
        print("Reasoning: it has the strongest combined score in the current ranking.")


def show_low_priority_jobs():
    rows = fetch_rows("""
        SELECT company, role, location, deadline, priority_score
        FROM job_opportunities
        WHERE priority_label = 'Low'
        ORDER BY priority_score ASC,
                 CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC
    """)

    if not rows:
        print("\nNo low priority jobs found.\n")
        return

    print("\n--- Lower Priority Jobs ---\n")
    for company, role, location, deadline, score in rows:
        print(f"{company} | {role} | {location} | Deadline: {deadline} | Score: {score}")


def normalize_query(user_query):
    return " ".join(user_query.lower().strip().split())


def handle_query(user_query):
    query = normalize_query(user_query)

    if "summary" in query or "summarize" in query:
        summarize_jobs()

    elif "high priority" in query:
        show_high_priority_jobs()

    elif (
        ("apply" in query and "first" in query)
        or "top jobs" in query
        or "best jobs" in query
        or "top opportunities" in query
        or "best opportunities" in query
    ):
        show_top_jobs()

    elif "internship" in query or "internships" in query:
        show_internships()

    elif "remote" in query:
        show_remote_jobs()

    elif (
        "machine learning" in query
        or "artificial intelligence" in query
        or "computer vision" in query
        or "deep learning" in query
        or ("ai" in query and "role" in query)
    ):
        show_machine_learning_roles()

    elif "deadline" in query or "coming soon" in query or "urgent" in query:
        show_deadlines_coming_soon()

    elif "why" in query or "explain" in query:
        explain_top_job()

    elif "low priority" in query or "ignore" in query:
        show_low_priority_jobs()

    elif query in {"exit", "quit"}:
        print("\nExiting assistant. Bye!\n")
        return False

    else:
        print("\nSorry, I can answer these for now:")
        print("- summarize jobs")
        print("- show high priority jobs")
        print("- what should I apply to first")
        print("- show internships")
        print("- show remote jobs")
        print("- show machine learning roles")
        print("- show upcoming deadlines")
        print("- explain top job")
        print("- show low priority jobs")
        print("- exit\n")

    return True


def main():
    print("\nCareerPilot AI Assistant")
    print("Ask a question about your jobs.")
    print("Type 'exit' to quit.\n")

    running = True
    while running:
        user_query = input("You: ")
        running = handle_query(user_query)


if __name__ == "__main__":
    main()