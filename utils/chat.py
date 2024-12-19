import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# OpenAI API client
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

def initialize_chat():
    """Initialize session state for chatbot and conversations."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = None

def handle_chat(user_input):
    """Handle user input and chatbot response."""
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        with st.spinner("Generating response..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.write("**BOT:**")
            st.write(reply)
    except Exception as e:
        st.write(f"Error: {str(e)}")

def load_conversation():
    """Load chat history for the selected conversation."""
    current_conversation = st.session_state.current_conversation
    if current_conversation:
        st.session_state.messages = st.session_state.conversations.get(current_conversation, [])

def save_conversation():
    """Save the current chat history to the conversations dictionary."""
    current_conversation = st.session_state.current_conversation
    if current_conversation:
        st.session_state.conversations[current_conversation] = st.session_state.messages
