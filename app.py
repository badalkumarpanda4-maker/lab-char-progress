import streamlit as st

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Lab Characterization Dashboard",
    layout="wide",
)

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
st.title("Lab Characterization Progress Dashboard")

st.markdown("Track completion status for each test and DUT.")

st.divider()

# ----------------------------
# CHECKBOX MATRIX
# ----------------------------
st.subheader("Test Completion Matrix")

data = {}

for test, minutes in tests.items():
    st.markdown(f"### {test} ({minutes} min per DUT)")
    cols = st.columns(len(devices))
    data[test] = {}

    for i, device in enumerate(devices):
        key = f"{test}_{device}"
        checked = cols[i].checkbox(device, key=key)
        data[test][device] = checked

# ----------------------------
# CALCULATIONS
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
# DASHBOARD METRICS
# ----------------------------
st.divider()

st.subheader("Overall Project Status")

st.progress(progress_percent / 100)

col1, col2, col3 = st.columns(3)

col1.metric("Total Project Time", format_time(total_minutes))
col2.metric("Completed Time", format_time(completed_minutes))
col3.metric("Remaining Time", format_time(remaining_minutes))

st.markdown(f"### Completion: {progress_percent:.2f}%")
