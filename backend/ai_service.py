import math
import re
from collections import Counter

NOTES = [
    {
        "id": 1,
        "text": "Binary search requires a sorted array and repeatedly halves the search range using a midpoint comparison.",
    },
    {
        "id": 2,
        "text": "Insertion sort builds a sorted list one element at a time by shifting larger elements to the right.",
    },
    {
        "id": 3,
        "text": "FastAPI uses Pydantic models to validate request bodies and automatically generates Swagger documentation.",
    },
    {
        "id": 4,
        "text": "SQL joins combine rows from two tables using a matching column, such as inner join, left join, and full join.",
    },
    {
        "id": 5,
        "text": "Prompt engineering structures a task, context, constraints, and desired output format to guide an LLM's response.",
    },
]

VOCABULARY = [
    "sort", "search", "binary", "insertion", "sql", "join",
    "fastapi", "pydantic", "prompt", "llm", "database", "validate",
]

STOP_WORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is",
    "are", "with", "using", "from", "by", "as", "this", "that", "it",
    "into", "one", "each", "up", "be", "can", "at", "two", "how"
}


def _tokens(text: str):
    """Lower-case and split on every run of non-letter/non-digit characters."""
    return [token for token in re.split(r"[^A-Za-z0-9]+", text.lower()) if token]


def _mock_topic(raw_text: str) -> str:
    # Documented rule: use the first non-empty line as the title/topic.
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if lines:
        topic = re.sub(r"[^A-Za-z0-9\s-]", "", lines[0]).strip()
        if topic:
            return topic[:100]

    words = [w for w in _tokens(raw_text) if len(w) > 2 and w not in STOP_WORDS]
    return Counter(words).most_common(1)[0][0] if words else "untitled"


def summarize_notes(raw_text: str) -> dict:
    """Return exactly topic, key_points and difficulty using deterministic mock rules."""
    if not raw_text.strip():
        return {
            "topic": "untitled",
            "key_points": [],
            "difficulty": "easy",
        }

    sentences = re.split(r"[.!?]+", raw_text)
    key_points = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            key_points.append(sentence)
        if len(key_points) == 3:
            break

    word_count = len(_tokens(raw_text))
    if word_count < 40:
        difficulty = "easy"
    elif word_count <= 100:
        difficulty = "medium"
    else:
        difficulty = "hard"

    return {
        "topic": _mock_topic(raw_text),
        "key_points": key_points,
        "difficulty": difficulty,
    }


def mock_embed(text: str) -> list[float]:
    """Build the required 12-dimensional fixed-vocabulary word-count vector."""
    tokens = _tokens(text)
    counts = Counter(tokens)
    return [float(counts.get(word, 0)) for word in VOCABULARY]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity from first principles with zero-vector safety."""
    dot_product = 0.0
    magnitude_a_squared = 0.0
    magnitude_b_squared = 0.0

    for a, b in zip(vec_a, vec_b):
        dot_product += a * b
        magnitude_a_squared += a * a
        magnitude_b_squared += b * b

    magnitude_a = math.sqrt(magnitude_a_squared)
    magnitude_b = math.sqrt(magnitude_b_squared)

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def semantic_search(query: str, limit: int = 5):
    """Rank the fixed notes by deterministic mock cosine similarity."""
    query_vector = mock_embed(query)
    scored = []

    for note in NOTES:
        score = cosine_similarity(query_vector, mock_embed(note["text"]))
        scored.append({
            "id": note["id"],
            "text": note["text"],
            "score": score,
        })

    # Stable descending score; Python's sort preserves original id order for ties.
    scored.sort(key=lambda item: item["score"], reverse=True)

    if all(value == 0 for value in query_vector):
        return scored

    return scored[:max(1, min(limit, len(scored)))]
