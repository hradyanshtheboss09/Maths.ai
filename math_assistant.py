import streamlit as st
import json
import os
import requests
import time

# 1. Page Configuration
st.set_page_config(page_title="Maths.ai Pro - Manan Soni", page_icon="🧠", layout="wide")
# --- HIDE GITHUB & DEPLOY BUT KEEP SIDEBAR TOGGLE ---
hide_st_style = """
            <style>
            /* 1. Specifically hide the Deploy button */
            [data-testid="stAppDeployButton"] {
                display: none !important;
            }

            /* 2. Specifically hide the GitHub icon (the link inside the toolbar) */
            .stAppToolbar a {
                display: none !important;
            }

            /* 3. Hide the '...' Main Menu */
            #MainMenu {
                visibility: hidden;
            }

            /* 4. Hide the footer */
            footer {
                visibility: hidden;
            }

            /* 5. FORCE the Sidebar button to stay visible */
            [data-testid="stSidebarCollapsedControl"] {
                display: block !important;
                visibility: visible !important;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# 2. API Setup
# --- FIXED VERSION ---
if "GEMINI_API_KEY" in st.secrets:
    # This runs when you are on the internet (Streamlit Cloud)
  API_KEY = st.secrets["GEMINI_API_KEY"]

# Using the stable 1.5-flash model which is the most reliable for March 2026
MODEL_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"
# 3. Data Persistence Functions
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_users(users_dict):
    with open("users.json", "w") as f:
        json.dump(users_dict, f)

# 4. Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "username" not in st.session_state:
    st.session_state.username = None

# 5. Sidebar - Settings & Features
with st.sidebar:
    st.title("⚙️ Maths.ai Settings")
    st.markdown("---")
    st.write("👨‍💻 **Developer:** Manan Soni")
    st.write("📅 **Version:** 2026.1.0")
    st.markdown("---")
    
    # User Login Feature
    users = load_users()
    uname = st.text_input("Enter your name", value=st.session_state.username if st.session_state.username else "")
    if uname:
        st.session_state.username = uname
        if uname not in users:
            users[uname] = {"scores": []}
            save_users(users)
        st.success(f"Welcome, {uname} 👋")

    st.divider()
    
    # Mode and Subject Selection
    mode = st.selectbox("Mode", ["Solve", "Learn", "Practice", "Exam"])
    subject = st.selectbox(
        "Subject", 
        ["Maths", "Science", "English", "Hindi", "Sst", "Sanskrit", "Gk", "Computer"]
    )
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 6. Main UI Header
st.title("🧠 Maths.ai - Smart Study Assistant")
st.caption("Created and Owned by Manan Soni")

# 7. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. Chat Input & AI Logic (With Safety Bypass)
if prompt := st.chat_input("Ask Maths.ai anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # This is the "Safety Bypass" payload
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        try:
            res = requests.post(MODEL_URL, json=payload, timeout=30)
            if res.status_code == 200:
                full_response = res.json()['candidates'][0]['content']['parts'][0]['text']
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                # This will tell us the EXACT error from Google
                st.error(f"Google Response: {res.status_code} - {res.text}")
        except Exception as e:
            st.error(f"System Error: {e}")
# 9. Practice Section
st.divider()
with st.expander("📝 Quick Practice Quiz"):
    quiz_topic = st.text_input("Enter topic:")
    if st.button("Generate Quiz"):
        if quiz_topic:
            with st.status("Generating..."):
                quiz_prompt = f"Create a 10-question MCQ quiz about {quiz_topic}."
                q_payload = {"contents": [{"parts": [{"text": quiz_prompt}]}]}
                q_res = requests.post(MODEL_URL, json=q_payload)
                if q_res.status_code == 200:
                    st.markdown(q_res.json()['candidates'][0]['content']['parts'][0]['text'])
