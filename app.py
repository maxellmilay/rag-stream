import streamlit as st
from PyPDF2 import PdfReader
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
import os

from utils.nlp import clean_string

load_dotenv()

# Streamlit configuration
st.set_page_config(
    page_title="RAG Bot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI and Chroma DB clients
client = OpenAI(api_key=API_KEY)
chroma_client = chromadb.Client()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name="text-embedding-3-small"
)
collection_name = "file_embeddings"
collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)

st.session_state.conversations = [
    {
        "id": 1,
        "messages": [{"role": "system", "content": "You are a helpful assistant that only answers the question based on the given context."}],
        "title": "Current Conversation"
    }
]

st.session_state.current_conversation_id = 1

# Function to chunk text
def chunk_text(text, max_tokens=8192):
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_length = len(word)
        if current_tokens + word_length + 1 <= max_tokens:
            current_chunk.append(word)
            current_tokens += word_length + 1
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_length + 1

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def switch_current_conversation(conversation_id):
    st.session_state.current_conversation_id = conversation_id

st.sidebar.title("Conversations")

for conversation in st.session_state.conversations:
    if st.sidebar.button(conversation["title"], type="secondary"):
        switch_current_conversation(conversation["id"])

# Initialize session state for processed files and chatbot interaction
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant that only answers the question based on the given context."}]

if "new_file_uploaded" not in st.session_state:
    st.session_state.new_file_uploaded = False

# Step 1: File Upload and Embedding
st.title("RAG Chatbot with File Upload")

uploaded_files = st.file_uploader("Upload one or more files", type=["pdf", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.session_state.new_file_uploaded = False  # Reset the flag
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.processed_files:
            st.session_state.new_file_uploaded = True  # Set the flag when new files are processed
            with st.spinner(f"Processing {uploaded_file.name}..."):
                if uploaded_file.name.endswith(".pdf"):
                    pdf_reader = PdfReader(uploaded_file)
                    content = "".join(page.extract_text() for page in pdf_reader.pages)
                elif uploaded_file.name.endswith(".txt"):
                    content = uploaded_file.read().decode("utf-8")
                else:
                    st.error(f"Unsupported file type: {uploaded_file.name}")
                    continue

                # Chunk content and store embeddings
                chunks = chunk_text(content, max_tokens=8192)
                for i, chunk in enumerate(chunks):
                    cleaned_chunk = clean_string(chunk)
                    document_id = f"{uploaded_file.name}_chunk_{i}"
                    collection.add(
                        documents=[cleaned_chunk],
                        metadatas=[{"filename": uploaded_file.name, "chunk_index": i, "full_content": chunk}],
                        ids=[document_id]
                    )
                st.success(f"Content from {uploaded_file.name} stored in Chroma DB!")

            # Add file to processed files list
            st.session_state.processed_files.add(uploaded_file.name)

    if not st.session_state.new_file_uploaded:
        st.info("No new files to process. All uploaded files have already been processed.")

# Step 2: Chatbot Interface
user_input = st.text_input("Ask a question:", placeholder="Type your question here...")

if user_input and not st.session_state.new_file_uploaded:  # Generate response only if no new files were uploaded
    # Retrieve relevant documents from Chroma DB
    with st.spinner("Retrieving relevant context..."):
        results = collection.query(query_texts=[user_input], n_results=3, include=["metadatas"])
        # print(results["metadatas"][0][0]["full_content"])
        context = " ".join([item["full_content"] for metadata in results["metadatas"] for item in metadata])
        
    st.session_state.messages.append({"role": "user", "content": f"Context: {context}\n\nQuestion: {user_input}"})

    print(context)

    # Query OpenAI with the retrieved context
    with st.spinner("Generating response..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            reply = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": reply})

# Display conversation history
for message in st.session_state.messages[1:]:
    if message["role"] == "user":
        st.write("**YOU**")
        st.write(f"{message['content']}")
    else:
        st.write("**BOT**")
        st.write(f"{message['content']}")
