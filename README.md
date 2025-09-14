
---

# Note Writer (RAG + Ollama)

Draft customer-facing support notes in **your own style** using Retrieval-Augmented Generation (RAG).

* **Index** your past notes into a local Chroma vector DB.
* **Retrieve** the top-K similar notes.
* **Generate** a new note in your style with an Ollama-hosted LLM (default: `deepseek-r1:32b`).

> ⚠️ **Do not** commit real notes or your vector DB. Use the provided anonymizer and keep data local.

---

## Quickstart

```bash
git clone <your-repo-url>
cd note-writer-rag
cp .env.example .env

# Create venv & install deps
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Install spaCy model for anonymization (optional but recommended)
python -m spacy download en_core_web_trf

# Try the demo with synthetic notes
mkdir -p data
cp samples/notes.txt data/case_notes_final.txt
python src/index_notes.py

# Generate a draft note
python src/ask_new.py "Write a note letting the customer know I disabled the logic hook but it did not resolve the issue. Tell them I'll keep looking and send an update soon."
```

Or use the **Makefile**:

```bash
make install
python -m spacy download en_core_web_trf
make demo
make run
```

---

## Project Structure

```
note-writer-rag/
├─ src/
│  ├─ write.py          # query + generate (entry point)
│  ├─ anonymize.py      # PII redaction utilities
│  └─ index_notes.py    # build Chroma index from notes
├─ samples/             # synthetic notes to try out
├─ prompts/             # prompt templates
├─ docs/                # redaction & eval notes
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ Makefile
└─ LICENSE
```

---

## Data Preparation

Your notes file should be a single text file with each note separated by a line containing `---`.

**Example (`data/case_notes_final.txt`):**

```
First note text here...
---
Second note text here...
---
Third note text here...
```

### (Recommended) Anonymize before indexing

```bash
# Reads INPUT_NOTES_PATH and writes ANON_OUTPUT_PATH (see .env)
python src/anonymize.py

# Then build the index using the anonymized notes:
# (by default index_notes.py reads INPUT_NOTES_PATH; point that to the anonymized file in .env)
python src/index_notes.py
```

---

## Usage

Draft a note by describing what you want to say:

```bash
python src/ask_new.py "Write a note to Jane Doe letting them know I disabled the logic hook but it didn't resolve the issue, and that I will follow up soon."
```

What happens:

1. Loads embeddings (`sentence-transformers/all-MiniLM-L6-v2` by default).
2. Retrieves top-K similar notes from Chroma.
3. Loads an optional prompt template from `prompts/note_template.txt`.
4. Calls your local Ollama model (default `deepseek-r1:32b`) with retrieved context.
5. Prints the drafted note (optionally appends a signature).

---

## Configuration

All settings are read from `.env` (see `.env.example`):

```dotenv
# Paths
CHROMA_DB=./chroma_db
INPUT_NOTES_PATH=./data/case_notes_final.txt

# Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=deepseek-r1:32b

# Optional
ADD_SIGNATURE=true
SPACY_MODEL=en_core_web_trf
ANON_OUTPUT_PATH=./data/anonymized_notes.txt
PROMPT_TEMPLATE_PATH=./prompts/note_template.txt

# Retrieval
TOP_K=5
```

* **CHROMA\_DB**: where the vector index is stored (persisted locally).
* **INPUT\_NOTES\_PATH**: the notes file to index (use anonymized output for safety).
* **LLM\_MODEL**: any Ollama model you have locally (e.g., `deepseek-r1:7b`, `qwen2.5:7b`).
* **ADD\_SIGNATURE**: if `true`, appends the example signature block to output.
* **PROMPT\_TEMPLATE\_PATH**: optional template to control tone/format.
* **TOP\_K**: number of similar notes to retrieve.

---

## Redaction & Safety

See `docs/redaction.md` for a checklist. The provided anonymizer:

* Uses spaCy NER (`en_core_web_trf`) to replace entity spans (e.g., names, orgs) with placeholders.
* Masks emails/phones via regex.
* Preserves `---` separators.

**Always** spot-check a sample before indexing or sharing drafts.

---

## Troubleshooting

* **No relevant notes found**
  Make sure you’ve run `index_notes.py` and that `CHROMA_DB` points to the correct directory.

* **spaCy model not found**
  Run: `python -m spacy download en_core_web_trf` and ensure `SPACY_MODEL=en_core_web_trf`.

* **Model errors with Ollama**
  Ensure Ollama is running and you’ve pulled the model, e.g.:
  `ollama run deepseek-r1:32b` (or set `LLM_MODEL` to a model you have locally).

* **Inconsistent imports**
  All scripts use `from langchain_community.vectorstores import Chroma`.

---

## Notes on Data & Licensing

* Do **not** upload real notes or your `chroma_db/`.
* Provide only **synthetic or heavily anonymized** samples in `samples/`.
* This repository is licensed under **MIT** (see `LICENSE`).

---

## Roadmap (Optional Enhancements)

* FastAPI wrapper (`/draft`, `/healthz`) for HTTP requests.
* CLI with `typer` for nicer commands.
* Retrieval evaluators and style-similarity scoring.
* Pluggable redaction rules (term maps, regex packs).

---

**Enjoy!** If you use this, consider sharing improvements via PRs.

