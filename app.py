import streamlit as st
from auth.login import login_user
from auth.register import register_user
from services.analytics import get_user_logs, delete_study_log
from services.burnout import calculate_burnout
from ml.clustering import cluster_subjects
from services.pdf_export import generate_weekly_report
from db.session import SessionLocal
from db.models import StudyLog, User
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from datetime import timedelta

#  Page Config 
st.set_page_config(
    page_title="StudyVista",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS 
st.markdown(
    """
<style>
/* ===== Google Font Import ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* Ensure Material Icons keep their font */
.material-symbols-rounded, .material-icons, [class^="st-icon"], [class*=" st-icon"] {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}

/* ===== Main Background with Gradient Animation ===== */
.stApp {
    background: linear-gradient(
        -45deg,
        #0A0F1E 0%,
        #111C44 26%,
        #1A1F4D 44%,
        #0B3A5A 68%,
        #052B2F 100%
    );
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ===== Glass Morphism Cards ===== */
.glass-card {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    margin-top: 16px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(31, 38, 135, 0.45);
}

/* ===== Stat Cards ===== */
.stat-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 16px;
    padding: 24px 16px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
    transform: scale(1.05) translateY(-4px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
    border-color: rgba(102, 126, 234, 0.4);
}

.stat-value {
    font-size: 2.5em;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 8px 0;
    line-height: 1.2;
}

.stat-label {
    color: rgba(255,255,255,0.85);
    font-size: 0.95em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-icon {
    font-size: 1.8em;
    margin-bottom: 4px;
}

/* ===== Enhanced Buttons ===== */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 12px 30px;
    font-weight: 600;
    font-size: 15px;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.55);
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.stButton>button:active {
    transform: translateY(0);
}

/* ===== Tab Styling ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    color: white;
    font-weight: 600;
    padding: 10px 20px;
    border: 1px solid rgba(255,255,255,0.12);
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.18);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    border-color: transparent !important;
}

/* ===== Input Fields ===== */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div>select {
    background: rgba(255,255,255,0.1) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 500;
}

.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus {
    border-color: rgba(102, 126, 234, 0.6) !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
}

.stTextInput>div>div>input::placeholder {
    color: rgba(255,255,255,0.45) !important;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Fix sidebar hide symbol color */
[data-testid="collapsedControl"] svg, button[kind="header"] svg {
    color: white !important;
    fill: white !important;
}

/* ===== Metric Cards ===== */
div[data-testid="stMetricValue"] {
    font-size: 1.8em;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ===== DataFrame ===== */
.dataframe {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 12px;
    overflow: hidden;
}

/* ===== Headers ===== */
h1, h2, h3 {
    color: white !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

p, span, label, .stMarkdown {
    color: rgba(255,255,255,0.9);
}

/* ===== Messages ===== */
.stSuccess, .stError, .stWarning, .stInfo {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    border-left: 4px solid;
}

/* ===== Progress Bar ===== */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 8px;
}

/* ===== Achievement Badge ===== */
.achievement-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;
    padding: 8px 18px;
    border-radius: 24px;
    font-weight: 700;
    font-size: 0.9em;
    margin: 5px;
    box-shadow: 0 4px 12px rgba(245, 87, 108, 0.35);
    animation: pulse 2s infinite;
    transition: transform 0.2s ease;
}

.achievement-badge:hover {
    transform: scale(1.08);
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.03); }
}

/* ===== Floating Animation ===== */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
}

.floating {
    animation: float 3s ease-in-out infinite;
}

/* ===== Glow Text ===== */
.glow-text {
    text-shadow: 0 0 20px rgba(102, 126, 234, 0.5),
                 0 0 40px rgba(118, 75, 162, 0.3);
}

/* ===== Section Divider ===== */
.section-header {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
    border-left: 4px solid #667eea;
    padding: 12px 20px;
    border-radius: 0 12px 12px 0;
    margin: 20px 0 16px 0;
}

/* ===== Delete Button Override ===== */
button[kind="primary"] {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    color: white !important;
    border: none !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5) !important;
}

/* ===== Burnout Gauge ===== */
.burnout-low { color: #22c55e; }
.burnout-moderate { color: #f59e0b; }
.burnout-high { color: #ef4444; }

/* ===== Scrollbar ===== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.4);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(102, 126, 234, 0.6); }
</style>
""",
    unsafe_allow_html=True,
)


# HELPER FUNCTIONS

def render_plotly_chart(fig, height=400):
    """Apply consistent dark transparent theme to Plotly charts."""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Inter"),
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# SESSION STATE

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None


# AUTHENTICATION FLOW

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div style='text-align: center; padding: 50px 0 30px 0;'>
            <div class='floating'>
                <h1 class='glow-text' style='font-size: 3.5em; margin-bottom: 5px;'>📚 StudyVista</h1>
            </div>
            <p style='font-size: 1.3em; color: rgba(255,255,255,0.85); font-weight: 300; letter-spacing: 3px;'>
                Track  ●  Analyze  ●  Improve
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        auth_tab = st.tabs(["🔑 Login", "📝 Register"])

        with auth_tab[0]:
            login_user()

        with auth_tab[1]:
            register_user()

    st.stop()


# SIDEBAR

with st.sidebar:
    st.markdown(
        f"""
    <div style='display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: rgba(255, 255, 255, 0.05); border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1);'>
        <div style='font-size: 1.4em;'>👤</div>
        <h3 style='margin: 0; font-size: 1.1em; color: white; font-weight: 500;'>{st.session_state.username}</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.update({"logged_in": False, "user_id": None, "username": None})
        st.rerun()

    st.markdown("---")

    # Load user data
    user_id = st.session_state.user_id
    df = get_user_logs(user_id)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])

    # Quick Stats
    st.markdown(
        "<div class='section-header'><b>📊 Quick Stats</b></div>",
        unsafe_allow_html=True,
    )
    if not df.empty:
        total_hours = df["study_hours"].sum()
        total_sessions = len(df)
        avg_focus = df["focus_level"].mean()

        st.metric("Total Hours", f"{total_hours:.1f}h")
        st.metric("Study Sessions", total_sessions)
        st.metric("Avg Focus", f"{avg_focus:.1f}/5")
    else:
        st.caption("No data yet. Start logging!")

    st.markdown("---")

    # Danger Zone
    with st.expander("⚠️ Danger Zone"):
        st.markdown(
            """
            <div style='background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 12px;'>
                <div style='color: #ef4444; font-weight: 600; margin-bottom: 4px; font-size: 0.95em;'>Warning</div>
                <div style='color: rgba(255,255,255,0.8); font-size: 0.85em;'>
                    This action is permanent and will delete all your data. Proceed with caution.
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if st.button("🗑️ Delete Account", type="primary", use_container_width=True):
            session = SessionLocal()
            try:
                uid = st.session_state.user_id
                session.query(StudyLog).filter(StudyLog.user_id == uid).delete()
                session.query(User).filter(User.id == uid).delete()
                session.commit()
                st.success("Account deleted.")
                st.session_state.update({"logged_in": False, "user_id": None, "username": None})
                st.rerun()
            finally:
                session.close()


# MAIN HEADER

st.markdown(
    f"""
<div style='text-align: center; padding: 16px 0 8px 0;'>
    <h1 class='glow-text' style='font-size: 2.5em; margin-bottom: 4px;'>📚 StudyVista</h1>
    <p style='font-size: 1.1em; letter-spacing: 2px; color: rgba(255,255,255,0.7); font-weight: 300;'>
        Track  ●  Analyze  ●  Improve
    </p>
    <p style='font-size: 1.15em; color: rgba(255,255,255,0.9); margin-top: 8px;'>
        Welcome back, <b>{st.session_state.username}</b>! 🎯
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Main Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📊 Overview", "➕ Add Log", "📈 Analytics", "🧠 AI Insights", "🔥 Burnout Monitor", "📅 Planner"]
)


# TAB 1: OVERVIEW DASHBOARD

with tab1:
    if df.empty:
        st.markdown(
            """
        <div class='glass-card' style='text-align: center; padding: 80px 40px;'>
            <div style='font-size: 4em; margin-bottom: 16px;'>🎯</div>
            <h2 style='margin-bottom: 12px;'>Start Your Study Journey!</h2>
            <p style='font-size: 1.15em; color: rgba(255,255,255,0.7); margin-bottom: 24px; line-height: 1.6;'>
                Begin tracking your study sessions to unlock<br>
                powerful insights, analytics, and AI recommendations.
            </p>
            <p style='font-size: 1.05em; color: rgba(255,255,255,0.9);'>
                👉 Head to the <b>"➕ Add Log"</b> tab to get started!
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        # Stat Cards
        total_hours = df["study_hours"].sum()
        total_sessions = len(df)
        avg_focus = df["focus_level"].mean()
        subjects_count = df["subject"].nunique()

        col1, col2, col3, col4 = st.columns(4)

        stats = [
            ("⏱️", "Total Hours", f"{total_hours:.1f}h", col1),
            ("📝", "Sessions", f"{total_sessions}", col2),
            ("🎯", "Avg Focus", f"{avg_focus:.1f}/5", col3),
            ("📚", "Subjects", f"{subjects_count}", col4),
        ]

        for icon, label, value, col in stats:
            with col:
                st.markdown(
                    f"""
                <div class='stat-card'>
                    <div class='stat-icon'>{icon}</div>
                    <div class='stat-value'>{value}</div>
                    <div class='stat-label'>{label}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Row
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                "<div class='section-header'><b>📈 Study Productivity Trend</b></div>",
                unsafe_allow_html=True,
            )
            df_sorted = df.sort_values("date")
            df_sorted["productivity"] = df_sorted["study_hours"] * df_sorted["focus_level"]

            fig = px.area(
                df_sorted,
                x="date",
                y="productivity",
                labels={"productivity": "Productivity Score", "date": "Date"},
            )
            fig.update_traces(
                fillcolor="rgba(102, 126, 234, 0.25)",
                line=dict(color="rgb(102, 126, 234)", width=2.5),
            )
            render_plotly_chart(fig, height=350)

        with col2:
            st.markdown(
                "<div class='section-header'><b>🎯 Subject Distribution</b></div>",
                unsafe_allow_html=True,
            )
            subject_hours = df.groupby("subject")["study_hours"].sum().sort_values(ascending=False)

            fig = px.pie(
                values=subject_hours.values,
                names=subject_hours.index,
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(showlegend=False)
            render_plotly_chart(fig, height=350)

        # Achievements
        st.markdown(
            "<div class='section-header'><b>🏆 Achievements Unlocked</b></div>",
            unsafe_allow_html=True,
        )

        achievements = []
        if total_hours >= 10:
            achievements.append("📖 Bookworm (10+ hours)")
        if total_hours >= 50:
            achievements.append("🎯 Study Master (50+ hours)")
        if total_hours >= 100:
            achievements.append("💪 Century Club (100+ hours)")
        if total_sessions >= 10:
            achievements.append("🔄 Getting Started (10+ sessions)")
        if total_sessions >= 30:
            achievements.append("🔥 Consistency King (30+ sessions)")
        if avg_focus >= 4:
            achievements.append("🧠 Focus Champion (4+ avg focus)")
        if subjects_count >= 5:
            achievements.append("📚 Polymath (5+ subjects)")

        if achievements:
            html = "".join([f"<span class='achievement-badge'>{a}</span>" for a in achievements])
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("Keep studying to unlock achievements! 🎯 Start with 10 hours of study time.")


# TAB 2: ADD STUDY LOG

with tab2:
    st.markdown(
        "<div class='section-header'><b>✏️ Log Your Study Session</b></div>",
        unsafe_allow_html=True,
    )

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("📅 Date", datetime.date.today(), key="add_date")
            subject = st.text_input(
                "📖 Subject", placeholder="e.g., Mathematics, Physics", key="add_subject"
            )
            hours = st.number_input("⏱️ Hours Studied", 0.0, 24.0, 1.0, 0.5, key="add_hours")

        with col2:
            focus = st.slider(
                "🎯 Focus Level",
                1,
                5,
                3,
                key="add_focus",
                help="1 = Very Distracted, 5 = Highly Focused",
            )
            notes = st.text_area(
                "📝 Notes (Optional)", placeholder="What did you learn today?", key="add_notes"
            )

        if st.button("✅ Add Study Log", use_container_width=True, key="btn_add_log"):
            if not subject.strip():
                st.error("Please enter a subject name!")
            else:
                session = SessionLocal()
                try:
                    log = StudyLog(
                        user_id=user_id,
                        date=date,
                        subject=subject.strip(),
                        study_hours=hours,
                        focus_level=focus,
                        notes=notes.strip(),
                    )
                    session.add(log)
                    session.commit()
                    st.balloons()
                    st.success("🎉 Study log added successfully!")
                    st.rerun()
                finally:
                    session.close()

    # Recent Logs with Delete
    if not df.empty:
        st.markdown(
            "<div class='section-header'><b>📜 Recent Study Logs</b></div>",
            unsafe_allow_html=True,
        )

        recent_df = df.sort_values("date", ascending=False).head(10)

        # Display table
        display_df = recent_df[["date", "subject", "study_hours", "focus_level", "notes"]].copy()
        display_df.columns = ["Date", "Subject", "Hours", "Focus", "Notes"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Delete functionality
        with st.expander("🗑️ Delete a Study Log"):
            log_options = {
                f"{row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else row['date']} | {row['subject']} | {row['study_hours']}h": row["id"]
                for _, row in recent_df.iterrows()
            }
            if log_options:
                selected = st.selectbox("Select a log to delete:", list(log_options.keys()))
                if st.button("🗑️ Delete Selected Log", key="btn_delete_log"):
                    if delete_study_log(log_options[selected]):
                        st.success("Log deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete log.")

        # CSV Export
        st.markdown("<br>", unsafe_allow_html=True)
        csv_data = df.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Export All Data as CSV",
            data=csv_data,
            file_name=f"studyvista_{st.session_state.username}_data.csv",
            mime="text/csv",
            use_container_width=True,
        )


# TAB 3: ADVANCED ANALYTICS

with tab3:
    if df.empty:
        st.markdown(
            """
        <div class='glass-card' style='text-align: center; padding: 60px;'>
            <div style='font-size: 3em; margin-bottom: 12px;'>📊</div>
            <h3>No Data Available</h3>
            <p style='color: rgba(255,255,255,0.7);'>Add some study logs first to see analytics!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        # Subject Analysis
        st.markdown(
            "<div class='section-header'><b>📊 Study Hours by Subject</b></div>",
            unsafe_allow_html=True,
        )

        subject_analysis = (
            df.groupby("subject")
            .agg({"study_hours": ["sum", "mean", "count"], "focus_level": "mean"})
            .round(2)
        )
        subject_analysis.columns = ["Total Hours", "Avg Hours/Session", "Sessions", "Avg Focus"]
        subject_analysis = subject_analysis.sort_values("Total Hours", ascending=False)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=subject_analysis.index,
                y=subject_analysis["Total Hours"],
                name="Total Hours",
                marker=dict(
                    color=subject_analysis["Total Hours"],
                    colorscale=[[0, "#667eea"], [1, "#764ba2"]],
                ),
                text=subject_analysis["Total Hours"].apply(lambda x: f"{x:.1f}h"),
                textposition="outside",
            )
        )
        render_plotly_chart(fig, height=400)
        st.dataframe(subject_analysis, use_container_width=True)

        # Weekly Pattern
        st.markdown(
            "<div class='section-header'><b>📅 Weekly Study Pattern</b></div>",
            unsafe_allow_html=True,
        )

        df_copy = df.copy()
        df_copy["weekday"] = pd.to_datetime(df_copy["date"]).dt.day_name()
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly = df_copy.groupby("weekday")["study_hours"].sum().reindex(weekday_order, fill_value=0)

        fig = px.bar(
            x=weekly.index,
            y=weekly.values,
            labels={"x": "Day", "y": "Total Hours"},
            color=weekly.values,
            color_continuous_scale="Viridis",
        )
        fig.update_layout(showlegend=False)
        fig.update_traces(text=weekly.values.round(1), textposition="outside")
        render_plotly_chart(fig, height=400)

        # Focus vs Hours + Streak 
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                "<div class='section-header'><b>🎯 Focus vs Study Hours</b></div>",
                unsafe_allow_html=True,
            )
            fig = px.scatter(
                df,
                x="study_hours",
                y="focus_level",
                color="subject",
                size="study_hours",
                hover_data=["date"],
                labels={"study_hours": "Study Hours", "focus_level": "Focus Level"},
            )
            render_plotly_chart(fig, height=380)

        with col2:
            st.markdown(
                "<div class='section-header'><b>📈 Study Streak</b></div>",
                unsafe_allow_html=True,
            )

            # Streak calculation (now correctly inside col2)
            dates = df.sort_values("date")["date"]
            current_streak = 0
            max_streak = 0
            temp_streak = 1

            for i in range(1, len(dates)):
                if (dates.iloc[i] - dates.iloc[i - 1]).days == 1:
                    temp_streak += 1
                else:
                    max_streak = max(max_streak, temp_streak)
                    temp_streak = 1
            max_streak = max(max_streak, temp_streak)

            if len(dates) > 0:
                last_date = dates.iloc[-1]
                if (pd.Timestamp(datetime.date.today()) - last_date).days <= 1:
                    current_streak = 1
                    for i in range(len(dates) - 2, -1, -1):
                        if (dates.iloc[i + 1] - dates.iloc[i]).days == 1:
                            current_streak += 1
                        else:
                            break

            st.metric("Current Streak 🔥", f"{current_streak} days")
            st.metric("Best Streak 🏆", f"{max_streak} days")

            progress = min(current_streak / 30, 1.0) if current_streak > 0 else 0
            st.progress(progress)
            st.caption(f"Goal: 30-day streak ({current_streak}/30)")

            # Streak motivation
            if current_streak >= 30:
                st.success("🎉 You've hit your 30-day streak goal!")
            elif current_streak >= 7:
                st.info(f"🔥 Great momentum! {30 - current_streak} days to your goal!")
            elif current_streak > 0:
                st.info(f"💪 Keep going! Study tomorrow to extend your streak.")
            else:
                st.warning("📅 Study today to start a new streak!")


# TAB 4: AI INSIGHTS

with tab4:
    if df.empty:
        st.markdown(
            """
        <div class='glass-card' style='text-align: center; padding: 60px;'>
            <div style='font-size: 3em; margin-bottom: 12px;'>🧠</div>
            <h3>No Data for AI Analysis</h3>
            <p style='color: rgba(255,255,255,0.7);'>Add study data to get AI-powered insights!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        # Subject Clustering
        st.markdown(
            "<div class='section-header'><b>🧠 AI-Powered Subject Clustering</b></div>",
            unsafe_allow_html=True,
        )
        st.caption("Subjects are grouped based on study hours and focus level patterns using K-Means clustering")

        clustered = cluster_subjects(df)
        if not clustered.empty and "cluster" in clustered.columns:
            fig = px.scatter(
                clustered,
                x="study_hours",
                y="focus_level",
                color="category" if "category" in clustered.columns else "cluster",
                text="subject",
                size="study_hours",
                labels={"study_hours": "Avg Study Hours", "focus_level": "Avg Focus Level"},
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="white")))
            render_plotly_chart(fig, height=450)

            # Display with friendly column names
            display_cols = ["subject", "study_hours", "focus_level", "category"]
            available_cols = [c for c in display_cols if c in clustered.columns]
            st.dataframe(clustered[available_cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(clustered, use_container_width=True, hide_index=True)

        # Performance Insights
        st.markdown(
            "<div class='section-header'><b>💡 Performance Insights</b></div>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        subject_perf = df.groupby("subject").agg({"study_hours": "sum", "focus_level": "mean"})
        subject_perf["score"] = subject_perf["study_hours"] * subject_perf["focus_level"]

        with col1:
            best_subject = subject_perf["score"].idxmax()
            st.markdown(
                f"""
            <div class='glass-card' style='border-left: 4px solid #22c55e;'>
                <h4>🌟 Top Performing Subject</h4>
                <h3 style='color: #22c55e !important;'>{best_subject}</h3>
                <p>📊 Total Hours: <b>{subject_perf.loc[best_subject, 'study_hours']:.1f}h</b></p>
                <p>🎯 Avg Focus: <b>{subject_perf.loc[best_subject, 'focus_level']:.1f}/5</b></p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            weak_subject = subject_perf["score"].idxmin()
            st.markdown(
                f"""
            <div class='glass-card' style='border-left: 4px solid #f59e0b;'>
                <h4>⚠️ Needs Attention</h4>
                <h3 style='color: #f59e0b !important;'>{weak_subject}</h3>
                <p>📊 Total Hours: <b>{subject_perf.loc[weak_subject, 'study_hours']:.1f}h</b></p>
                <p>🎯 Avg Focus: <b>{subject_perf.loc[weak_subject, 'focus_level']:.1f}/5</b></p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Recommendations 
        st.markdown(
            "<div class='section-header'><b>🎯 Personalized Recommendations</b></div>",
            unsafe_allow_html=True,
        )

        avg_hours_per_day = df["study_hours"].sum() / max(len(df["date"].unique()), 1)
        avg_focus_overall = df["focus_level"].mean()

        recommendations = []

        if avg_hours_per_day < 2:
            recommendations.append(("⏰", "Try to increase daily study time to at least 2–3 hours for better progress."))
        elif avg_hours_per_day > 8:
            recommendations.append(("⚠️", "Consider reducing study hours to prevent burnout. Quality > quantity."))

        if avg_focus_overall < 3:
            recommendations.append(("🧘", "Practice Pomodoro technique or meditation to improve focus levels."))

        subject_variance = df.groupby("subject")["study_hours"].sum().std()
        if subject_variance > df["study_hours"].mean() * 2:
            recommendations.append(("📚", "Balance your study time more evenly across subjects."))

        recent_week = df[df["date"] >= pd.Timestamp(datetime.date.today() - timedelta(days=7))]
        if len(recent_week) < 4:
            recommendations.append(("📅", "Aim for at least 4–5 study sessions per week for consistency."))

        if avg_focus_overall >= 4 and avg_hours_per_day >= 2:
            recommendations.append(("🎉", "Excellent work! You're maintaining great study habits!"))

        if recommendations:
            for icon, rec in recommendations:
                st.markdown(
                    f"""
                <div class='glass-card' style='padding: 12px 20px; margin-top: 8px;'>
                    <span style='font-size: 1.2em;'>{icon}</span> &nbsp; {rec}
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("🎉 Great job! You're maintaining excellent study habits!")


# TAB 5: BURNOUT MONITOR

with tab5:
    st.markdown(
        "<div class='section-header'><b>🔥 Burnout Risk Analysis</b></div>",
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Add study data to monitor burnout risk.")
    else:
        score = calculate_burnout(df)

        # Determine risk level and color
        if score < 4:
            risk_level = "Low"
            risk_color = "#22c55e"
            risk_emoji = "😊"
            risk_msg = "You're in a healthy zone! Keep up the balanced approach."
        elif score < 7:
            risk_level = "Moderate"
            risk_color = "#f59e0b"
            risk_emoji = "⚠️"
            risk_msg = "Take regular breaks and monitor your focus levels. Consider rest days."
        else:
            risk_level = "High"
            risk_color = "#ef4444"
            risk_emoji = "🔥"
            risk_msg = "Consider reducing study load significantly. Prioritize rest and recovery."

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.markdown(
                f"""
            <div class='stat-card'>
                <div class='stat-label'>Burnout Score</div>
                <div class='stat-value' style='background: {risk_color}; -webkit-background-clip: text;'>{score:.1f}/10</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class='glass-card' style='border-left: 4px solid {risk_color};'>
                <h3>{risk_emoji} {risk_level} Risk of Burnout</h3>
                <p style='color: rgba(255,255,255,0.8);'>{risk_msg}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            avg_h = df["study_hours"].mean()
            st.markdown(
                f"""
            <div class='stat-card'>
                <div class='stat-label'>Avg Daily Hours</div>
                <div class='stat-value'>{avg_h:.1f}h</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Progress bar with correct color
        progress = min(score / 10, 1.0)
        st.markdown(
            f"""
        <style>
        div[data-testid="stProgress"] > div > div {{
            background-color: {risk_color} !important;
        }}
        </style>
        """,
            unsafe_allow_html=True,
        )
        st.progress(progress)

        # Burnout factors breakdown
        st.markdown(
            "<div class='section-header'><b>📋 Contributing Factors</b></div>",
            unsafe_allow_html=True,
        )

        factors = []
        avg_hours = df["study_hours"].mean()
        if avg_hours > 6:
            factors.append(("🕐 High Study Hours", f"Averaging {avg_hours:.1f}h per session", "high"))
        elif avg_hours > 4:
            factors.append(("🕐 Moderate Study Hours", f"Averaging {avg_hours:.1f}h per session", "moderate"))
        else:
            factors.append(("🕐 Healthy Study Hours", f"Averaging {avg_hours:.1f}h per session", "low"))

        focus_std = df["focus_level"].std()
        if focus_std > 1.5:
            factors.append(("🎯 Inconsistent Focus", f"Focus variability: {focus_std:.1f}", "high"))
        elif focus_std > 1.0:
            factors.append(("🎯 Some Focus Variation", f"Focus variability: {focus_std:.1f}", "moderate"))
        else:
            factors.append(("🎯 Consistent Focus", f"Focus variability: {focus_std:.1f}", "low"))

        for label, detail, level in factors:
            color = {"low": "#22c55e", "moderate": "#f59e0b", "high": "#ef4444"}[level]
            st.markdown(
                f"""
            <div class='glass-card' style='padding: 12px 20px; margin-top: 6px; border-left: 3px solid {color};'>
                <b>{label}</b> — {detail}
            </div>
            """,
                unsafe_allow_html=True,
            )


# TAB 6: PLANNER & WEEKLY REPORT

with tab6:
    st.markdown(
        "<div class='section-header'><b>📅 Weekly Study Planner & Report</b></div>",
        unsafe_allow_html=True,
    )

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        start_date = st.date_input("Start Date", datetime.date.today() - timedelta(days=7), key="plan_start")
    with pcol2:
        end_date = st.date_input("End Date", datetime.date.today(), key="plan_end")

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        week_data = df[(df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))]
    else:
        week_data = pd.DataFrame()

    if st.button("📄 Generate Weekly Report", use_container_width=True, key="btn_gen_report"):
        if week_data.empty:
            st.warning("⚠️ No study logs found for the selected period.")
        else:
            pdf_bytes = generate_weekly_report(st.session_state.username, week_data)
            st.session_state.weekly_pdf = pdf_bytes
            st.success("✅ Weekly report generated successfully!")

    if "weekly_pdf" in st.session_state and st.session_state.weekly_pdf:
        st.download_button(
            label="📥 Download Weekly Report (PDF)",
            data=st.session_state.weekly_pdf,
            file_name=f"{st.session_state.username}_weekly_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # Weekly Chart
    if not week_data.empty:
        st.markdown(
            "<div class='section-header'><b>📊 Weekly Hours Distribution</b></div>",
            unsafe_allow_html=True,
        )
        weekly_subjects = week_data.groupby("subject")["study_hours"].sum().sort_values(ascending=False)

        fig = px.bar(
            x=weekly_subjects.index,
            y=weekly_subjects.values,
            labels={"x": "Subject", "y": "Hours"},
            color=weekly_subjects.values,
            color_continuous_scale=[[0, "#667eea"], [1, "#764ba2"]],
        )
        fig.update_layout(showlegend=False)
        fig.update_traces(text=weekly_subjects.values.round(1), textposition="outside")
        render_plotly_chart(fig, height=400)

    # AI Goal Suggestions
    if not df.empty:
        st.markdown(
            "<div class='section-header'><b>🤖 AI-Powered Study Goal Suggestion</b></div>",
            unsafe_allow_html=True,
        )
        st.caption("Recommended daily study targets for next week based on your past performance")

        subject_avg = df.groupby("subject")["study_hours"].mean()
        total_hours_by_subject = df.groupby("subject")["study_hours"].sum()
        max_hours = total_hours_by_subject.max()
        attention_subjects = total_hours_by_subject[total_hours_by_subject < max_hours * 0.5].index.tolist()

        goal_recommendations = []
        for subject in subject_avg.index:
            avg_hrs = subject_avg[subject]
            if subject in attention_subjects:
                recommended = round(avg_hrs * 1.3, 1)
                status = "📈 Boost"
            else:
                recommended = round(avg_hrs, 1)
                status = "✅ Maintain"

            goal_recommendations.append(
                {"Subject": subject, "Daily Target (hrs)": recommended, "Strategy": status}
            )

        goal_df = pd.DataFrame(goal_recommendations).sort_values("Daily Target (hrs)", ascending=False)
        st.dataframe(goal_df, use_container_width=True, hide_index=True)

        total_suggested = goal_df["Daily Target (hrs)"].sum()
        if total_suggested > 10:
            st.warning(f"💡 Total recommended: {total_suggested:.1f} hrs/day — consider prioritizing your top subjects.")
        else:
            st.info(f"💡 Total recommended study time per day: {total_suggested:.1f} hrs")
