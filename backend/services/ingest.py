"""Load FAQ/structured files/PDFs and create traceable text records."""
import csv
import json
import re
from pathlib import Path
from typing import Iterable

from backend.config import DATA_DIR, DOCUMENTS_DIR, KNOWLEDGE_FILE

SUPPORTED_TEXT = {".txt", ".md"}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int = 850, overlap: int = 120) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        part = text[start:end].strip()
        if part:
            chunks.append(part)
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _normalise_record(record: dict, fallback_id: str, source: str) -> dict | None:
    text = clean_text(str(record.get("text", "")))
    if not text:
        # Convenient FAQ CSV format: question + answer columns.
        question = clean_text(str(record.get("question", "")))
        answer = clean_text(str(record.get("answer", "")))
        if question and answer:
            text = f"Question: {question} Answer: {answer}"
    if not text:
        return None
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    metadata.setdefault("source", source)
    metadata.setdefault("category", str(record.get("category", "General")))
    return {"id": str(record.get("id") or fallback_id), "text": text, "metadata": metadata}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path.name}, line {line_no}: {exc}") from exc
            item = _normalise_record(raw, f"{path.stem}_{line_no}", path.name)
            if item:
                records.append(item)
    return records


def load_csv(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for i, row in enumerate(csv.DictReader(handle), 1):
            item = _normalise_record(row, f"{path.stem}_{i}", path.name)
            if item:
                records.append(item)
    return records


def load_excel(path: Path) -> list[dict]:
    import pandas as pd
    frame = pd.read_excel(path, dtype=str).fillna("")
    return [item for i, row in enumerate(frame.to_dict(orient="records"), 1)
            if (item := _normalise_record(row, f"{path.stem}_{i}", path.name))]


def load_pdf(path: Path) -> list[dict]:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    records = []
    for page_no, page in enumerate(reader.pages, 1):
        page_text = clean_text(page.extract_text() or "")
        for chunk_no, chunk in enumerate(chunk_text(page_text), 1):
            records.append({
                "id": f"{path.stem}_p{page_no}_c{chunk_no}",
                "text": chunk,
                "metadata": {"category": "Document", "source": path.name, "page": page_no}
            })
    return records


def load_all_records() -> list[dict]:
    DATA_DIR.mkdir(exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    if KNOWLEDGE_FILE.exists():
        records.extend(load_jsonl(KNOWLEDGE_FILE))
    for path in sorted(DATA_DIR.glob("*.csv")):
        records.extend(load_csv(path))
    for path in sorted(DATA_DIR.glob("*.xlsx")):
        records.extend(load_excel(path))
    for path in sorted(DOCUMENTS_DIR.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".pdf":
            records.extend(load_pdf(path))
        elif path.suffix.lower() in SUPPORTED_TEXT:
            for i, chunk in enumerate(chunk_text(path.read_text(encoding="utf-8")), 1):
                records.append({"id": f"{path.stem}_{i}", "text": chunk,
                                "metadata": {"category": "Document", "source": path.name}})
    # Deduplicate exact text while retaining the first source record.
    unique, seen = [], set()
    for record in records:
        key = record["text"].casefold()
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique
