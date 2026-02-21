import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Lab Characterization Dashboard", layout="wide")

DATA_FILE = "daily_progress.json"

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

# -----------------------------
# LOAD / SAVE FUNCTIONS
# -----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"start_date": None, "daily_progress": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data_store = load_data()
today = str(date.today())

# -----------------------------
# START DATE SETUP
# -----------------------------
st.title("Lab Characterization Progress Dashboard")

if data_store["start_date"] is None:
    if st.button("Start Characterization Today"):
        data_store["start_date"] = today
        save_data(data_store)
        st.rerun()
else:
    st.info(f"Characterization started on: {data_store['start_date']}")

st.divider()

# -----------------------------
# CHECKBOX MATRIX
# -----------------------------
data = {}

for test, minutes in tests.items():
    cols = st.columns(len(devices))
    data[test] = {}

    for i, device in enumerate(devices):
        key = f"{test}_{device}"
        checked = cols[i].checkbox(device, key=key)
        data[test][device] = checked

# -----------------------------
# CALCULATE PROGRESS
# -----------------------------
total_minutes = sum(tests.values()) * len(devices)

completed_minutes = 0
for test, minutes in tests.items():
    for device in devices:
        if data[test][device]:
            completed_minutes += minutes

progress_percent = (completed_minutes / total_minutes) * 100

# Save today's cumulative progress
if data_store["start_date"] is not None:
    data_store["daily_progress"][today] = progress_percent
    save_data(data_store)

# -----------------------------
# OVERALL STATUS
# -----------------------------
st.subheader("Overall Completion")

st.progress(progress_percent / 100)
st.metric("Completion %", f"{progress_percent:.2f}%")

# -----------------------------
# COMPLETION POPUP
# -----------------------------
if progress_percent >= 100:
    st.success("🎉 Full Characterization Completed Successfully!")

# -----------------------------
# LINE CHART (DATE vs %)
# -----------------------------
st.subheader("Progress Trend")

if data_store["daily_progress"]:
    df = pd.DataFrame(
        list(data_store["daily_progress"].items()),
        columns=["Date", "Completion %"]
    )
    df = df.sort_values("Date")
    df.set_index("Date", inplace=True)

    st.line_chart(df)
