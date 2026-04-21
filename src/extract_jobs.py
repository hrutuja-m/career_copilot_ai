import re
import sqlite3

DB_NAME = "career_copilot.db"

KNOWN_COMPANIES = [
    "Amazon", "Google", "Deloitte", "Microsoft", "Tesla", "Netflix",
    "Meta", "Spotify", "Apple", "Nvidia", "Uber", "StartupX AI",
    "Salesforce", "Accenture", "Adobe", "Oracle", "Airbnb", "Snap",
    "Startup.io"
]

AGGREGATOR_COMPANIES = {"Linkedin", "Indeed", "Glassdoor", "University"}

ROLE_PATTERNS = [
    (r"data scientist intern", "Data Scientist Intern"),
    (r"data science intern", "Data Science Intern"),
    (r"software engineering intern|software engineer intern", "Software Engineering Intern"),
    (r"ai engineer intern", "AI Engineer Intern"),
    (r"ai and machine learning intern|machine learning engineer intern", "Machine Learning Engineer Intern"),
    (r"machine learning internship|machine learning intern", "Machine Learning Internship"),
    (r"deep learning internship|deep learning intern", "Deep Learning Internship"),
    (r"junior machine learning engineer", "Junior Machine Learning Engineer"),
    (r"data analyst", "Data Analyst"),
    (r"business analyst", "Business Analyst"),
    (r"computer vision internship|computer vision intern", "Computer Vision Internship"),
    (r"cloud engineering internship|cloud engineering intern", "Cloud Engineering Internship"),
    (r"software engineer new graduate|software engineer new grad", "Software Engineer New Graduate"),
    (r"data science new grad|data science new graduate", "Data Science New Graduate"),
    (r"data scientist full[- ]time|data scientist", "Data Scientist"),
    (r"backend developer", "Backend Developer"),
]

def extract_apply_link(text: str):
    match = re.search(r"https?://\S+", text)
    return match.group(0).rstrip(".,)") if match else None

def extract_deadline(text: str):
    match = re.search(r"Deadline[: ]+([A-Za-z]+ \d{1,2}, \d{4})", text, re.IGNORECASE)
    return match.group(1) if match else None

def extract_company(sender: str, subject: str, body: str):
    text = f"{subject} {body}"

    for company in KNOWN_COMPANIES:
        if company.lower() in text.lower():
            return company

    patterns = [
        r"at ([A-Z][A-Za-z0-9&\.\- ]+)",
        r"([A-Z][A-Za-z0-9&\.\- ]+) is hiring",
        r"([A-Z][A-Za-z0-9&\.\- ]+) has a .* position",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip()
            for company in KNOWN_COMPANIES:
                if company.lower() in candidate.lower():
                    return company
            return candidate

    domain = sender.split("@")[-1].split(".")[0].replace("-", " ").title()
    return domain

def extract_role(subject: str, body: str):
    text = f"{subject} {body}".lower()

    for pattern, normalized_role in ROLE_PATTERNS:
        if re.search(pattern, text):
            return normalized_role

    return "Unknown Role"

def extract_location(subject: str, body: str):
    text = f"{subject} {body}"

    if "remote" in text.lower():
        return "Remote"

    patterns = [
        r"available in ([A-Z][A-Za-z ]+?) at",
        r"in ([A-Z][A-Za-z ]+?)(?:\.|,| Apply| Deadline| mode|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None

def extract_job_type(subject: str, body: str):
    text = f"{subject} {body}".lower()

    if "internship" in text or "intern" in text:
        return "Internship"
    if "new grad" in text or "new graduate" in text:
        return "New Graduate"
    if "full-time" in text or "full time" in text:
        return "Full-Time"
    return "Unknown"

def main():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM job_opportunities")

    cur.execute("""
        SELECT email_id, sender, subject, body, received_date
        FROM raw_emails
        WHERE is_job_related = 1
    """)
    rows = cur.fetchall()

    inserted = 0

    for email_id, sender, subject, body, received_date in rows:
        company = extract_company(sender or "", subject or "", body or "")
        role = extract_role(subject or "", body or "")
        location = extract_location(subject or "", body or "")
        deadline = extract_deadline(body or "")
        apply_link = extract_apply_link(body or "")
        job_type = extract_job_type(subject or "", body or "")

        cur.execute("""
            INSERT INTO job_opportunities (
                email_id, company, role, location, deadline,
                apply_link, job_type, priority_score, priority_label,
                source_subject, received_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_id,
            company,
            role,
            location,
            deadline,
            apply_link,
            job_type,
            None,
            None,
            subject,
            received_date
        ))

        inserted += 1

    conn.commit()
    conn.close()

    print(f"{inserted} job opportunities extracted successfully.")

if __name__ == "__main__":
    main()