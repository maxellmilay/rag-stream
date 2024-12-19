import streamlit as st
from utils.chat import initialize_chat, handle_chat, load_conversation, save_conversation
from utils.file import process_files

# Streamlit configuration
st.set_page_config(
    page_title="RAG Bot",
    page_icon="🤖",
    layout="wide",
)

# Initialize session state
initialize_chat()

# Sidebar for managing conversations
st.sidebar.title("Conversations")
if "conversations" not in st.session_state:
    st.session_state.conversations = {}  # Dictionary to store multiple conversations

# Sidebar options
selected_conversation = st.sidebar.selectbox(
    "Select Conversation", 
    options=["New Conversation"] + list(st.session_state.conversations.keys())
)

# Handle new or existing conversation
if selected_conversation == "New Conversation":
    new_convo_name = st.sidebar.text_input("Conversation Name", key="new_convo_name")
    if st.sidebar.button("Start New Conversation"):
        if new_convo_name and new_convo_name not in st.session_state.conversations:
            st.session_state.conversations[new_convo_name] = []
            st.session_state.current_conversation = new_convo_name
        else:
            st.sidebar.error("Please enter a unique conversation name.")
else:
    st.session_state.current_conversation = selected_conversation

# Load selected conversation history
load_conversation()

# Title and file upload section
st.title("RAG Chatbot with File Upload and Sidebar Conversations")
uploaded_files = st.file_uploader("Upload one or more files", type=["pdf", "txt"], accept_multiple_files=True)

# Process uploaded files
if uploaded_files:
    process_files(uploaded_files)

# Chat interface
user_input = st.text_input("Ask a question:", placeholder="Type your question here...")
if user_input:
    handle_chat(user_input)

# Save conversation
save_conversation()
