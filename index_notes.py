import os
import re
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Paths
input_file = "case_notes_final.txt"
chroma_db_path = "./chroma_db"

# Load embedding model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Read cleaned case notes
with open(input_file, "r", encoding="utf-8") as f:
    raw_notes = f.read()

# Split notes by the "---" separator to keep them as whole entries
notes = raw_notes.split("\n---\n")

# Function to clean notes (just in case any signature remains)
signature_patterns = [
    r"Best Regards,.*",
    r"Dustin Coker.*",
    r"Engage, Learn, Explore: .*",
]

def clean_note(note):
    """Remove lingering signatures and extra spaces."""
    for pattern in signature_patterns:
        note = re.sub(pattern, "", note, flags=re.DOTALL)
    return note.strip()

# Process and clean all notes
cleaned_notes = [clean_note(note) for note in notes]

# Convert notes into Document objects
documents = [Document(page_content=note, metadata={"source": f"Note {i+1}"}) for i, note in enumerate(cleaned_notes)]

# Delete existing ChromaDB to avoid duplicate entries
if os.path.exists(chroma_db_path):
    os.system(f"rm -rf {chroma_db_path}")

# Initialize ChromaDB
vector_store = Chroma.from_documents(
    documents,
    embedding=embedding_model,
    persist_directory=chroma_db_path
)

print(f"✅ Indexed {len(cleaned_notes)} case notes in ChromaDB!")

