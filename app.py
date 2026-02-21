import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Lab Characterization Dashboard",
    layout="wide",
)

# -----------------------------
# CUSTOM STYLING
# -----------------------------
st.markdown("""
    <style>
        .main-title {
            font-size: 34px;
            font-weight: 700;
            color: #1f2937;
        }
        .section-title {
            font-size: 22px;
            font-weight: 600;
            margin-top: 25px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Lab Characterization Dashboard</div>', unsafe_allow_html=True)

# -----------------------------
# DATA CONFIGURATION
# -----------------------------
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

st.markdown('<div class="section-title">Test Completion Matrix</div>', unsafe_allow_html=True)

data = {}
progress_per_test = []

for test, minutes in tests.items():
    cols = st.columns(len(devices))
    data[test] = {}
    completed_count = 0

    for i, device in enumerate(devices):
        key = f"{test}_{device}"
        checked = cols[i].checkbox(device, key=key)
        data[test][device] = checked
        if checked:
            completed_count += 1

    completion_percent = (completed_count / len(devices)) * 100
    progress_per_test.append(completion_percent)

# -----------------------------
# CALCULATIONS
# -----------------------------
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

# -----------------------------
# KPI SECTION
# -----------------------------
st.markdown('<div class="section-title">Overall Project Status</div>', unsafe_allow_html=True)

st.progress(progress_percent / 100)

col1, col2, col3 = st.columns(3)
col1.metric("Total Project Time", format_time(total_minutes))
col2.metric("Completed Time", format_time(completed_minutes))
col3.metric("Remaining Time", format_time(remaining_minutes))

st.markdown(f"### Completion: {progress_percent:.2f}%")

# -----------------------------
# LINE CHART (Progress per Test)
# -----------------------------
st.markdown('<div class="section-title">Progress Trend by Test</div>', unsafe_allow_html=True)

chart_df = pd.DataFrame({
    "Test": list(tests.keys()),
    "Completion %": progress_per_test
})

st.line_chart(chart_df.set_index("Test"))
