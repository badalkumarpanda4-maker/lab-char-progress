import streamlit as st
import json
import os
import pandas as pd
from datetime import date

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Lab Characterization Dashboard",
    layout="wide",
)

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
# CUSTOM STYLING (UNCHANGED)
# ----------------------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}

.main-title {
    font-size: 26px;
    font-weight: 600;
    color: #e2e8f0;
}

.subtitle {
    font-size: 14px;
    color: #94a3b8;
}

.section-title {
    font-size: 18px;
    font-weight: 500;
    color: #38bdf8;
    margin-top: 25px;
}

.metric-card {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #334155;
    text-align: center;
}

.metric-title {
    font-size: 13px;
    color: #94a3b8;
}

.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATA CONFIGURATION (UNCHANGED)
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
# TITLE (UNCHANGED)
# ----------------------------
st.markdown('<div class="main-title">Lab Characterization Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Track completion status for each test and DUT</div>', unsafe_allow_html=True)

# ----------------------------
# START DATE SECTION
# ----------------------------
if progress_store["start_date"] is None:
    if st.button("Start Characterization Today"):
        progress_store["start_date"] = today
        progress_store["history"][today] = 0
        save_progress(progress_store)
        st.rerun()
else:
    st.markdown(
        f"<div style='color:#94a3b8; font-size:13px;'>Started on: {progress_store['start_date']}</div>",
        unsafe_allow_html=True
    )

st.divider()

# ----------------------------
# CHECKBOX MATRIX (UNCHANGED)
# ----------------------------
st.markdown('<div class="section-title">Test Completion Matrix</div>', unsafe_allow_html=True)

data = {}

for test, minutes in tests.items():
    st.markdown(
        f"**{test}**  \n<span style='font-size:12px; color:#94a3b8'>{minutes} min per DUT</span>",
        unsafe_allow_html=True
    )

    cols = st.columns(len(devices))
    data[test] = {}

    for i, device in enumerate(devices):
        key = f"{test}_{device}"
        checked = cols[i].checkbox(device, key=key)
        data[test][device] = checked

# ----------------------------
# CALCULATIONS (UNCHANGED LOGIC)
# ----------------------------
total_minutes = sum(tests.values()) * len(devices)

completed_minutes = 0
for test, minutes in tests.items():
    for device in devices:
        if data[test][device]:
            completed_minutes += minutes

remaining_minutes = total_minutes - completed_minutes
progress_percent = (completed_minutes / total_minutes) * 100


def format_time(minutes):
    hrs = minutes // 60
    mins = minutes % 60
    return f"{hrs} hr {mins} min"

# ----------------------------
# SAVE DAILY PROGRESS
# ----------------------------
if progress_store["start_date"] is not None:
    progress_store["history"][today] = progress_percent
    save_progress(progress_store)

# ----------------------------
# DASHBOARD METRICS (UNCHANGED DESIGN)
# ----------------------------
st.divider()
st.markdown('<div class="section-title">Overall Project Status</div>', unsafe_allow_html=True)

st.progress(progress_percent / 100)

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Total Project Time</div>
    <div class="metric-value">{format_time(total_minutes)}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Completed Time</div>
    <div class="metric-value">{format_time(completed_minutes)}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Remaining Time</div>
    <div class="metric-value">{format_time(remaining_minutes)}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"<div style='margin-top:15px; font-size:14px; color:#38bdf8;'>Completion: {progress_percent:.2f}%</div>",
    unsafe_allow_html=True
)

# ----------------------------
# COMPLETION POPUP
# ----------------------------
if progress_percent >= 100:
    st.success("🎉 Your Full Characterization is Completed!")

# ----------------------------
# LINE CHART (DATE vs OVERALL %)
# ----------------------------
st.divider()
st.markdown('<div class="section-title">Progress Trend</div>', unsafe_allow_html=True)

if progress_store["history"]:
    df = pd.DataFrame(
        list(progress_store["history"].items()),
        columns=["Date", "Completion %"]
    )

    df = df.sort_values("Date")
    df.set_index("Date", inplace=True)

    st.line_chart(df)
