import datetime
import os
import uuid

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data import (
    DEFAULT_EMPLOYEES,
    EMPLOYEES_COLUMNS,
    LIKERT_KEYS,
    QUESTIONNAIRE,
    RESPONSES_COLUMNS,
    current_week,
    score_label,
)

# ── paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSES_FILE = os.path.join(BASE_DIR, "responses.csv")
EMPLOYEES_FILE = os.path.join(BASE_DIR, "employees.csv")

# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
<style>
:root {
    --navy:   #0d1b2a;
    --blue:   #1e3a5f;
    --accent: #2980b9;
    --gold:   #f39c12;
    --green:  #27ae60;
    --red:    #e74c3c;
    --bg:     #f4f6f9;
    --card:   #ffffff;
    --text:   #2c3e50;
    --muted:  #7f8c8d;
}
[data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
[data-testid="stSidebar"] * { color: #ecf0f1 !important; }
[data-testid="stSidebar"] .stButton button {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.2);
    color: #ecf0f1 !important;
    border-radius: 6px;
    width: 100%;
    text-align: left;
    padding: 8px 14px;
    margin-bottom: 4px;
    font-size: 0.9rem;
    transition: background 0.2s;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.1);
}
.page-title {
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 0.2rem;
}
.page-sub {
    font-size: 0.95rem;
    color: var(--muted);
    margin-bottom: 1.4rem;
}
.kpi-card {
    background: var(--card);
    border-radius: 10px;
    padding: 20px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--navy);
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 4px;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}
.section-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--navy);
    border-left: 4px solid var(--accent);
    padding-left: 10px;
    margin: 1.4rem 0 0.8rem;
}
.survey-card {
    background: var(--card);
    border-radius: 10px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.emp-row {
    background: var(--card);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
hr.divider {
    border: none;
    border-top: 1px solid #e0e4ea;
    margin: 1.2rem 0;
}
</style>
"""

# ── file helpers ─────────────────────────────────────────────────────────────

def load_employees() -> pd.DataFrame:
    if os.path.exists(EMPLOYEES_FILE):
        return pd.read_csv(EMPLOYEES_FILE, dtype=str)
    df = pd.DataFrame(DEFAULT_EMPLOYEES)[EMPLOYEES_COLUMNS]
    df.to_csv(EMPLOYEES_FILE, index=False)
    return df


def save_employees(df: pd.DataFrame):
    df.to_csv(EMPLOYEES_FILE, index=False)


def load_responses() -> pd.DataFrame:
    if os.path.exists(RESPONSES_FILE):
        df = pd.read_csv(RESPONSES_FILE, dtype=str)
        for k in LIKERT_KEYS:
            df[k] = pd.to_numeric(df[k], errors="coerce")
        df["week"] = pd.to_numeric(df["week"], errors="coerce")
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        return df
    return pd.DataFrame(columns=RESPONSES_COLUMNS)


def append_response(row: dict):
    df = load_responses()
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(RESPONSES_FILE, index=False)


def already_submitted(employee_id: str, week: int, year: int) -> bool:
    df = load_responses()
    if df.empty:
        return False
    mask = (df["employee_id"] == str(employee_id)) & (df["week"] == week) & (df["year"] == year)
    return mask.any()


def engagement_score(row: pd.Series) -> float:
    vals = [row[k] for k in LIKERT_KEYS if pd.notna(row[k])]
    return round(sum(vals) / len(vals), 2) if vals else 0.0


# ── sidebar nav ───────────────────────────────────────────────────────────────

PAGES = ["Dashboard", "Take Survey", "Employees", "Analytics", "History"]

def sidebar():
    st.sidebar.markdown(
        """
        <div style='padding:16px 0 24px;'>
          <div style='font-size:1.25rem;font-weight:800;color:#ecf0f1;'>People Analytics</div>
          <div style='font-size:0.78rem;color:#95a5a6;margin-top:2px;'>Bench Engagement Tracker</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    icons = {"Dashboard": "📊", "Take Survey": "📝", "Employees": "👥", "Analytics": "📈", "History": "🗂️"}
    for p in PAGES:
        if st.sidebar.button(f"{icons[p]}  {p}", key=f"nav_{p}"):
            st.session_state.page = p

    week, year = current_week()
    st.sidebar.markdown(
        f"""
        <div style='margin-top:auto;padding:16px 0 8px;font-size:0.75rem;color:#7f8c8d;'>
            Week {week} · {year}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── page: dashboard ───────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    week, year = current_week()
    st.markdown(
        f'<div class="page-sub">Weekly snapshot — Week {week}, {year}</div>',
        unsafe_allow_html=True,
    )

    employees = load_employees()
    responses = load_responses()
    total = len(employees)

    week_df = responses[(responses["week"] == week) & (responses["year"] == year)] if not responses.empty else pd.DataFrame()
    submitted_ids = set(week_df["employee_id"].tolist()) if not week_df.empty else set()
    submitted_count = len(submitted_ids)
    pct = round(submitted_count / total * 100) if total else 0

    avg_score = 0.0
    at_risk = 0
    if not week_df.empty:
        week_df = week_df.copy()
        week_df["score"] = week_df.apply(engagement_score, axis=1)
        avg_score = round(week_df["score"].mean(), 2)
        at_risk = int((week_df["score"] < 3).sum())

    label, colour = score_label(avg_score)

    # KPI strip
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [
        (c1, total, "Bench Headcount"),
        (c2, f"{pct}%", "Survey Completion"),
        (c3, f"{avg_score:.1f} / 5", "Avg Engagement"),
        (c4, at_risk, "At-Risk Employees"),
    ]:
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-value">{val}</div>'
            f'<div class="kpi-label">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-header">Pending Submissions This Week</div>', unsafe_allow_html=True)
    pending = employees[~employees["id"].isin(submitted_ids)]
    if pending.empty:
        st.success("All bench employees have submitted their survey this week!")
    else:
        cols = st.columns([3, 2, 2])
        cols[0].markdown("**Name**")
        cols[1].markdown("**Role**")
        cols[2].markdown("**Bench Since**")
        for _, row in pending.iterrows():
            c0, c1, c2 = st.columns([3, 2, 2])
            c0.write(row["name"])
            c1.write(row["role"])
            c2.write(row["bench_since"])

    if not week_df.empty and "score" in week_df.columns:
        st.markdown('<div class="section-header">Engagement Scores — Current Week</div>', unsafe_allow_html=True)
        fig = px.bar(
            week_df.sort_values("score"),
            x="score",
            y="employee_name",
            orientation="h",
            color="score",
            color_continuous_scale=["#e74c3c", "#f39c12", "#27ae60"],
            range_color=[1, 5],
            labels={"score": "Engagement Score", "employee_name": ""},
            height=max(300, len(week_df) * 36),
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="white",
            plot_bgcolor="white",
            coloraxis_showscale=False,
            xaxis=dict(range=[0, 5], gridcolor="#ecf0f1"),
            yaxis=dict(gridcolor="#ecf0f1"),
        )
        fig.add_vline(x=3, line_dash="dash", line_color="#e74c3c", annotation_text="At-risk threshold")
        st.plotly_chart(fig, use_container_width=True)

    # Week-on-week trend
    if not responses.empty:
        trend = responses.copy()
        trend["score"] = trend.apply(engagement_score, axis=1)
        trend["week_label"] = "W" + trend["week"].astype(int).astype(str) + " '" + (trend["year"].astype(int) % 100).astype(str)
        agg = trend.groupby("week_label")["score"].mean().reset_index().rename(columns={"score": "avg_score"})

        if len(agg) >= 2:
            st.markdown('<div class="section-header">Week-on-Week Trend</div>', unsafe_allow_html=True)
            fig2 = px.line(
                agg,
                x="week_label",
                y="avg_score",
                markers=True,
                labels={"week_label": "Week", "avg_score": "Avg Engagement"},
            )
            fig2.update_traces(line_color="#2980b9", marker_color="#2980b9")
            fig2.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="white",
                plot_bgcolor="white",
                yaxis=dict(range=[0, 5.2], gridcolor="#ecf0f1"),
                xaxis=dict(gridcolor="#ecf0f1"),
            )
            fig2.add_hrect(y0=0, y1=3, fillcolor="#e74c3c", opacity=0.05, line_width=0)
            st.plotly_chart(fig2, use_container_width=True)


# ── page: take survey ─────────────────────────────────────────────────────────

def page_take_survey():
    st.markdown('<div class="page-title">Weekly Engagement Survey</div>', unsafe_allow_html=True)
    week, year = current_week()
    st.markdown(
        f'<div class="page-sub">Week {week}, {year} — please answer honestly, responses are reviewed by your People Manager.</div>',
        unsafe_allow_html=True,
    )

    employees = load_employees()
    names = ["— select your name —"] + employees["name"].tolist()
    selected_name = st.selectbox("Your name", names)

    if selected_name == "— select your name —":
        return

    emp_row = employees[employees["name"] == selected_name].iloc[0]
    emp_id = emp_row["id"]

    if already_submitted(emp_id, week, year):
        st.success(
            f"You've already submitted your survey for Week {week}. "
            "Come back next week — thank you!"
        )
        return

    st.markdown(f'<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-header">Hi {selected_name.split()[0]}! Please complete the survey below.</div>',
        unsafe_allow_html=True,
    )

    answers: dict = {}

    with st.form("survey_form", clear_on_submit=False):
        for q in QUESTIONNAIRE:
            st.markdown(f'<div class="survey-card">', unsafe_allow_html=True)
            st.markdown(f"**{q['label']}**")
            st.markdown(q["text"])

            if q["type"] == "likert":
                val = st.slider(
                    q["key"],
                    min_value=1,
                    max_value=5,
                    value=3,
                    help=q.get("help", ""),
                    label_visibility="collapsed",
                )
                st.caption(q.get("help", ""))
                answers[q["key"]] = val

            elif q["type"] == "select":
                val = st.selectbox(
                    q["key"],
                    options=q["options"],
                    label_visibility="collapsed",
                )
                answers[q["key"]] = val

            elif q["type"] == "text":
                val = st.text_area(
                    q["key"],
                    placeholder=q.get("placeholder", ""),
                    label_visibility="collapsed",
                )
                answers[q["key"]] = val

            st.markdown("</div>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Submit Survey", type="primary", use_container_width=True)

    if submitted:
        row = {
            "week": week,
            "year": year,
            "employee_id": emp_id,
            "employee_name": selected_name,
            "q1": answers.get("q1"),
            "q2": answers.get("q2"),
            "q3": answers.get("q3"),
            "q4": answers.get("q4"),
            "q5": answers.get("q5"),
            "q6": answers.get("q6"),
            "q7_readiness": answers.get("q7_readiness"),
            "q8_activity": answers.get("q8_activity"),
            "q9_concerns": answers.get("q9_concerns", ""),
            "q10_goals": answers.get("q10_goals", ""),
            "submitted_at": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        append_response(row)
        st.success("Survey submitted! Thank you for your response.")
        st.balloons()


# ── page: employees ───────────────────────────────────────────────────────────

def page_employees():
    st.markdown('<div class="page-title">Bench Employees</div>', unsafe_allow_html=True)
    week, year = current_week()
    st.markdown(
        '<div class="page-sub">Manage the list of employees currently on the bench.</div>',
        unsafe_allow_html=True,
    )

    employees = load_employees()
    responses = load_responses()
    week_df = responses[(responses["week"] == week) & (responses["year"] == year)] if not responses.empty else pd.DataFrame()
    submitted_ids = set(week_df["employee_id"].tolist()) if not week_df.empty else set()

    st.markdown('<div class="section-header">Current Bench Roster</div>', unsafe_allow_html=True)

    display = employees.copy()
    display["This Week"] = display["id"].apply(lambda x: "Submitted" if x in submitted_ids else "Pending")
    st.dataframe(
        display.rename(columns={"id": "ID", "name": "Name", "role": "Role", "bench_since": "Bench Since"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown('<div class="section-header">Add Employee</div>', unsafe_allow_html=True)
    with st.form("add_emp_form"):
        col1, col2, col3 = st.columns(3)
        new_name = col1.text_input("Full Name")
        new_role = col2.text_input("Role / Title")
        new_since = col3.date_input("Bench Since", value=datetime.date.today())
        add_clicked = st.form_submit_button("Add Employee")

    if add_clicked:
        if not new_name.strip():
            st.error("Name is required.")
        elif new_name.strip() in employees["name"].values:
            st.warning(f"'{new_name}' already exists in the roster.")
        else:
            existing_ids = employees["id"].str.replace("E", "", regex=False).astype(int)
            next_id = f"E{existing_ids.max() + 1:03d}"
            new_row = pd.DataFrame([{
                "id": next_id,
                "name": new_name.strip(),
                "role": new_role.strip(),
                "bench_since": str(new_since),
            }])
            employees = pd.concat([employees, new_row], ignore_index=True)
            save_employees(employees)
            st.success(f"Added {new_name} (ID: {next_id})")
            st.rerun()

    st.markdown('<div class="section-header">Remove Employee</div>', unsafe_allow_html=True)
    remove_name = st.selectbox("Select employee to remove", ["— select —"] + employees["name"].tolist(), key="remove_sel")
    if remove_name != "— select —":
        if st.button(f"Remove {remove_name}", type="secondary"):
            employees = employees[employees["name"] != remove_name]
            save_employees(employees)
            st.success(f"Removed {remove_name} from the bench roster.")
            st.rerun()


# ── page: analytics ───────────────────────────────────────────────────────────

def page_analytics():
    st.markdown('<div class="page-title">Analytics</div>', unsafe_allow_html=True)
    week, year = current_week()
    st.markdown(
        f'<div class="page-sub">Detailed breakdown for Week {week}, {year}</div>',
        unsafe_allow_html=True,
    )

    responses = load_responses()
    if responses.empty:
        st.info("No survey responses yet. Ask your team to complete the survey first.")
        return

    week_df = responses[(responses["week"] == week) & (responses["year"] == year)].copy()

    if week_df.empty:
        st.warning(f"No responses for Week {week} yet.")
    else:
        week_df["score"] = week_df.apply(engagement_score, axis=1)

        # Radar: avg per question
        st.markdown('<div class="section-header">Average Score by Question (Q1–Q6)</div>', unsafe_allow_html=True)
        q_labels = [f"Q{i+1}" for i in range(6)]
        q_avgs = [week_df[k].mean() for k in LIKERT_KEYS]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=q_avgs + [q_avgs[0]],
            theta=q_labels + [q_labels[0]],
            fill="toself",
            fillcolor="rgba(41,128,185,0.2)",
            line=dict(color="#2980b9"),
            name="Avg Score",
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        col_left, col_right = st.columns(2)

        # Readiness pie
        with col_left:
            st.markdown('<div class="section-header">Placement Readiness</div>', unsafe_allow_html=True)
            ready_counts = week_df["q7_readiness"].value_counts().reset_index()
            ready_counts.columns = ["status", "count"]
            fig_pie = px.pie(
                ready_counts,
                names="status",
                values="count",
                color_discrete_sequence=["#27ae60", "#f39c12", "#e74c3c"],
            )
            fig_pie.update_layout(margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="white")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Activity bar
        with col_right:
            st.markdown('<div class="section-header">Primary Activity Breakdown</div>', unsafe_allow_html=True)
            act_counts = week_df["q8_activity"].value_counts().reset_index()
            act_counts.columns = ["activity", "count"]
            fig_act = px.bar(
                act_counts,
                x="count",
                y="activity",
                orientation="h",
                color_discrete_sequence=["#2980b9"],
            )
            fig_act.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="white",
                plot_bgcolor="white",
                yaxis_title="",
                xaxis_title="Responses",
                xaxis=dict(gridcolor="#ecf0f1"),
            )
            st.plotly_chart(fig_act, use_container_width=True)

        # Concerns & goals
        st.markdown('<div class="section-header">Open Feedback — Concerns & Blockers</div>', unsafe_allow_html=True)
        concerns = week_df[week_df["q9_concerns"].str.strip().astype(bool)][["employee_name", "q9_concerns"]]
        if concerns.empty:
            st.info("No concerns flagged this week.")
        else:
            for _, r in concerns.iterrows():
                st.markdown(f"**{r['employee_name']}:** {r['q9_concerns']}")

        st.markdown('<div class="section-header">Open Feedback — Goals for Next Week</div>', unsafe_allow_html=True)
        goals = week_df[week_df["q10_goals"].str.strip().astype(bool)][["employee_name", "q10_goals"]]
        if goals.empty:
            st.info("No goals recorded this week.")
        else:
            for _, r in goals.iterrows():
                st.markdown(f"**{r['employee_name']}:** {r['q10_goals']}")


# ── page: history ─────────────────────────────────────────────────────────────

def page_history():
    st.markdown('<div class="page-title">Survey History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Browse and download past weekly responses.</div>', unsafe_allow_html=True)

    responses = load_responses()
    if responses.empty:
        st.info("No responses recorded yet.")
        return

    responses = responses.copy()
    responses["week_label"] = (
        "Week " + responses["week"].astype(int).astype(str) + " — " + responses["year"].astype(int).astype(str)
    )
    week_options = sorted(responses["week_label"].unique(), reverse=True)
    selected_week = st.selectbox("Select week", week_options)

    filtered = responses[responses["week_label"] == selected_week].copy()
    filtered["score"] = filtered.apply(engagement_score, axis=1).round(2)

    display_cols = [
        "employee_name", "score",
        "q1", "q2", "q3", "q4", "q5", "q6",
        "q7_readiness", "q8_activity",
        "q9_concerns", "q10_goals",
        "submitted_at",
    ]
    col_rename = {
        "employee_name": "Employee", "score": "Eng. Score",
        "q1": "Q1", "q2": "Q2", "q3": "Q3", "q4": "Q4", "q5": "Q5", "q6": "Q6",
        "q7_readiness": "Readiness", "q8_activity": "Activity",
        "q9_concerns": "Concerns", "q10_goals": "Next Week Goals",
        "submitted_at": "Submitted At",
    }
    st.dataframe(
        filtered[display_cols].rename(columns=col_rename),
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = filtered[display_cols].rename(columns=col_rename).to_csv(index=False).encode()
    week_slug = selected_week.replace(" ", "_").replace("—", "-")
    st.download_button(
        label="Download as CSV",
        data=csv_bytes,
        file_name=f"bench_survey_{week_slug}.csv",
        mime="text/csv",
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Bench Engagement Tracker",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    sidebar()

    page = st.session_state.get("page", "Dashboard")

    if page == "Dashboard":
        page_dashboard()
    elif page == "Take Survey":
        page_take_survey()
    elif page == "Employees":
        page_employees()
    elif page == "Analytics":
        page_analytics()
    elif page == "History":
        page_history()


if __name__ == "__main__":
    main()
