
"""Hybrid retrieval using Sentence Transformers and keyword matching."""

import json
import re
import numpy as np

from backend.config import EMBEDDING_MODEL, INDEX_DIR, MIN_SIMILARITY, TOP_K
from backend.services.ingest import load_all_records


class Retriever:

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self.records: list[dict] = []
        self.vectors: np.ndarray | None = None
        self.faiss_index = None

    @staticmethod
    def _normalise(vectors: np.ndarray) -> np.ndarray:
        vectors = np.asarray(vectors, dtype="float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)

    @staticmethod
    def _tokens(text: str) -> set:
        stopwords = {
            "what", "is", "are", "the", "a", "an", "of", "in",
            "on", "for", "to", "and", "or", "with", "do", "does",
            "can", "i", "we", "you", "my", "your", "how", "much",
            "many", "tell", "me", "about", "please", "give",
            "information", "available", "there", "at", "from",
            "which", "who", "when", "where", "diems"
        }

        words = set(re.findall(r"[a-z0-9]+", text.lower()))
        return words - stopwords

    def build(self, records: list[dict] | None = None) -> int:

        self.records = (
            records if records is not None else load_all_records()
        )

        if not self.records:
            raise ValueError(
                "No knowledge records found. Add verified records "
                "to data/knowledge_base.jsonl or supported files."
            )

        raw = self.model.encode(
            [r["text"] for r in self.records],
            convert_to_numpy=True,
            show_progress_bar=True
        )

        self.vectors = self._normalise(raw)
        self.faiss_index = None

        try:
            import faiss

            self.faiss_index = faiss.IndexFlatIP(
                self.vectors.shape[1]
            )
            self.faiss_index.add(self.vectors)

        except Exception:
            pass

        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        np.save(INDEX_DIR / "embeddings.npy", self.vectors)

        (INDEX_DIR / "records.json").write_text(
            json.dumps(self.records, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        (INDEX_DIR / "model.txt").write_text(
            EMBEDDING_MODEL,
            encoding="utf-8"
        )

        return len(self.records)

    def load(self) -> bool:

        vectors_path = INDEX_DIR / "embeddings.npy"
        records_path = INDEX_DIR / "records.json"

        if not vectors_path.exists() or not records_path.exists():
            return False

        saved_model = (
            (INDEX_DIR / "model.txt").read_text(
                encoding="utf-8"
            ).strip()
            if (INDEX_DIR / "model.txt").exists()
            else EMBEDDING_MODEL
        )

        if saved_model != EMBEDDING_MODEL:
            return False

        self.vectors = np.load(vectors_path).astype("float32")

        self.records = json.loads(
            records_path.read_text(encoding="utf-8")
        )

        try:
            import faiss

            self.faiss_index = faiss.IndexFlatIP(
                self.vectors.shape[1]
            )
            self.faiss_index.add(self.vectors)

        except Exception:
            self.faiss_index = None

        return True

    def search(self, question: str, top_k: int = TOP_K) -> list[dict]:

        if self.vectors is None or not self.records:
            raise RuntimeError(
                "Index is not loaded. Build the knowledge index first."
            )

        query_vector = self._normalise(
            self.model.encode(
                [question],
                convert_to_numpy=True
            )
        )

        # Semantic similarity scores
        if self.faiss_index is not None:

            scores, indices = self.faiss_index.search(
                query_vector,
                len(self.records)
            )

            semantic_results = zip(
                scores[0].tolist(),
                indices[0].tolist()
            )

        else:

            scores = (
                self.vectors @ query_vector[0]
            ).astype(float)

            order = np.argsort(scores)[::-1]

            semantic_results = (
                (float(scores[i]), int(i))
                for i in order
            )

        question_tokens = self._tokens(question)
        results = []

        # Hybrid scoring
        for semantic_score, idx in semantic_results:

            if idx < 0:
                continue

            record = self.records[idx].copy()

            record_text = record.get("text", "")
            metadata = record.get("metadata", {})

            record_tokens = self._tokens(record_text)

            # Keyword matching
            if question_tokens:
                overlap = len(
                    question_tokens & record_tokens
                )

                keyword_score = overlap / len(question_tokens)
            else:
                keyword_score = 0

            # Category matching
            category = str(
                metadata.get("category", "")
            ).lower()

            category_keywords = {
                "contact": [
                    "contact", "phone", "number", "email",
                    "address", "reach", "call"
                ],
                "fees": [
                    "fee", "fees", "cost", "payment", "charges"
                ],
                "hostel": [
                    "hostel", "accommodation", "room", "stay"
                ],
                "documents": [
                    "document", "certificate", "marksheet",
                    "papers", "required"
                ],
                "admission": [
                    "admission", "application", "eligibility",
                    "enquiry", "enrollment"
                ],
                "programmes": [
                    "course", "programme", "program",
                    "degree", "branch"
                ]
            }

            category_bonus = 0

            for category_name, keywords in category_keywords.items():

                if (
                    category_name in category
                    and any(word in question.lower() for word in keywords)
                ):
                    category_bonus = 0.05
                    break

            # Final relevance score
            hybrid_score = (
                float(semantic_score)
                + (0.12 * keyword_score)
                + category_bonus
            )

            record["score"] = hybrid_score
            record["semantic_score"] = float(semantic_score)
            record["keyword_score"] = float(keyword_score)

            results.append(record)

        # Highest relevance first
        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]

    def confident_results(
        self,
        question: str,
        top_k: int = TOP_K
    ) -> list[dict]:

        return [
            record
            for record in self.search(question, top_k)
            if record["score"] >= MIN_SIMILARITY
        ]
