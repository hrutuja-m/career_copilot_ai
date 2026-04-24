# CareerPilot AI  
### A personal intelligent assistant for job search, opportunity prioritization, and career decision support

## Overview

CareerPilot AI is a personal job search assistant that helps users manage the chaos of career-related emails.

Instead of manually reading through job alerts, reminders, application updates, and unrelated inbox noise, CareerPilot AI turns email content into a structured and useful opportunity system. It identifies relevant job emails, extracts important job details, removes repeated alerts, ranks opportunities by priority, and allows users to ask natural questions about what they should apply to first.

This project was designed from the perspective that job searching is not only an information problem. It is also a prioritization problem.

Many students and early-career applicants miss strong opportunities because:
- important emails get buried under noise,
- deadlines pass unnoticed,
- duplicate alerts create confusion,
- and there is no clear system for deciding what matters most.

CareerPilot AI is built to solve that.

---

## The problem

Most job seekers do not struggle because opportunities do not exist.  
They struggle because opportunities are scattered, repetitive, unstructured, and difficult to prioritize.

A typical inbox contains:
- job alerts,
- internship announcements,
- reminder emails,
- application status updates,
- newsletters,
- event invitations,
- and unrelated messages.

This creates a workflow problem:

**How can a user turn messy job-related emails into a clean, ranked, actionable opportunity list?**

CareerPilot AI addresses that by creating a personal assistant layer on top of email-based job discovery.

---

## What the system does

CareerPilot AI currently supports the following workflow:

1. Load raw email data into a database  
2. Identify which emails are actually related to job opportunities  
3. Extract structured job details from unstructured email text  
4. Remove duplicate alerts and repeated reminders  
5. Rank opportunities based on relevance and urgency  
6. Present results in a web interface  
7. Answer natural language questions through a chat-style assistant  

---

## Core features

### Email relevance filtering
The system separates meaningful career emails from irrelevant messages such as newsletters, promotions, events, and general updates.

### Information extraction
From relevant emails, the system extracts:
- company
- role
- location
- deadline
- application link
- job type
- source subject
- received date

### Duplicate handling
Repeated alerts and reminder emails are detected and removed so that the final opportunity list is cleaner and more useful.

### Priority scoring
Each opportunity is ranked using a scoring system based on:
- deadline urgency
- role relevance
- job type
- location
- record completeness

### Expired deadline handling
Expired opportunities are separated from active opportunities so that older jobs do not interfere with current recommendations.

### Chat-style assistant
Users can ask questions such as:
- What should I apply to first?
- Show high priority jobs
- Show remote jobs
- Show internships
- Show upcoming deadlines
- Explain top job

### Web interface
The project includes a Streamlit-based web application with:
- summary cards
- recommendation cards
- a filterable opportunity table
- a chat-style assistant section

---

## Why this project matters

CareerPilot AI is not just a parser or a chatbot. It is a **decision-support system**.

The goal is not simply to collect job information.  
The goal is to help a user decide:
- what matters now,
- what can wait,
- what is expired,
- and what deserves immediate action.

This project can grow into a real-world personal career dashboard for:
- students,
- job seekers,
- internship applicants,
- and professionals tracking opportunities from multiple sources.

---

## System design

### Current pipeline

```text
Raw email dataset
    ↓
Load into database
    ↓
Relevant or irrelevant filtering
    ↓
Job detail extraction
    ↓
Duplicate cleanup
    ↓
Priority scoring
    ↓
Web interface + chat assistant
