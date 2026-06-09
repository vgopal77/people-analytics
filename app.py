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
    --dxc-purple:  #702F8A;
    --dxc-dark:    #3C1053;
    --dxc-teal:    #00B0CA;
    --dxc-teal2:   #007A8C;
    --dxc-lilac:   #E8D5F5;
    --green:       #00C897;
    --amber:       #FF8C00;
    --red:         #E63946;
    --bg:          #F7F2FB;
    --card:        #FFFFFF;
    --text:        #1A1A1A;
    --muted:       #6B6B6B;
    --border:      #E2D5EC;
}

/* ── global ── */
[data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stMain"] { padding-top: 0 !important; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3C1053 0%, #702F8A 60%, #9B5CAD 100%) !important;
}
[data-testid="stSidebar"] * { color: #F0E6F8 !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    color: #F0E6F8 !important;
    border-radius: 8px;
    width: 100%;
    text-align: left;
    padding: 10px 14px;
    margin-bottom: 6px;
    font-size: 0.88rem;
    font-weight: 500;
    transition: background 0.2s, border-color 0.2s;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.18);
    border-color: rgba(255,255,255,0.35);
}

/* ── hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #3C1053 0%, #702F8A 55%, #00B0CA 100%);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    color: white;
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: "";
    position: absolute;
    right: -40px; top: -40px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.hero-title {
    font-size: 1.65rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}
.hero-sub {
    font-size: 0.92rem;
    color: rgba(255,255,255,0.75);
}
.hero-week {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
    margin-top: 10px;
    letter-spacing: 0.04em;
}

/* ── KPI cards ── */
.kpi-card {
    border-radius: 14px;
    padding: 22px 18px;
    color: white;
    position: relative;
    overflow: hidden;
    min-height: 120px;
}
.kpi-card::before {
    content: "";
    position: absolute;
    right: -20px; bottom: -20px;
    width: 100px; height: 100px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
}
.kpi-purple  { background: linear-gradient(135deg, #702F8A, #9B5CAD); }
.kpi-teal    { background: linear-gradient(135deg, #007A8C, #00B0CA); }
.kpi-green   { background: linear-gradient(135deg, #00957A, #00C897); }
.kpi-red     { background: linear-gradient(135deg, #B02030, #E63946); }
.kpi-icon    { font-size: 1.6rem; margin-bottom: 6px; }
.kpi-value   { font-size: 2rem; font-weight: 800; line-height: 1.1; color: white; }
.kpi-label   { font-size: 0.72rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 5px; }

/* ── section header ── */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: var(--dxc-dark);
    border-left: 4px solid var(--dxc-purple);
    padding-left: 10px;
    margin: 1.6rem 0 0.9rem;
}

/* ── pending employee cards ── */
.pending-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 6px;
}
.pending-chip {
    background: white;
    border: 1px solid var(--border);
    border-left: 4px solid var(--amber);
    border-radius: 8px;
    padding: 10px 14px;
    min-width: 190px;
    box-shadow: 0 1px 4px rgba(112,47,138,0.08);
}
.pending-chip-name { font-weight: 700; font-size: 0.88rem; color: var(--text); }
.pending-chip-role { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }
.pending-chip-since { font-size: 0.72rem; color: var(--dxc-teal2); margin-top: 4px; font-weight: 600; }

/* ── page header ── */
.page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--dxc-dark);
    margin-bottom: 0.2rem;
}
.page-sub {
    font-size: 0.9rem;
    color: var(--muted);
    margin-bottom: 1.4rem;
}

/* ── survey card ── */
.survey-card {
    background: var(--card);
    border-radius: 12px;
    padding: 22px 24px;
    border-left: 4px solid var(--dxc-purple);
    box-shadow: 0 2px 10px rgba(112,47,138,0.07);
    margin-bottom: 1rem;
}

hr.divider {
    border: none;
    border-top: 1px solid var(--border);
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
        <div style='padding:20px 4px 28px;'>
          <div style='font-size:0.65rem;font-weight:700;letter-spacing:0.18em;color:rgba(255,255,255,0.5);text-transform:uppercase;margin-bottom:6px;'>DXC Technology</div>
          <div style='font-size:1.2rem;font-weight:800;color:#FFFFFF;line-height:1.2;'>People<br>Analytics</div>
          <div style='font-size:0.75rem;color:rgba(255,255,255,0.6);margin-top:6px;'>Bench Engagement Tracker</div>
          <div style='height:1px;background:rgba(255,255,255,0.12);margin-top:18px;'></div>
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
        <div style='height:1px;background:rgba(255,255,255,0.12);margin:16px 0 10px;'></div>
        <div style='font-size:0.72rem;color:rgba(255,255,255,0.45);padding-bottom:8px;'>
            Week {week} &nbsp;·&nbsp; {year}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── page: dashboard ───────────────────────────────────────────────────────────

def page_dashboard():
    week, year = current_week()

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

    score_lbl, score_colour = score_label(avg_score)
    today_str = datetime.date.today().strftime("%d %b %Y")

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="hero-banner">
          <div class="hero-title">Bench Engagement Dashboard</div>
          <div class="hero-sub">Real-time visibility into bench employee satisfaction &amp; readiness</div>
          <div class="hero-week">Week {week} &nbsp;·&nbsp; {today_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI strip ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "kpi-purple", "👥", total,             "Bench Headcount"),
        (c2, "kpi-teal",   "📋", f"{pct}%",         "Survey Completion"),
        (c3, "kpi-green",  "⭐", f"{avg_score:.1f}/5", "Avg Engagement"),
        (c4, "kpi-red",    "⚠️", at_risk,            "At-Risk Employees"),
    ]
    for col, cls, icon, val, lbl in kpis:
        col.markdown(
            f"""<div class="kpi-card {cls}">
                  <div class="kpi-icon">{icon}</div>
                  <div class="kpi-value">{val}</div>
                  <div class="kpi-label">{lbl}</div>
                </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Completion donut  +  Engagement gauge ─────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-header">Survey Completion — Week {}</div>'.format(week), unsafe_allow_html=True)
        donut = go.Figure(go.Pie(
            values=[submitted_count, max(total - submitted_count, 0)],
            labels=["Submitted", "Pending"],
            hole=0.68,
            marker_colors=["#702F8A", "#E8D5F5"],
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        donut.update_layout(
            showlegend=True,
            legend=dict(orientation="h", x=0.2, y=-0.05),
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="white",
            annotations=[dict(
                text=f"<b>{pct}%</b><br><span style='font-size:11px'>complete</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=22, color="#3C1053"),
                align="center",
            )],
            height=280,
        )
        st.plotly_chart(donut, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">Avg Engagement Score</div>', unsafe_allow_html=True)
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_score,
            number={"suffix": " / 5", "font": {"size": 28, "color": "#3C1053"}},
            delta={"reference": 3.5, "increasing": {"color": "#00C897"}, "decreasing": {"color": "#E63946"}},
            gauge={
                "axis": {"range": [0, 5], "tickwidth": 1, "tickcolor": "#6B6B6B"},
                "bar": {"color": "#702F8A", "thickness": 0.28},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 3],   "color": "#FFE5E7"},
                    {"range": [3, 4],   "color": "#FFF3CD"},
                    {"range": [4, 5],   "color": "#D4F5EC"},
                ],
                "threshold": {
                    "line": {"color": "#E63946", "width": 2},
                    "thickness": 0.75,
                    "value": 3,
                },
            },
            title={"text": f"<b style='color:{score_colour}'>{score_lbl} Engagement</b>", "font": {"size": 14}},
        ))
        gauge.update_layout(
            paper_bgcolor="white",
            margin=dict(l=30, r=30, t=30, b=10),
            height=280,
        )
        st.plotly_chart(gauge, use_container_width=True)

    # ── Pending submissions ────────────────────────────────────────────────────
    pending = employees[~employees["id"].isin(submitted_ids)]
    st.markdown('<div class="section-header">Pending Submissions This Week</div>', unsafe_allow_html=True)

    if pending.empty:
        st.success("All bench employees have submitted their survey this week!")
    else:
        chips_html = '<div class="pending-grid">'
        for _, row in pending.iterrows():
            chips_html += (
                f'<div class="pending-chip">'
                f'  <div class="pending-chip-name">{row["name"]}</div>'
                f'  <div class="pending-chip-role">{row["role"]}</div>'
                f'  <div class="pending-chip-since">On bench since {row["bench_since"]}</div>'
                f'</div>'
            )
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)

    # ── Engagement bar chart ───────────────────────────────────────────────────
    if not week_df.empty and "score" in week_df.columns:
        st.markdown('<div class="section-header">Engagement Scores — Current Week</div>', unsafe_allow_html=True)
        sorted_df = week_df.sort_values("score").copy()
        sorted_df["colour"] = sorted_df["score"].apply(
            lambda s: "#00C897" if s >= 4 else ("#FF8C00" if s >= 3 else "#E63946")
        )
        fig = go.Figure(go.Bar(
            x=sorted_df["score"],
            y=sorted_df["employee_name"],
            orientation="h",
            marker_color=sorted_df["colour"],
            text=sorted_df["score"].apply(lambda s: f"{s:.1f}"),
            textposition="outside",
            hovertemplate="%{y}: %{x:.2f}<extra></extra>",
        ))
        fig.add_vline(x=3, line_dash="dash", line_color="#E63946",
                      annotation_text="At-risk (3.0)", annotation_font_color="#E63946")
        fig.update_layout(
            margin=dict(l=0, r=60, t=10, b=0),
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis=dict(range=[0, 5.5], gridcolor="#F0E6F8", title="Engagement Score"),
            yaxis=dict(gridcolor="#F0E6F8"),
            height=max(320, len(week_df) * 38),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Week-on-week trend ────────────────────────────────────────────────────
    if not responses.empty:
        trend = responses.copy()
        trend["score"] = trend.apply(engagement_score, axis=1)
        trend["week_label"] = "W" + trend["week"].astype(int).astype(str) + " '" + (trend["year"].astype(int) % 100).astype(str)
        agg = trend.groupby("week_label")["score"].mean().reset_index().rename(columns={"score": "avg_score"})

        if len(agg) >= 2:
            st.markdown('<div class="section-header">Week-on-Week Engagement Trend</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_hrect(y0=0, y1=3, fillcolor="#E63946", opacity=0.05, line_width=0, annotation_text="At-risk zone", annotation_position="top left", annotation_font_color="#E63946", annotation_font_size=11)
            fig2.add_hrect(y0=4, y1=5.2, fillcolor="#00C897", opacity=0.05, line_width=0)
            fig2.add_trace(go.Scatter(
                x=agg["week_label"],
                y=agg["avg_score"],
                mode="lines+markers+text",
                line=dict(color="#702F8A", width=3),
                marker=dict(color="#702F8A", size=9, line=dict(color="white", width=2)),
                text=agg["avg_score"].round(2).astype(str),
                textposition="top center",
                textfont=dict(color="#3C1053", size=11),
                fill="tozeroy",
                fillcolor="rgba(112,47,138,0.07)",
                hovertemplate="Week %{x}: %{y:.2f}<extra></extra>",
            ))
            fig2.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="white",
                plot_bgcolor="white",
                yaxis=dict(range=[0, 5.4], gridcolor="#F0E6F8", title="Avg Score"),
                xaxis=dict(gridcolor="#F0E6F8"),
                height=300,
            )
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
            fillcolor="rgba(112,47,138,0.18)",
            line=dict(color="#702F8A", width=2),
            marker=dict(color="#702F8A", size=7),
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
                color_discrete_sequence=["#00C897", "#FF8C00", "#E63946"],
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
                color_discrete_sequence=["#702F8A"],
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
