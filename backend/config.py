from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
KNOWLEDGE_FILE = DATA_DIR / "knowledge_base.jsonl"
INDEX_DIR = DATA_DIR / "index"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K = int(os.getenv("TOP_K", "5"))
MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.28"))
MAX_QUESTION_LENGTH = 1000
LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
