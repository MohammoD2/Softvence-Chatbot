# Softvence Chatbot

Welcome to the Softvence Chatbot — a clean, searchable, and extensible Streamlit-based QA assistant that uses sentence-transformers embeddings and a FAISS vector index to find relevant content for product-specific knowledge and a conversational LLM  to generate responses.

This README is crafted to be friendly, actionable, and impressive for reviewers. It explains architecture, setup (Windows PowerShell), how the pieces fit together, troubleshooting, and sensible next steps.

## Quick summary

- Project: Softvence Chatbot
- Purpose: Provide a product-aware conversational assistant that answers user questions using indexed product content and an LLM.
- Frontend: Streamlit (`Chatbot_app.py`) — simple chat UI with preserved session history.
- Backend/logic: `Chatbot.py` (embeddings, FAISS search, OpenRouter calls), `process_pipeline.py` (data processing pipeline — used to create chunks & FAISS index).
- Data: `processed_data/<ProductName>/faiss_store/index.faiss` + `chunks.pkl` (embeddings and text chunks). Additional supporting content in `local_storage/`.

## Project layout (important files)

- `Chatbot_app.py` — Streamlit UI, session handling and invocation of `chatbot()`.
- `Chatbot.py` — Chat logic: loads FAISS index, embeddings model, searches for similar chunks, and asks the LLM to generate responses.
- `process_pipeline.py` — (pipeline to ingest documents, chunk them, compute embeddings, and build FAISS index). Use when you need to add or rebuild product data.
- `requirements.txt` — Python dependencies.
- `processed_data/` — Contains per-product FAISS indexes used at runtime.
- `local_storage/Softvence/product_info.txt` — example product content used to seed the knowledge base.

## Contract (short)

- Input: a user chat message (string) via the Streamlit UI.
- Output: a short, professional assistant reply (string) that references product knowledge when relevant.
- Failure modes: missing API key, missing FAISS index for a product, network failures to OpenRouter.

## Prerequisites

- Windows (instructions below use PowerShell). Works similarly on macOS / Linux but adjust the commands (bash). 
- Python 3.8+ recommended.
- A modern internet connection for the LLM API calls.

Important: This repository currently includes an example `.env` file. Treat any real API keys as secrets; rotate them if they were checked into source control.

## Setup — Windows PowerShell (recommended)

1. Open PowerShell in the project root (where `requirements.txt` and `Chatbot_app.py` live).

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Upgrade pip and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r .\requirements.txt
```

4. Add API key(s):

- The bot uses an OpenRouter-compatible endpoint. Add an `OPENROUTER_API_KEY` to a `.env` file in the root (or use Streamlit secrets local). Example `.env` layout:

```text
OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

Note: The repository may contain an example `.env`. If you put real keys in source control, rotate them and move to secure storage.

5. (Optional) If you want to register the key in Streamlit secrets (recommended for deployments), create a file named `.streamlit/secrets.toml` with:

```toml
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
```
# Handling the OPENROUTER_API_KEY (Local vs Streamlit Cloud)

**How to access your API key securely:**

- **Locally (development):**
  - Store your key in a `.env` file at the project root.
  - Access it in your code using `os.getenv("OPENROUTER_API_KEY")` after calling `load_dotenv()`.

- **On Streamlit Cloud:**
  - Add your key to the Streamlit secrets UI or in `.streamlit/secrets.toml`.
  - Access it in your code using `st.secrets["OPENROUTER_API_KEY"]`.

**Recommended code pattern:**

```python
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_openrouter_api_key():
    # Prefer Streamlit secrets if available, else fallback to .env
    if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
        return st.secrets["OPENROUTER_API_KEY"]
    return os.getenv("OPENROUTER_API_KEY")

# Usage:
OPENROUTER_API_KEY = get_openrouter_api_key()
```

This ensures your code works both locally and on Streamlit Cloud, and never hardcodes secrets.
6. Run the Streamlit app:

```powershell
streamlit run .\Chatbot_app.py
```

