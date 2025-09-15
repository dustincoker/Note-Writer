import sys
import ollama
import os
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer

# Ensure the user provides a query
if len(sys.argv) < 2:
    print("❌ Usage: python ask.py \"your question here\"")
    sys.exit(1)

# Get the user query from command line
query = " ".join(sys.argv[1:])


# ✅ Define local model path
local_model_path = "./models/all-MiniLM-L6-v2"

# ✅ Ensure model is downloaded and cached locally
if not os.path.exists(local_model_path):
    print("📥 Downloading embedding model (this may take a moment)...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    model.save(local_model_path)  # Save model locally
    print("✅ Model downloaded and cached locally.")
else:
    print("✅ Using cached embedding model.")

# ✅ Load embedding model from local path
embedding_model = HuggingFaceEmbeddings(model_name=local_model_path)

# Load ChromaDB
vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)

# Create retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Retrieve relevant notes
docs = retriever.invoke(query)

# Display retrieved case notes
print("\n🔍 Retrieved Notes:\n")
retrieved_text = ""
for i, doc in enumerate(docs):
    print(f"[{i + 1}] {doc.page_content}")
    print("-" * 80)
    retrieved_text += f"{doc.page_content}\n\n"

# If no relevant notes are found
if not retrieved_text.strip():
    print("⚠️ No relevant notes found.")
    sys.exit(1)


# Ollama prompt
prompt = f"""
You are a technical support engineer at SugarCRM.
Based on the following past case notes, generate a support response in the same style. 


⚠️ NOTE: DO NOT include a sign-off or signature such as "Best regards".


Relevant past notes:
{retrieved_text}

New Issue:
{query}


Generate a detailed response in the same style as the past notes.
"""

# Call Ollama to generate a response using LLM 
response = ollama.chat(model="deepseek-r1:32b", messages=[{"role": "user", "content": prompt}])

# Extract the AI-generated response
ai_response = response["message"]["content"].strip()

# Append a newline before the signature to ensure proper spacing
signature = """
Best Regards,

Dustin Coker
Technical Support Engineer
Engage, Learn, Explore: https://sugarclub.sugarcrm.com
"""

# Output AI-generated support note with properly formatted signature
print("\n📌 AI-Generated Support Note:\n")
print(ai_response + "\n" + signature)

