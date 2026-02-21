import streamlit as st

st.set_page_config(page_title="Lab Progress", layout="wide")

st.title("Lab Characterization Progress Dashboard")

st.write("Your app is working successfully 🎉")

progress = st.slider("Progress %", 0, 100, 0)
st.progress(progress / 100)
