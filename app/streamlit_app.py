import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="💼",
    layout="wide"
)

DB_PATH = Path(__file__).resolve().parents[1] / "career_copilot.db"
REFERENCE_TODAY = datetime(2026, 3, 31)


# -----------------------------
# Database helpers
# -----------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


def load_jobs():
    conn = get_connection()
    query = """
        SELECT
            company,
            role,
            location,
            deadline,
            job_type,
            priority_score,
            priority_label,
            apply_link,
            source_subject,
            received_date
        FROM job_opportunities
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def parse_deadline(value):
    if pd.isna(value) or value in [None, "", "None"]:
        return pd.NaT
    try:
        return pd.to_datetime(datetime.strptime(value, "%B %d, %Y"))
    except Exception:
        return pd.NaT


def prepare_jobs(df):
    if df.empty:
        return df

    df = df.copy()
    df["parsed_deadline"] = df["deadline"].apply(parse_deadline)
    df["is_expired"] = df["parsed_deadline"].apply(
        lambda x: pd.notna(x) and x < pd.Timestamp(REFERENCE_TODAY)
    )

    df["location"] = df["location"].fillna("Not specified")
    df["deadline"] = df["deadline"].fillna("Not specified")
    df["job_type"] = df["job_type"].fillna("Unknown")
    df["priority_label"] = df["priority_label"].fillna("Unknown")
    df["priority_score"] = df["priority_score"].fillna(0)

    return df


def sorted_active_jobs(df):
    active_df = df[~df["is_expired"]].copy()
    return active_df.sort_values(
        by=["priority_score", "parsed_deadline"],
        ascending=[False, True],
        na_position="last"
    )


# -----------------------------
# Assistant logic
# -----------------------------
def assistant_response(user_query, df):
    query = " ".join(user_query.lower().strip().split())
    active_df = sorted_active_jobs(df)

    if df.empty:
        return "No job data is available yet."

    if "summary" in query or "summarize" in query:
        total_jobs = len(df)
        active_jobs = len(active_df)
        high_jobs = len(active_df[active_df["priority_label"] == "High"])
        internships = len(active_df[active_df["job_type"].str.contains("Internship", case=False, na=False)])
        remote_jobs = len(active_df[active_df["location"].str.contains("Remote", case=False, na=False)])

        return (
            f"You currently have {total_jobs} extracted opportunities. "
            f"{active_jobs} are still active, {high_jobs} are high priority, "
            f"{internships} are internships, and {remote_jobs} are remote."
        )

    if ("apply" in query and "first" in query) or "top jobs" in query or "best jobs" in query:
        top_df = active_df.head(3)
        if top_df.empty:
            return "There are no active jobs to recommend right now."

        lines = ["Top jobs to apply to first:"]
        for _, row in top_df.iterrows():
            lines.append(
                f"• {row['company']} | {row['role']} | Deadline: {row['deadline']} | Score: {row['priority_score']}"
            )
        return "\n".join(lines)

    if "high priority" in query:
        high_df = active_df[active_df["priority_label"] == "High"]
        if high_df.empty:
            return "No high-priority jobs are available right now."

        lines = ["High-priority jobs:"]
        for _, row in high_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    if "internship" in query:
        internships_df = active_df[
            active_df["job_type"].str.contains("Internship", case=False, na=False)
        ]
        if internships_df.empty:
            return "No internship opportunities are available right now."

        lines = ["Internship opportunities:"]
        for _, row in internships_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    if "remote" in query:
        remote_df = active_df[
            active_df["location"].str.contains("Remote", case=False, na=False)
        ]
        if remote_df.empty:
            return "No remote jobs are available right now."

        lines = ["Remote jobs:"]
        for _, row in remote_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    if (
        "machine learning" in query
        or "artificial intelligence" in query
        or "deep learning" in query
        or "computer vision" in query
        or ("ai" in query and "role" in query)
    ):
        ml_df = active_df[
            active_df["role"].str.contains(
                "Machine Learning|Artificial Intelligence|AI|Deep Learning|Computer Vision",
                case=False,
                na=False
            )
        ]
        if ml_df.empty:
            return "No machine learning or artificial intelligence roles are available right now."

        lines = ["Machine learning and artificial intelligence roles:"]
        for _, row in ml_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    if "deadline" in query or "coming soon" in query or "urgent" in query:
        deadline_df = active_df[active_df["parsed_deadline"].notna()].sort_values(
            by="parsed_deadline",
            ascending=True
        )
        if deadline_df.empty:
            return "No upcoming deadlines are available right now."

        lines = ["Upcoming deadlines:"]
        for _, row in deadline_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    if "why" in query or "explain" in query:
        if active_df.empty:
            return "There is no active top recommendation to explain."

        top_job = active_df.iloc[0]
        reasons = []

        role_lower = str(top_job["role"]).lower()
        if any(term in role_lower for term in [
            "data science", "data scientist", "machine learning",
            "ai", "deep learning", "computer vision"
        ]):
            reasons.append("it matches your target technical area")

        if top_job["deadline"] != "Not specified":
            reasons.append(f"the deadline is {top_job['deadline']}")

        if top_job["job_type"] not in ["Unknown", "Not specified"]:
            reasons.append(f"it is a {str(top_job['job_type']).lower()} opportunity")

        if "remote" in str(top_job["location"]).lower():
            reasons.append("it offers remote flexibility")

        reason_text = "; ".join(reasons) if reasons else "it currently has the strongest combined score"

        return (
            f"Top recommendation: {top_job['company']} | {top_job['role']}. "
            f"It is ranked highly because {reason_text}."
        )

    if "low priority" in query or "ignore" in query:
        low_df = active_df[active_df["priority_label"] == "Low"]
        if low_df.empty:
            return "There are no low-priority active jobs right now."

        lines = ["Lower-priority jobs:"]
        for _, row in low_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    if "expired" in query:
        expired_df = df[df["is_expired"]]
        if expired_df.empty:
            return "There are no expired jobs right now."

        lines = ["Expired jobs:"]
        for _, row in expired_df.head(8).iterrows():
            lines.append(f"• {row['company']} | {row['role']} | Deadline: {row['deadline']}")
        return "\n".join(lines)

    return (
        "Try one of these:\n"
        "• What should I apply to first?\n"
        "• Show high priority jobs\n"
        "• Show internships\n"
        "• Show remote jobs\n"
        "• Show machine learning roles\n"
        "• Show upcoming deadlines\n"
        "• Explain top job\n"
        "• Show low priority jobs\n"
        "• Show expired jobs\n"
        "• Summarize jobs"
    )


# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #fffafc 0%, #f8fbff 45%, #f7fff9 100%);
    }

    .hero-box {
        padding: 1.2rem 1.4rem;
        border-radius: 24px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(230,230,240,0.9);
        box-shadow: 0 10px 30px rgba(120, 120, 160, 0.08);
        margin-bottom: 1rem;
    }

    .metric-card {
        border-radius: 20px;
        padding: 1rem 1rem 0.9rem 1rem;
        color: #334155;
        box-shadow: 0 8px 24px rgba(100, 100, 140, 0.08);
        border: 1px solid rgba(255,255,255,0.8);
        min-height: 110px;
    }

    .metric-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.45rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
    }

    .card-wrap {
        border-radius: 22px;
        padding: 1rem;
        background: rgba(255,255,255,0.82);
        border: 1px solid #ececf3;
        box-shadow: 0 8px 24px rgba(120, 120, 150, 0.08);
    }

    .job-company {
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .job-role {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: #334155;
    }

    .job-meta {
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 0.4rem;
    }

    .soft-label {
        display: inline-block;
        padding: 0.3rem 0.65rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        background: #f6eefe;
        color: #7c3aed;
        margin-top: 0.45rem;
    }

    .section-title {
        font-size: 1.2rem;
        font-weight: 800;
        margin: 0.5rem 0 0.8rem 0;
        color: #334155;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 18px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Load data
# -----------------------------
raw_df = load_jobs()
jobs_df = prepare_jobs(raw_df)

st.markdown("""
<div class="hero-box">
    <h1 style="margin-bottom:0.2rem;">CareerPilot AI</h1>
    <p style="margin:0;color:#64748b;font-size:1rem;">
        Personal job search assistant with recommendations, filtering, and chat support
    </p>
