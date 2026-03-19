import streamlit as st
import requests

# 1. Setup the Page
st.set_page_config(page_title="Maths.ai Pro", page_icon="🧠", layout="wide")

# 2. Sidebar with your Branding
with st.sidebar:
    st.title("⚙️ Maths.ai Settings")
    st.write("---")
    st.write("👤 **Developer:** Manan Soni")
    st.write("📅 **Version:** 2026.1.0")
    st.success("App is Live!")

# 3. Main Header
st.title("🧠 Maths.ai - Smart Study Assistant")
st.caption("Created and Owned by Manan Soni")

# 4. API Connection
API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
# 5. Chat History System
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. THE ONLY CHAT INPUT
if prompt := st.chat_input("Ask Maths.ai anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Expert prompt to make the AI act like a tutor
        payload = {
            "contents": [{"parts": [{"text": f"You are a helpful math tutor. Answer this: {prompt}"}]}]
        }
        
        try:
            res = requests.post(MODEL_URL, json=payload, timeout=30)
            if res.status_code == 200:
                answer = res.json()['candidates'][0]['content']['parts'][0]['text']
                response_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Google Error: {res.status_code}. Please Reboot App.")
        except:
            st.error("Connection blink. Please try again!")
