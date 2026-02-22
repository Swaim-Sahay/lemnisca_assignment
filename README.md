# Clearpath RAG Chatbot

A production-ready customer support chatbot for **Clearpath**, a fictional SaaS project management tool. This system implements a custom Retrieval-Augmented Generation (RAG) pipeline with deterministic model routing and automated response evaluation.

## 🚀 How to Run Locally

Follow these steps to set up and run Clearpath on your local machine.

### 1. Prerequisites
- **Python 3.9+**
- **Groq API Key**: Obtain one from the [Groq Console](https://console.groq.com/).

### 2. Installation & Setup
```bash
# Clone the repository and navigate to the directory
cd lemnisca-take-home

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pypdf sentence-transformers numpy groq python-multipart
```

### 3. Ingest Documentation (Generate Vector Store)
The RAG pipeline requires a local vector store built from the Clearpath manual PDFs located in `docs/`.
```bash
# Run the ingestion script to create vector_store.pkl
PYTHONPATH=. python backend/rag.py
```
*Wait for the process to complete. This generates local embeddings using `all-MiniLM-L6-v2`.*

### 4. Start the Application
```bash
# Set your Groq API key
export GROQ_API_KEY="your_api_key_here"

# Start the FastAPI server
PYTHONPATH=. uvicorn backend.main:app --port 8000
```
Visit **[http://localhost:8000](http://localhost:8000)** to interact with the chatbot.

---

## 🧠 Groq Models & Environment Configuration

Clearpath utilizes a "Router" architecture to optimize for both cost and performance:

| Model | Usage | Trigger |
| :--- | :--- | :--- |
| **Llama 3.1 8B Instant** | **Simple** queries | Short, factual, or greeting-oriented questions. |
| **Llama 3.3 70B Versatile** | **Complex** queries | Synthesis, multi-part, or troubleshooting intents. |

**Configuration:**
- `GROQ_API_KEY`: Mandatory environment variable for LLM access.
- All model names and chunking parameters are configurable in `backend/config.py`.

---

## 🏆 Bonus Challenges Attempted

- **Glassmorphic UI & System Dashboard**: Built a premium, interactive frontend using vanilla CSS with glassmorphism effects that displays real-time system metrics (Latency, Token Usage, Model Classification, and Evaluator Flags) in a dedicated debug panel.

---

## ⚠️ Known Issues & Limitations

- **Stateless Conversations**: The current MVP treats each query as an isolated event. It does not maintain multi-turn memory (e.g., following up with "How does that compare to the budget plan?").
- **Cold Start Latency**: The first execution may experience a delay of 5-10 seconds while the `sentence-transformers` model weights are loaded into local memory.
- **Keyword Dependency**: The router relies on deterministic keywords and length. Highly complex but very short queries might occasionally be routed to the 8B model. 
- **Static Vector Store**: Changes to the `docs/` folder require a manual re-run of `backend/rag.py` to update the `vector_store.pkl` database.