</div>
""", unsafe_allow_html=True)

if jobs_df.empty:
    st.warning("No job data found. Run your backend pipeline first.")
    st.stop()

active_jobs_df = sorted_active_jobs(jobs_df)

# -----------------------------
# Section 1: Overview cards
# -----------------------------
total_jobs = len(jobs_df)
high_priority = len(active_jobs_df[active_jobs_df["priority_label"] == "High"])
internships = len(active_jobs_df[active_jobs_df["job_type"].str.contains("Internship", case=False, na=False)])
remote_jobs = len(active_jobs_df[active_jobs_df["location"].str.contains("Remote", case=False, na=False)])
upcoming_deadlines = len(active_jobs_df[active_jobs_df["parsed_deadline"].notna()])

metric_cols = st.columns(5)
metric_info = [
    ("Total Opportunities", total_jobs, "#E7F0FF"),
    ("High Priority Jobs", high_priority, "#FFE6EC"),
    ("Internships", internships, "#E8F8EC"),
    ("Remote Jobs", remote_jobs, "#FFF0E3"),
    ("Upcoming Deadlines", upcoming_deadlines, "#EFE9FF"),
]

for col, (label, value, bg) in zip(metric_cols, metric_info):
    with col:
        st.markdown(f"""
        <div class="metric-card" style="background:{bg};">
            <div class="metric-title">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='section-title'>Top Recommendations</div>", unsafe_allow_html=True)

