import streamlit as st
import requests
from datetime import date
from enum import IntEnum

API_URL = "http://localhost:8000"

class MoodEnum(IntEnum):
    happy = 0
    sad = 1
    neutral = 2
    angry = 3
    excited = 4

# # Session state for token
# if "token" not in st.session_state:
#     st.session_state.token = None

# Store username/password in session
if "user" not in st.session_state:
    st.session_state.user = None
if "password" not in st.session_state:
    st.session_state.password = None

# Auth headers
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

# Register or Login
def auth_form():
    st.subheader("Login or Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
        if res.status_code == 200:
            # st.session_state.token = res.json()["access_token"]
            st.session_state.user = username
            st.session_state.password = password
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Login failed.")
    if st.button("Register"):
        res = requests.post(f"{API_URL}/auth/register", json={"username": username, "password": password})
        if res.status_code == 200:
            st.success("Registered! Now log in.")
        else:
            st.error("Registration failed.")

# Mood entry form
def mood_entry_form():
    st.subheader("Log a Mood")
    mood_options = {
        "1 - 😔": 0,
        "2 - 🙁": 1,
        "3 - 🙂": 2,
        "4 - 😊": 3,
        "5 - 😄": 4
    }
    mood_str = st.selectbox("How do you feel today? Rate your mood", list(mood_options.keys()))
    description = st.text_area("Describe your mood")
    entry_date = st.date_input("Date", value=date.today())

    if st.button("Submit Mood"):
        mood_int = mood_options[mood_str]
        res = requests.post(
            f"{API_URL}/mood/",
            json={"mood": mood_int, "note": description, "date": entry_date.isoformat()}
        )
        if res.status_code == 200:
            st.success("Mood logged!")
        else:
            st.error(res.json().get("detail", "Failed to log mood."))

# View mood history
def view_moods():
    st.subheader("Mood History")
    res = requests.get(f"{API_URL}/mood/")
    if res.status_code == 200:
        moods = res.json()
        mood_map = {
            0: "1 - 😔",
            1: "2 - 🙁",
            2: "3 - 🙂",
            3: "4 - 😊",
            4: "5 - 😄"
        }
        for m in moods:
            mood_label = mood_map.get(m["mood"], "unknown")
            st.markdown(f"**{m['date']}** — {mood_label}: {m.get('note', '[No description]')}")
    else:
        st.error("Failed to load mood history.")

# Mood stats
def view_stats():
    st.subheader("Mood Stats")
    res = requests.get(f"{API_URL}/stats/")
    if res.status_code == 200:
        stats = res.json()
        st.write(stats)
    else:
        st.error("Failed to fetch stats.")

# Main UI
st.title("📝 Mood Diary")

# if not st.session_state.token:
#     auth_form()
if not st.session_state.user:
    auth_form()
else:
    # st.sidebar.button("Logout", on_click=lambda: st.session_state.pop("token"))
    st.sidebar.write(f"👋 Hello, {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.password = None
        st.rerun()
    
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Log Mood", "View History", "Stats"])
    
    if page == "Log Mood":
        mood_entry_form()
    elif page == "View History":
        view_moods()
    elif page == "Stats":
        view_stats()