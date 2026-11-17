
"""Concise answer generation for the DIEMS Admission Assistant."""

import re
import requests

from backend.config import LLM_API_KEY, LLM_API_URL, LLM_MODEL


FALLBACK = (
    "I couldn't find this information in my available DIEMS records. "
    "Please contact the DIEMS admission office for confirmation."
)


def extract_concise_answer(question: str, contexts: list[dict]) -> str:
    """
    Extract the most relevant sentences from retrieved records.
    Used when an AI API is not configured.
    """

    if not contexts:
        return FALLBACK

    stopwords = {
        "what", "is", "are", "the", "a", "an", "of", "in", "on",
        "for", "to", "and", "or", "with", "do", "does", "can",
        "i", "we", "you", "my", "your", "how", "much", "many",
        "tell", "me", "about", "please", "give", "information",
        "available", "there", "at", "does", "diems"
    }

    question_words = set(
        re.findall(r"[a-z0-9]+", question.lower())
    ) - stopwords

    candidates = []

    for record in contexts:
        text = record.get("text", "").strip()

        if not text:
            continue

        sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

        for position, sentence in enumerate(sentences):
            sentence = sentence.strip()

            if len(sentence.split()) < 3:
                continue

            words = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            overlap = len(question_words & words)

            score = overlap + (0.15 if position == 0 else 0)

            if score > 0:
                candidates.append((score, sentence, position))

        # Use the best available record if no sentence matches directly.
        if not candidates:
            for position, sentence in enumerate(sentences[:2]):
                sentence = sentence.strip()
                if len(sentence.split()) >= 3:
                    candidates.append((0, sentence, position))

    if not candidates:
        return FALLBACK

    candidates.sort(key=lambda item: (-item[0], item[2]))

    selected = []
    seen = set()
    total_words = 0

    for score, sentence, position in candidates:
        normalized = sentence.lower()

        if normalized in seen:
            continue

        word_count = len(sentence.split())

        if total_words + word_count > 65:
            continue

        selected.append(sentence)
        seen.add(normalized)
        total_words += word_count

        if len(selected) == 3:
            break

    if not selected:
        return FALLBACK

    return " ".join(selected)


def create_answer(question: str, contexts: list[dict]) -> tuple[str, str]:

    if not contexts:
        return FALLBACK, "fallback"

    context_text = "\n\n".join(
        f"[Source: {r.get('metadata', {}).get('source', 'Unknown')}; "
        f"Category: {r.get('metadata', {}).get('category', 'General')}]\n"
        f"{r.get('text', '')}"
        for r in contexts
    )

    # Retrieval-only mode: extract concise relevant information.
    if not (LLM_API_URL and LLM_API_KEY and LLM_MODEL):
        answer = extract_concise_answer(question, contexts)
        return answer, "retrieval-only"

    system_prompt = """
You are DIEMS College Admission Enquiry Assistant.

Instructions:
1. Give short, direct and accurate answers.
2. Answer only what the user asks.
3. Use only the provided DIEMS knowledge base.
4. Do not add unnecessary introductions or conclusions.
5. Do not repeat the question.
6. Avoid lengthy explanations.
7. Use bullet points only when listing multiple items.
8. If information is unavailable, say:
   "This information is not available in the current DIEMS records. Please contact the college."
9. Never invent information.
10. Keep answers within 2-4 sentences whenever possible.
11. Never use phrases like:
    "According to the DIEMS website",
    "As stated on the DIEMS website",
    "The DIEMS website mentions".
    Start directly with the answer.

Do not begin every answer with phrases like
"According to the knowledge base" or "Here is the information".
Sound like a helpful college admission assistant.
"""

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": (
                    f"AVAILABLE DIEMS INFORMATION:\n{context_text}\n\n"
                    f"STUDENT QUESTION: {question}\n\n"
                    "Give a concise and directly relevant answer."
                )
            }
        ],
        "temperature": 0.1,
        "max_tokens": 180
    }

    try:
        response = requests.post(
            LLM_API_URL,
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=45
        )

        response.raise_for_status()

        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()

        if not answer:
            raise ValueError("The AI returned an empty response.")

        return answer, "generative"

    except Exception:
        # Keep the chatbot functional if the AI service is unavailable.
        answer = extract_concise_answer(question, contexts)
        return answer, "retrieval-only"
