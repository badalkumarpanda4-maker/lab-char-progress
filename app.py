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
# ✅ OVERALL PROJECT STATUS (NOW AT TOP)
# ----------------------------
st.divider()
st.subheader("Overall Project Status")
st.progress(progress_percent / 100)
st.markdown(f"**Completion: {progress_percent:.2f}%**")

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

        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y(
                "Completion %:Q",
                title="Completion %",
                scale=alt.Scale(domain=[0, 100])
            )
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