# -----------------------------
# Section 2: Top recommendation cards
# -----------------------------
top_df = active_jobs_df.head(3)
card_cols = st.columns(3)

for i, col in enumerate(card_cols):
    if i < len(top_df):
        row = top_df.iloc[i]
        company = row["company"]
        role = row["role"]
        location = row["location"]
        deadline = row["deadline"]
        priority_label = row["priority_label"]
        priority_score = row["priority_score"]
        apply_link = row["apply_link"]

        with col:
            st.markdown("<div class='card-wrap'>", unsafe_allow_html=True)

            if apply_link and str(apply_link).strip() not in ["", "None"]:
                st.markdown(
                    f"<div class='job-company'><a href='{apply_link}' target='_blank' style='text-decoration:none;color:#1f2937;'>{company}</a></div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='job-role'><a href='{apply_link}' target='_blank' style='text-decoration:none;color:#475569;'>{role}</a></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"<div class='job-company'>{company}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='job-role'>{role}</div>", unsafe_allow_html=True)

            st.markdown(f"<div class='job-meta'>📍 {location}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='job-meta'>📅 Deadline: {deadline}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<span class='soft-label'>{priority_label} • Score {priority_score}</span>",
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:0.7rem'></div>", unsafe_allow_html=True)

            if apply_link and str(apply_link).strip() not in ["", "None"]:
                st.link_button("Apply Now", apply_link)

            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>All Opportunities</div>", unsafe_allow_html=True)

# -----------------------------
# Section 3: Filters + table
# -----------------------------
f1, f2, f3, f4 = st.columns(4)

priority_filter = f1.selectbox("Priority", ["All", "High", "Medium", "Low", "Expired"])
job_type_options = ["All"] + sorted(jobs_df["job_type"].dropna().astype(str).unique().tolist())
job_type_filter = f2.selectbox("Job Type", job_type_options)
location_filter = f3.selectbox("Location", ["All", "Remote only", "Non-remote only"])
company_options = ["All"] + sorted(jobs_df["company"].dropna().astype(str).unique().tolist())
company_filter = f4.selectbox("Company", company_options)

table_df = jobs_df.copy()

if priority_filter == "Expired":
    table_df = table_df[table_df["is_expired"]]
elif priority_filter != "All":
    table_df = table_df[table_df["priority_label"] == priority_filter]

if job_type_filter != "All":
    table_df = table_df[table_df["job_type"] == job_type_filter]

if location_filter == "Remote only":
    table_df = table_df[table_df["location"].str.contains("Remote", case=False, na=False)]
elif location_filter == "Non-remote only":
    table_df = table_df[~table_df["location"].str.contains("Remote", case=False, na=False)]

if company_filter != "All":
    table_df = table_df[table_df["company"] == company_filter]

table_df = table_df.sort_values(
    by=["priority_score", "parsed_deadline"],
    ascending=[False, True],
    na_position="last"
)

display_df = table_df[[
    "company",
    "role",
    "location",
    "deadline",
    "job_type",
    "priority_score",
    "priority_label"
]].rename(columns={
    "company": "Company",
    "role": "Role",
    "location": "Location",
    "deadline": "Deadline",
    "job_type": "Job Type",
    "priority_score": "Priority Score",
    "priority_label": "Priority Label"
})

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("<div class='section-title'>Ask CareerPilot AI</div>", unsafe_allow_html=True)

# -----------------------------
# Section 4: Chat assistant
# -----------------------------
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi — I can help you review your job opportunities.\n\n"
                "Try asking:\n"
                "- What should I apply to first?\n"
                "- Show upcoming deadlines\n"
                "- Show remote jobs\n"
                "- Explain top job"
            )
        }
    ]

chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

prompt = st.chat_input("Ask about your jobs...")

if prompt:
    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    reply = assistant_response(prompt, jobs_df)
    st.session_state.chat_messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)