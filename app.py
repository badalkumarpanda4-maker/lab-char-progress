import streamlit as st
import json
import os
import pandas as pd
import altair as alt
from datetime import date

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Lab Characterization Dashboard",
    layout="wide",
)

# ----------------------------
# GLASS DARK THEME + STYLING
# ----------------------------
st.markdown("""
<style>
/* Main Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #f1f5f9;
}

/* Section Headers */
h1, h2, h3 {
    color: #38bdf8 !important;
    font-weight: 600;
}

/* Glass Card Effect */
.block-container {
    background: rgba(255,255,255,0.03);
    padding: 2rem;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
}

/* Progress Bar Styling */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #38bdf8, #6366f1);
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 0.5rem 1rem;
}

.stButton button:hover {
    transform: scale(1.03);
    transition: 0.2s ease-in-out;
}

/* KPI Cards */
.kpi-card {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    margin-bottom: 10px;
}
.kpi-card h3 {
    margin: 0;
    color: #38bdf8;
}
.kpi-card h1 {
    margin: 0;
    color: white;
    font-size: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATA STORAGE CONFIG
# ----------------------------
DATA_FILE = "progress_tracking.json"

def load_progress():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"start_date": None, "history": {}}

def save_progress(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

progress_store = load_progress()
today = str(date.today())

# ----------------------------
# DATA CONFIGURATION
# ----------------------------
tests = {
    "PWM_SW_DELAY": 45,
    "DEAD_TIME": 30,
    "TRISTATE_DELAY": 45,
    "SW_MIN_ON": 30,
    "SW_MIN_OFF": 30,
    "CS_ACCURACY": 75,
    "OCP_POS_NEG": 40,
    "HIGH_DUTY": 30,
    "EFFICIENCY": 420,
    "SYNC_HIZ_DELAY": 30,
    "CS_COMMON_MODE": 45,
}

devices = ["DUT1", "DUT2", "DUT3", "DUT4", "DUT5"]

# ----------------------------
# TITLE
# ----------------------------
st.title("Lab Characterization Dashboard")
st.caption("Track completion status for each test and DUT")

# ----------------------------
# START SECTION
# ----------------------------
if progress_store["start_date"] is None:
    if st.button("Start Characterization Today"):
        progress_store["start_date"] = today
        progress_store["history"][today] = 0
        save_progress(progress_store)
        st.rerun()
else:
    st.markdown(f"Started on: **{progress_store['start_date']}**")

# ----------------------------
# CHECKBOX MATRIX DATA COLLECTION
# ----------------------------
data = {}
for test in tests:
    data[test] = {}
    for device in devices:
        key = f"{test}_{device}"
        if key not in st.session_state:
            st.session_state[key] = False

# ----------------------------
# CALCULATIONS (BEFORE DISPLAY)
# ----------------------------
total_minutes = sum(tests.values()) * len(devices)

completed_minutes = 0
for test, minutes in tests.items():
    for device in devices:
        if st.session_state[f"{test}_{device}"]:
            completed_minutes += minutes

remaining_minutes = total_minutes - completed_minutes
progress_percent = (completed_minutes / total_minutes) * 100

# ----------------------------
# SAVE DAILY PROGRESS
# ----------------------------
if progress_store["start_date"] is not None:
    progress_store["history"][today] = progress_percent
    save_progress(progress_store)

# ----------------------------
# ✅ KPI CARDS TOP
# ----------------------------
st.divider()
st.subheader("Overall Project Status")

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col1.markdown(f"""
<div class="kpi-card">
<h3>Total Tests</h3>
<h1>{len(tests)*len(devices)}</h1>
</div>
""", unsafe_allow_html=True)

kpi_col2.markdown(f"""
<div class="kpi-card">
<h3>Completion</h3>
<h1>{progress_percent:.2f}%</h1>
</div>
""", unsafe_allow_html=True)

kpi_col3.markdown(f"""
<div class="kpi-card">
<h3>Remaining Time (min)</h3>
<h1>{remaining_minutes}</h1>
</div>
""", unsafe_allow_html=True)

# Traditional progress bar also kept
st.progress(progress_percent / 100)
if progress_percent >= 100:
    st.success("🎉 Your Full Characterization is Completed!")
st.divider()

# ----------------------------
# CHECKBOX MATRIX + GRAPH SIDE BY SIDE
# ----------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Test Completion Matrix")
    for test, minutes in tests.items():
        st.markdown(f"**{test}**  \n{minutes} min per DUT")
        cols = st.columns(len(devices))
        for i, device in enumerate(devices):
            key = f"{test}_{device}"
            cols[i].checkbox(device, key=key)

with right_col:
    st.subheader("Progress Trend")
    if progress_store["history"]:
        df = pd.DataFrame(
            list(progress_store["history"].items()),
            columns=["Date", "Completion %"]
        )
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # ----------------------------
        # STYLED ALTair CHART
        # ----------------------------
        chart = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(size=80), strokeWidth=4).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Completion %:Q", title="Completion %", scale=alt.Scale(domain=[0,100]))
        ).configure_axis(
            labelColor="white",
            titleColor="white"
        ).configure_view(
            strokeWidth=0
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)

# ----------------------------
# CONTROL BUTTONS
# ----------------------------
st.divider()
col1, col2 = st.columns(2)

if col1.button("Stop Characterization"):
    progress_store["start_date"] = None
    save_progress(progress_store)
    st.rerun()

if col2.button("Clear All"):
    for test in tests:
        for device in devices:
            st.session_state[f"{test}_{device}"] = False
    st.rerun()
