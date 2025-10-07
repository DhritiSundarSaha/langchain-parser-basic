import os
import streamlit as st
from dotenv import load_dotenv
from chat import respond

load_dotenv()

st.set_page_config(page_title="Contact Extractor Chatbot", page_icon="📇", layout="centered")
st.title("📇 Contact Extractor — Gemini + LangChain + Pydantic")
st.caption("Extracts contact data from messages.")

with st.sidebar:
    st.text_input("GOOGLE_API_KEY", type="password", value=os.getenv("GOOGLE_API_KEY") or "", key="api_key")
    st.text_input("MODEL_ID", value=os.getenv("MODEL_ID", "gemini-2.5-flash"), key="model_id")
    st.text_input("DEFAULT_REGION", value=os.getenv("DEFAULT_REGION", "IN"), key="default_region")
    st.markdown("---")
    st.markdown("Paste contact text like: 'I'm Raj, 22, email raj(at)gmail,com'")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Message:")
if st.button("Send") and user_input.strip():
    reply = respond(user_input)
    st.session_state.history.append((user_input, reply))
    st.rerun()  # <-- fixed
if st.session_state.history:
    st.markdown("### Chat History")

for u, r in reversed(st.session_state.history):
    st.markdown(f"**You:** {u}")
    st.code(r, language="json")