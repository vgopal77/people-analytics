import datetime

DEFAULT_EMPLOYEES = [
    {"id": "E001", "name": "Alice Johnson",    "role": "Software Engineer",       "bench_since": "2026-04-15"},
    {"id": "E002", "name": "Brian Patel",       "role": "Data Analyst",            "bench_since": "2026-05-01"},
    {"id": "E003", "name": "Carla Nguyen",      "role": "Project Manager",         "bench_since": "2026-04-22"},
    {"id": "E004", "name": "David Kim",         "role": "QA Engineer",             "bench_since": "2026-05-10"},
    {"id": "E005", "name": "Elena Rossi",       "role": "UX Designer",             "bench_since": "2026-04-28"},
    {"id": "E006", "name": "Frank Obi",         "role": "DevOps Engineer",         "bench_since": "2026-05-05"},
    {"id": "E007", "name": "Grace Liu",         "role": "Business Analyst",        "bench_since": "2026-05-12"},
    {"id": "E008", "name": "Henry Müller",      "role": "Cloud Architect",         "bench_since": "2026-04-10"},
    {"id": "E009", "name": "Isabelle Tremblay", "role": "Scrum Master",            "bench_since": "2026-05-20"},
    {"id": "E010", "name": "James Carter",      "role": "Full Stack Developer",    "bench_since": "2026-05-03"},
    {"id": "E011", "name": "Kavya Sharma",      "role": "Data Scientist",          "bench_since": "2026-05-18"},
    {"id": "E012", "name": "Liam O'Brien",      "role": "Security Analyst",        "bench_since": "2026-04-30"},
    {"id": "E013", "name": "Maya Fernandez",    "role": "ML Engineer",             "bench_since": "2026-05-07"},
    {"id": "E014", "name": "Nathan Brooks",     "role": "Technical Lead",          "bench_since": "2026-05-15"},
    {"id": "E015", "name": "Olivia Zhang",      "role": "Product Analyst",         "bench_since": "2026-05-22"},
]

QUESTIONNAIRE = [
    {
        "key": "q1",
        "label": "Q1 — Overall Engagement",
        "text": "How would you rate your overall engagement this week?",
        "type": "likert",
        "help": "1 = Very disengaged, 5 = Highly engaged",
    },
    {
        "key": "q2",
        "label": "Q2 — Bench Activity Satisfaction",
        "text": "How satisfied are you with your current bench activities?",
        "type": "likert",
        "help": "1 = Very dissatisfied, 5 = Very satisfied",
    },
    {
        "key": "q3",
        "label": "Q3 — Manager Support",
        "text": "Do you feel supported by your manager / team this week?",
        "type": "likert",
        "help": "1 = Not at all, 5 = Fully supported",
    },
    {
        "key": "q4",
        "label": "Q4 — Learning & Upskilling",
        "text": "Are you getting sufficient upskilling or training opportunities?",
        "type": "likert",
        "help": "1 = None at all, 5 = Excellent opportunities",
    },
    {
        "key": "q5",
        "label": "Q5 — Placement Clarity",
        "text": "How clear are you on your project placement timeline?",
        "type": "likert",
        "help": "1 = Completely unclear, 5 = Very clear",
    },
    {
        "key": "q6",
        "label": "Q6 — Leadership Communication",
        "text": "How well is leadership keeping you informed about organisational updates?",
        "type": "likert",
        "help": "1 = Very poorly, 5 = Excellent",
    },
    {
        "key": "q7_readiness",
        "label": "Q7 — Placement Readiness",
        "text": "How ready do you feel for a new project placement?",
        "type": "select",
        "options": ["Ready", "Almost Ready", "Not Yet"],
    },
    {
        "key": "q8_activity",
        "label": "Q8 — Primary Activity This Week",
        "text": "What was your primary activity this week?",
        "type": "select",
        "options": ["Training / Certification", "Self-Study", "Internal Project", "Administrative / Compliance", "Other"],
    },
    {
        "key": "q9_concerns",
        "label": "Q9 — Concerns or Blockers",
        "text": "Do you have any concerns or blockers you'd like to flag?",
        "type": "text",
        "placeholder": "Optional — share anything on your mind",
    },
    {
        "key": "q10_goals",
        "label": "Q10 — Goals for Next Week",
        "text": "What are your goals for next week?",
        "type": "text",
        "placeholder": "E.g. complete AWS certification module 3, attend project shadowing session…",
    },
]

RESPONSES_COLUMNS = [
    "week", "year", "employee_id", "employee_name",
    "q1", "q2", "q3", "q4", "q5", "q6",
    "q7_readiness", "q8_activity", "q9_concerns", "q10_goals",
    "submitted_at",
]

EMPLOYEES_COLUMNS = ["id", "name", "role", "bench_since"]

LIKERT_KEYS = ["q1", "q2", "q3", "q4", "q5", "q6"]

SCORE_LABELS = {
    (4.0, 5.0): ("High", "#27ae60"),
    (3.0, 3.99): ("Medium", "#f39c12"),
    (0.0, 2.99): ("Low", "#e74c3c"),
}


def score_label(score: float) -> tuple[str, str]:
    if score >= 4.0:
        return "High", "#27ae60"
    if score >= 3.0:
        return "Medium", "#f39c12"
    return "Low", "#e74c3c"


def current_week() -> tuple[int, int]:
    iso = datetime.date.today().isocalendar()
    return int(iso[1]), int(iso[0])  # week, year
