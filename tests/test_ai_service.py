import math

from backend.ai_service import cosine_similarity, mock_embed, semantic_search, summarize_notes


def test_empty_summary_has_required_shape():
    result = summarize_notes("   ")
    assert result == {"topic": "untitled", "key_points": [], "difficulty": "easy"}


def test_summary_is_deterministic_and_fixed_shape():
    text = "Binary search works. It uses sorted data."
    first = summarize_notes(text)
    second = summarize_notes(text)
    assert first == second
    assert set(first) == {"topic", "key_points", "difficulty"}


def test_mock_embed_is_exactly_12_dimensions():
    vector = mock_embed("binary search SQL LLM's unknown")
    assert len(vector) == 12
    assert vector[1] == 1.0  # search
    assert vector[2] == 1.0  # binary
    assert vector[4] == 1.0  # sql
    assert vector[9] == 1.0  # llm
    assert sum(vector) == 4.0


def test_mock_embed_does_not_match_sorted_as_sort():
    assert mock_embed("sorted") [0] == 0.0


def test_cosine_similarity_edges():
    vector = mock_embed("binary search")
    assert math.isclose(cosine_similarity(vector, vector), 1.0)
    assert cosine_similarity(mock_embed("binary"), mock_embed("sql")) == 0.0
    assert cosine_similarity(mock_embed(""), vector) == 0.0


def test_semantic_search_binary_query_ranks_note_one():
    results = semantic_search("binary search algorithm")
    assert results[0]["id"] == 1


def test_semantic_search_empty_query_returns_all_zero_scores():
    results = semantic_search("")
    assert [r["id"] for r in results] == [1, 2, 3, 4, 5]
    assert all(r["score"] == 0.0 for r in results)
