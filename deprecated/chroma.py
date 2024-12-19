import streamlit as st
from PyPDF2 import PdfReader
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Chroma DB client
chroma_client = chromadb.Client()

# Create a collection in Chroma
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name="text-embedding-3-small"
)

collection_name = "file_embeddings"
collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)

# Function to chunk text
def chunk_text(text, max_tokens=8192):
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_length = len(word)  # Approximation; tokens != words but good enough
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

# Streamlit app
st.title("File Upload to Chroma Vector DB")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt"])

if uploaded_file:
    # Process the file content
    with st.spinner("Extracting content from the file..."):
        if uploaded_file.name.endswith(".pdf"):
            pdf_reader = PdfReader(uploaded_file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        elif uploaded_file.name.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
        else:
            st.error("Unsupported file type")
            st.stop()

    st.write("Extracted Content:")
    st.text(content[:1000] + "...")  # Show a snippet of the content

    # Chunk content
    chunks = chunk_text(content, max_tokens=8192)
    st.write(f"Content split into {len(chunks)} chunks for embedding.")

    # Store embeddings in Chroma DB
    with st.spinner("Embedding content and storing in Chroma DB..."):
        for i, chunk in enumerate(chunks):
            document_id = f"{uploaded_file.name}_chunk_{i}"  # Unique ID for each chunk
            collection.add(
                documents=[chunk],  # Store the chunked content
                metadatas=[{"filename": uploaded_file.name, "chunk_index": i}],  # Metadata with chunk index
                ids=[document_id]  # Unique ID
            )

    st.success("File content and embeddings stored in Chroma DB!")

    # Display existing data in the collection
    st.write("Stored documents in Chroma DB:")
    stored_docs = collection.get(include=["metadatas", "embeddings"])
    st.json(stored_docs)
