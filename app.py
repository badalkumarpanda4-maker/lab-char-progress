import streamlit as st
import sqlite3

# =========================
# CONFIGURATION
# =========================

tests = {
    "PWM_SW_DELAY": 45,
    "DEAD_TIME": 30,
    "TRISTATE_DELAY": 45,
    "SW_MIN_ON": 30,
    "SW_MIN_OFF": 30,
    "CS_ACCURACY": 75,
    "OCP_POS & NEG": 40,
    "HIGH_DUTY": 30,
    "EFFICIENCY": 420,
    "SYNC_HIZ_DELAY": 30,
    "CS_COMMON_MODE": 45
}

devices = ["DUT1", "DUT2", "DUT3", "DUT4", "DUT5"]

DB_NAME = "lab_progress.db"

# =========================
# DATABASE CONNECTION
# =========================

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS progress (
    test TEXT,
    device TEXT,
    status INTEGER,
    PRIMARY KEY (test, device)
)
""")

# Initialize entries if not present
for test in tests:
    for device in devices:
        cursor.execute("""
        INSERT OR IGNORE INTO progress (test, device, status)
        VALUES (?, ?, 0)
        """, (test, device))

conn.commit()

# =========================
# UI
# =========================

st.set_page_config(page_title="Lab Characterization Dashboard", layout="wide")

st.title("Lab Characterization Progress Dashboard")

st.subheader("Test Completion Matrix")

for test, time_value in tests.items():
    st.markdown(f"### {test} ({time_value} min per DUT)")
    cols = st.columns(len(devices))

    for i, device in enumerate(devices):
        cursor.execute(
            "SELECT status FROM progress WHERE test=? AND device=?",
            (test, device)
        )
        current_status = cursor.fetchone()[0]

        new_status = cols[i].checkbox(
            device,
            value=bool(current_status),
            key=f"{test}_{device}"
        )

        if new_status != bool(current_status):
            cursor.execute(
                "UPDATE progress SET status=? WHERE test=? AND device=?",
                (int(new_status), test, device)
            )
            conn.commit()

# =========================
# CALCULATIONS
# =========================

total_project_minutes = sum(tests.values()) * len(devices)

completed_minutes = 0

cursor.execute("SELECT test, device, status FROM progress")
rows = cursor.fetchall()

for test, device, status in rows:
    if status == 1:
        completed_minutes += tests[test]

remaining_minutes = total_project_minutes - completed_minutes
progress_percent = (completed_minutes / total_project_minutes) * 100

def minutes_to_hr_min(minutes):
    hrs = minutes // 60
    mins = minutes % 60
    return f"{hrs} hr {mins} min"

# =========================
# DISPLAY SUMMARY
# =========================

st.divider()

st.subheader("Overall Progress")

st.progress(progress_percent / 100)

col1, col2, col3 = st.columns(3)

col1.metric("Total Project Time", minutes_to_hr_min(total_project_minutes))
col2.metric("Completed Time", minutes_to_hr_min(completed_minutes))
col3.metric("Remaining Time", minutes_to_hr_min(remaining_minutes))

st.markdown(f"### Progress: {progress_percent:.2f} %")

# =========================
# RESET BUTTON
# =========================

if st.button("Reset All Progress"):
    cursor.execute("UPDATE progress SET status=0")
    conn.commit()
    st.rerun()
