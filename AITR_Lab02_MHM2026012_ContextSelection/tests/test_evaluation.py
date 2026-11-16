"""
tests/test_evaluation.py - Unit tests for metric engine with hand-made edge cases.
"""

import pytest
from src.evaluation import compute_retrieval_metrics, count_words_and_tokens

def make_dummy_candidates(n=10):
    return [{"title": f"Doc_{i}", "text": f"This is short content for doc {i}."} for i in range(n)]

def test_hand_made_case_partial_recall():
    candidates = make_dummy_candidates(10)
    # Gold indices: [0, 1]. Selected: [0]
    metrics = compute_retrieval_metrics(
        selected_indices=[0],
        gold_indices=[0, 1],
        candidates=candidates
    )
    assert metrics["k_selected"] == 1
    assert metrics["evidence_recall"] == 0.5
    assert metrics["full_coverage"] == 0.0
    assert metrics["precision"] == 1.0
    assert metrics["selected_words"] > 0
    assert metrics["selected_tokens"] > 0
    assert metrics["coverage_per_1000_tokens"] > 0.0

def test_hand_made_case_full_coverage():
    candidates = make_dummy_candidates(10)
    # Gold: [0, 1]. Selected: [0, 1, 2]
    metrics = compute_retrieval_metrics(
        selected_indices=[0, 1, 2],
        gold_indices=[0, 1],
        candidates=candidates
    )
    assert metrics["k_selected"] == 3
    assert metrics["evidence_recall"] == 1.0
    assert metrics["full_coverage"] == 1.0
    assert metrics["precision"] == pytest.approx(2.0 / 3.0)

def test_hand_made_case_zero_selected():
    candidates = make_dummy_candidates(10)
    metrics = compute_retrieval_metrics(
        selected_indices=[],
        gold_indices=[0, 1],
        candidates=candidates
    )
    assert metrics["k_selected"] == 0
    assert metrics["evidence_recall"] == 0.0
    assert metrics["full_coverage"] == 0.0
    assert metrics["precision"] == 0.0

def test_empty_gold_raises():
    candidates = make_dummy_candidates(10)
    with pytest.raises(ValueError, match="Gold indices set cannot be empty"):
        compute_retrieval_metrics(
            selected_indices=[0],
            gold_indices=[],
            candidates=candidates
        )