Open the local URL shown by Streamlit (usually http://localhost:8501).

## How it works (end-to-end)

1. On start, `Chatbot.py` creates a `SimpleChatManager` that scans `processed_data/` for per-product data and attempts to load:
   - A FAISS index (`index.faiss`) located at `processed_data/<Product>/faiss_store/index.faiss`.
   - A `chunks.pkl` file containing `chunks` (text segments) and embeddings.

2. When the user sends a query from the Streamlit UI, the flow is:
   - Compute an embedding for the query (SentenceTransformers `all-MiniLM-L6-v2`).
   - Use FAISS to find top-k similar chunks for the specified product.
   - Build a context-driven prompt containing the relevant product chunks and a short instruction set that aligns the LLM voice with Softvence.
   - Call the OpenRouter chat completions endpoint with the prompt and return the LLM response to the user.

3. If no FAISS index or relevant chunks exist, the app returns a friendly product overview fallback.

## Rebuilding or adding product data

1. Add source documents to a directory or create a new product folder under `processed_data/<NewProduct>/`.
2. Run `process_pipeline.py` to chunk, embed, and build the FAISS index. (This file is part of the repo and should be tailored to your documents.)
3. Confirm `processed_data/<NewProduct>/faiss_store/index.faiss` and `chunks.pkl` are created.
4. Restart Streamlit or the app will pick up the new product on next initialization.

## Configuration & important constants (where to change)

- Embedding model: `Chatbot.py` sets `MODEL_NAME = "all-MiniLM-L6-v2"`. Change if you want a different model.
- FAISS index path: `processed_data/<product>/faiss_store/index.faiss` (convention used by the code).
- LLM model used for generation is configured via `OPENROUTER_MODEL` in `Chatbot.py`.

## Troubleshooting

- Problem: "No FAISS index or chunks found for product"
  - Ensure `processed_data/<Product>/faiss_store/index.faiss` exists and `chunks.pkl` is present.
  - Re-run `process_pipeline.py` to create embeddings and the index.

- Problem: "Missing or invalid OPENROUTER_API_KEY"
  - Add your key to `.env` or `.streamlit/secrets.toml` and restart the app.
  - Confirm the key has correct permissions and has not been rate-limited/expired.

- Problem: App is slow when generating responses
  - Network latency to the LLM provider or large prompts can slow responses.
  - Reduce the number of chunks returned by the FAISS search (modify `k` in `search_similar_chunks`).

- Problem: The LLM output is incorrect or off-topic
  - Inspect the constructed prompt in `Chatbot.py` and refine the instruction section or reduce noisy chunks.

Check logs: `Chatbot.py` configures logging. You can change the logging level at the top of the file to `INFO` or `DEBUG` for more details.

## Safety & privacy

- Do not commit real API keys to version control. Use .env, OS environment variables, or Streamlit secrets.
- If your product data contains PII, ensure you follow your organization's data-retention and privacy policies when embedding and storing vectors.

## Edge cases & notes

- Empty dataset: The bot returns a friendly company overview if no relevant chunks are found.
- Large datasets: FAISS handles large vector collections, but embedding generation is the bottleneck. Use batched embedding generation when building indexes.
- Offline: If the LLM endpoint is unreachable, the app logs an error and returns a short failure message.

## Development checklist (quick)

1. Create & activate venv
2. Install requirements
3. Add API keys to `.env` or Streamlit secrets
4. Run `process_pipeline.py` to index product docs (if you have new docs)
5. Run Streamlit

## Commands (PowerShell)

```powershell
# create venv and activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install deps
pip install -r .\requirements.txt

# run streamlit UI
streamlit run .\Chatbot_app.py
```

## Next steps / improvements (suggestions)

- Add a CI check that aborts if `.env` is committed or any API key is present.
- Add unit tests for: FAISS loading, embedding generation stubbed, prompt construction.
- Add a small Dockerfile for deployment.
- Add a small test harness script to simulate end-to-end requests to the LLM using a test key / mock server.

## Contributing

If you'd like to contribute: fork, create a branch, add tests for new behavior, and open a PR with a clear description of the change. Follow the repository style and keep changes small.

## License

This project is provided as-is. Add a license file (e.g. MIT) if you want to allow reuse.

---

If you'd like, I can also:

- Add a small `README` badge header (CI, Python version),
- Create a minimal `Dockerfile` and `docker-compose.yml` for production deployment,
- Add a tiny test that imports `Chatbot.py` and does a dry-run of `SimpleChatManager` (mocking network calls).

Tell me which of the above you'd like next and I will implement it.
