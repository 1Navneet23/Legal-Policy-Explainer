# ⚖️ LegalMind — AI-Powered Legal Document Assistant

> Upload any legal PDF. Ask questions in plain English. Get clear, grounded answers — powered by local LLMs and semantic search.

---

## 📌 What It Does

LegalMind is a **Retrieval-Augmented Generation (RAG)** backend that lets users upload legal documents (contracts, agreements, acts, policies) and ask natural-language questions about them. It never hallucinates law — every answer is grounded strictly in the text of the uploaded document.

Two modes are supported:

| Mode | What it does |
|---|---|
| `explain` | Explains a legal clause or term in simple language |
| `scenario` | Reasons about a real-world situation using the document's legal text |

---

## 🧠 How It Works

```
User uploads PDF
      ↓
PDF text extracted  (PyPDF2)
      ↓
Text split into overlapping chunks  (custom text_splitter)
      ↓
Chunks embedded into vectors  (all-MiniLM-L6-v2)
      ↓
Vectors stored in ChromaDB  (per-session isolated collection)
      ↓
User asks a question
      ↓
Question embedded → top-k similar chunks retrieved
      ↓
Chunks + question sent to Mistral (via Ollama)
      ↓
Plain-English answer returned
```

---

## 🗂️ Project Structure

```
├── app.py                  # FastAPI entrypoint — all routes live here
├── backend/
│   ├── pdf_reader.py       # Extracts raw text from PDF files
│   ├── text_splitter.py    # Splits text into overlapping word chunks
│   ├── embeddings.py       # Encodes chunks into sentence vectors
│   ├── model_loader.py     # Loads the SentenceTransformer model (singleton)
│   ├── vector_store.py     # ChromaDB store/search — per-session collections
│   ├── search.py           # Cosine similarity search helper
│   └── llm_explainer.py    # Prompts Mistral via Ollama for final answers
├── uploads/                # Uploaded PDFs stored here (named by session_id)
├── chroma_db/              # ChromaDB persistent storage
└── sessions.json           # Active session state (survives restarts)
```

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) installed and running locally
- Mistral model pulled via Ollama:

```bash
ollama pull mistral
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn python-multipart \
            PyPDF2 sentence-transformers \
            chromadb scikit-learn ollama
```

### 3. Run the Server

```bash
uvicorn app:app --reload
```

The API will be live at `http://localhost:8000`.

---

## 📡 API Reference

### `GET /health`
Check that the server is running.

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

### `POST /session/create`
Creates a new isolated session. Returns a `session_id` and sets an `httponly` cookie.

```bash
curl -c cookies.txt -X POST http://localhost:8000/session/create
```

```json
{
  "message": "Session created",
  "session_id": "f47ac10b-58cc-..."
}
```

---

### `POST /upload`
Upload a PDF for the current session. The document is processed, chunked, embedded, and stored immediately.

```bash
curl -b cookies.txt -X POST http://localhost:8000/upload \
     -F "file=@contract.pdf"
```

```json
{
  "message": "PDF uploaded and processed.",
  "session_id": "f47ac10b-58cc-..."
}
```

---

### `POST /ask_question`
Ask a question about the uploaded document.

```bash
curl -b cookies.txt -X POST http://localhost:8000/ask_question \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "f47ac10b-58cc-...",
       "question": "What are the termination conditions?",
       "mode": "explain"
     }'
```

**Body fields:**

| Field | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | required | Your session ID |
| `question` | `str` | required | Natural language question |
| `mode` | `str` | `"explain"` | `"explain"` or `"scenario"` |

```json
{
  "session": "f47ac10b-58cc-...",
  "answer": "The contract can be terminated by either party with 30 days written notice...",
  "mode": "explain"
}
```

---

### `DELETE /session/clear`
Deletes your session, removes your uploaded PDF, and wipes your ChromaDB collection.

```bash
curl -b cookies.txt -X DELETE http://localhost:8000/session/clear
```

```json
{
  "message": "Session cleared."
}
```

---

## 🔧 Configuration

| Parameter | Location | Default | Description |
|---|---|---|---|
| Chunk size | `text_splitter.py` | `500` words | Max words per chunk |
| Overlap | `text_splitter.py` | `50` words | Context carried over between chunks |
| Top-k results | `vector_store.py` | `3` | Number of chunks retrieved per query |
| Embedding model | `model_loader.py` | `all-MiniLM-L6-v2` | Sentence transformer used for vectors |
| LLM model | `llm_explainer.py` | `mistral` | Ollama model used for generation |

---

## 🏗️ Architecture Decisions

### Per-Session ChromaDB Collections
Each session gets its own isolated ChromaDB collection (`session_<uuid>`). This ensures that document chunks from different users are never mixed together. When a session is deleted, the corresponding collection is also cleaned up.

### Overlapping Chunking
Text is split into word-count-bounded chunks with a configurable overlap window. Overlap sentences are carried forward from the previous chunk so that context is not lost at chunk boundaries — important for legal text where a clause may span multiple sentences.

### Top-K Context Merging
Instead of sending a single best-matching chunk to the LLM, the top 3 most relevant chunks are retrieved and merged with a separator (`---`). This gives the LLM broader context and leads to more accurate, complete answers.

### Local-First, No Data Leaves Your Machine
The entire stack — embedding model, vector database, and LLM — runs locally. No API keys required, no data sent to third-party services.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| PDF Parsing | [PyPDF2](https://pypi.org/project/PyPDF2/) |
| Embeddings | [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| Vector Store | [ChromaDB](https://www.trychroma.com/) |
| LLM | [Mistral](https://mistral.ai/) via [Ollama](https://ollama.ai/) |
| Session Storage | JSON file + HTTP cookies |

---

## 🔒 Privacy & Safety

- All processing is **local** — your documents never leave your machine
- Each session is **fully isolated** at the vector store level
- The LLM is instructed to answer **only from the provided document text** and will explicitly say when information is not available rather than guess
- Uploaded files are namespaced by `session_id` and deleted when the session is cleared

---

## 🧪 Example Use Cases

- **"Does this contract allow subletting?"** — get a plain-English answer from a dense rental agreement
- **"My employer hasn't paid me in 3 weeks — what does the labour act say?"** — scenario reasoning against an uploaded policy document
- **"Summarise the liability clause"** — instant explanations without a lawyer

---

## 📄 License

MIT License — free to use, modify, and distribute.

 
*Built with FastAPI · ChromaDB · SentenceTransformers · Ollama · Mistral*
