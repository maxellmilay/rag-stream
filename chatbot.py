import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Set the page configuration
st.set_page_config(
    page_title="OpenAI Chatbot",  # This sets the browser tab title
    page_icon="🤖",  # Optional: Add an emoji or icon
    layout="centered",  # Optional: Choose "centered" or "wide"
    initial_sidebar_state="expanded",  # Optional: Sidebar state
)

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

# Streamlit app
st.title("Chatbot with OpenAI API")
st.write("Ask anything, and the chatbot will respond!")

# Persistent storage for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

# User input
user_input = st.text_input("", placeholder="Type your question here...")

if user_input:
    # Append user input to messages
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Query OpenAI
    with st.spinner("Thinking..."):  # Add a spinner while waiting for the response
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
            
            # Append bot response to messages
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            reply = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": reply})

# Display conversation history
for message in st.session_state.messages[1:]:  # Skip the system message
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Bot:** {message['content']}")