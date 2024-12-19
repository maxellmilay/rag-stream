from PyPDF2 import PdfReader
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.nlp import clean_string
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Chroma DB client

API_KEY = os.getenv("OPENAI_API_KEY")

def chunk_text(text, max_tokens=8192):
    """Chunk text into smaller pieces."""
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

def process_files(uploaded_files):
    """Process uploaded files and add to Chroma DB."""
        
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=API_KEY,
        model_name="text-embedding-3-small"
    )
    chroma_client = chromadb.Client()
    collection_name = "file_embeddings"
    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)

    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state.get("processed_files", set()):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                if uploaded_file.name.endswith(".pdf"):
                    pdf_reader = PdfReader(uploaded_file)
                    content = "".join(page.extract_text() for page in pdf_reader.pages)
                elif uploaded_file.name.endswith(".txt"):
                    content = uploaded_file.read().decode("utf-8")
                else:
                    st.error(f"Unsupported file type: {uploaded_file.name}")
                    continue

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

            st.session_state.processed_files.add(uploaded_file.name)
