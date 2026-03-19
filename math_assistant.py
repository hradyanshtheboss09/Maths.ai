import streamlit as st
import json
import os
import requests
import time

# 1. Page Configuration
st.set_page_config(page_title="Maths.ai Pro - Manan Soni", page_icon="🧠", layout="wide")

# --- THE ULTIMATE API SETUP ---
API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# --- CHAT LOGIC ---
# --- CLEAN CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Single Chat Input
if prompt := st.chat_input("Ask Maths.ai anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        payload = {
            "contents": [{"parts": [{"text": f"You are Maths.ai by Manan Soni. Answer this: {prompt}"}]}]
        }
        
        try:
            res = requests.post(MODEL_URL, json=payload, timeout=30)
            if res.status_code == 200:
                answer = res.json()['candidates'][0]['content']['parts'][0]['text']
                response_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("Google is busy. Try one more time!")
        except:
            st.error("Connection blink. Please refresh!")
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

# 8. Chat Input & AI Logic
if prompt := st.chat_input("Ask Maths.ai anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        system_context = f"You are Maths.ai, an expert tutor developed by Manan Soni. Mode: {mode}. Subject: {subject}. "
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        full_query = system_context + history_text
        payload = {"contents": [{"parts": [{"text": full_query}]}]}
        
        try:
            res = requests.post(MODEL_URL, json=payload, timeout=20)
            if res.status_code == 200:
                full_response = res.json()['candidates'][0]['content']['parts'][0]['text']
                displayed_text = ""
                for word in full_response.split(" "):
                    displayed_text += word + " "
                    response_placeholder.markdown(displayed_text + "▌")
                    time.sleep(0.04)
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("Connection error. Check API settings.")
        except Exception as e:
            st.error(f"Error: {e}")

# 9. Practice Section
st.divider()
with st.expander("📝 Quick Practice Quiz"):
    quiz_topic = st.text_input("Enter topic:")
    if st.button("Generate Quiz"):
        if quiz_topic:
            with st.status("Generating..."):
                quiz_prompt = f"Create a 3-question MCQ quiz about {quiz_topic}."
                q_payload = {"contents": [{"parts": [{"text": quiz_prompt}]}]}
                q_res = requests.post(MODEL_URL, json=q_payload)
                if q_res.status_code == 200:
                    st.markdown(q_res.json()['candidates'][0]['content']['parts'][0]['text'])
