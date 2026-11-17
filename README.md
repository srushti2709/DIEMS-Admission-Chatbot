# DIEMS College Admission Enquiry Chatbot

A student-project implementation of the report's RAG architecture using Python, Streamlit, Sentence Transformers, NumPy semantic search (with optional FAISS acceleration), PyPDF and an optional OpenAI-compatible LLM API.

## 1. Project structure

```text
diems_admission_chatbot/
├── backend/
│   ├── config.py
│   └── services/
│       ├── ingest.py
│       ├── retriever.py
│       └── llm_service.py
├── data/
│   ├── documents/              # Put official PDF/TXT/MD documents here
│   ├── knowledge_base.jsonl   # JSONL knowledge records
│   ├── faq_template.csv       # Example structure; replace placeholders
│   └── README_DATA.md
├── tests/
├── build_index.py
├── streamlit_app.py
├── requirements.txt
└── .env.example
```

## 2. Requirements

- Python 3.10 or 3.11 recommended for smoother compatibility with ML packages.
- Internet connection for the first download of the sentence-transformer model.
- A Windows, macOS or Linux environment.

## 3. Setup on Windows (VS Code / PowerShell)

Open PowerShell in this project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatively, skip activation and run `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## 4. Prepare the college knowledge base (important)

The supplied report names the data categories but does not include the actual full verified values for programmes, fees, eligibility, documents or facilities. Do not present the template values as facts. Populate the knowledge base from current official DIEMS brochures/notices.

- Copy `templates/faq_template.csv` to `data/faq.csv` and replace all placeholder answers.
- Add JSONL records to `data/knowledge_base.jsonl` (one JSON object per line). Schema:

```json
{"id":"fee_001","text":"B.Tech fee information for academic year 2026-27: ...","metadata":{"category":"Fee information","source":"official_fee_notice.pdf","page":2,"academic_year":"2026-27","reviewed_on":"2026-11-16"}}
```

- Put official PDFs in `data/documents/`. Text-based PDF pages are extracted and chunked automatically. Scanned PDFs require OCR before ingestion.
- CSV and XLSX files in `data/` are also read. They need either a `text` column or both `question` and `answer` columns. Add category/source columns for traceability.

## 5. Build the semantic index

After adding verified data:

```powershell
python build_index.py
```

This downloads/loads `sentence-transformers/all-MiniLM-L6-v2`, embeds the records, and saves the vectors and metadata under `data/index/`. The first run can take time. NumPy cosine similarity is used by default; FAISS is optional. Install a compatible `faiss-cpu` package separately if desired.

Re-run `python build_index.py` whenever the knowledge base or source documents change.

## 6. Run the chatbot

```powershell
python -m streamlit run streamlit_app.py
```

Open the local URL printed in the terminal (usually `http://localhost:8501`).

## 7. Optional LLM mode

Without LLM settings, the chatbot runs in retrieval-only mode and displays retrieved source text. To enable generative answers, set an OpenAI-compatible chat-completions endpoint and credentials as environment variables. Never put API keys in frontend code or commit them to GitHub.

PowerShell example for the current terminal:

```powershell
$env:LLM_API_URL="https://YOUR_PROVIDER/v1/chat/completions"
$env:LLM_API_KEY="YOUR_SECRET_KEY"
$env:LLM_MODEL="YOUR_CHAT_MODEL"
python -m streamlit run streamlit_app.py
```

The endpoint must accept the standard `model`, `messages`, and `temperature` JSON fields and return `choices[0].message.content`. The app falls back to retrieved text if the API fails.

## 8. Test

```powershell
pip install pytest
python -m pytest -q
```

Also manually test: programme enquiry, paraphrased campus/location question, fee query with category and year, eligibility, category-specific documents, unknown live-seat query, blank input and long input. Record actual outcomes before reporting accuracy in the case study.

## 9. Important safeguards

- It is an enquiry helper, not an admission authority.
- It must not guarantee admission, seat allocation or scholarship approval.
- Fees and eligibility must retain the academic year and category.
- Confirm time-sensitive facts with current official notices.
- Avoid collecting sensitive applicant documents or personal data.
- Source labels are displayed to help users trace retrieved content.

## 10. Deployment note

Deploy the Streamlit app on a host that can install the pinned dependencies, download/load the embedding model and access the knowledge files. For cloud deployment, add API secrets through the host's secrets manager. Ensure the index is rebuilt during deployment or included as a generated artifact. Test dependencies in the target Linux/Python environment before publishing.
