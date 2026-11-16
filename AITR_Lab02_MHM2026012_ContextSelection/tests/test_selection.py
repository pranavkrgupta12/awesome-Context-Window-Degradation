"""
tests/test_selection.py - Unit tests for context selection algorithms (Fixed-k and Score-Gap Adaptive-k Proxy).
"""

import pytest
from src.selection import select_fixed_k, select_adaptive_k


def test_fixed_k_selection():
    indices = [5, 2, 8, 1, 9, 0, 3, 4, 7, 6]
    assert select_fixed_k(indices, 1) == [5]
    assert select_fixed_k(indices, 3) == [5, 2, 8]
    assert select_fixed_k(indices, 5) == [5, 2, 8, 1, 9]
    assert select_fixed_k(indices, 10) == indices
    assert select_fixed_k(indices, 0) == []
    assert select_fixed_k(indices, -1) == []


def test_adaptive_k_sharp_drop():
    # Big drop after index 1 (between 9.0 and 3.0) -> selects top 2
    indices = [0, 1, 2, 3, 4]
    scores = [10.0, 9.0, 3.0, 2.5, 1.0]
    selected, k_star = select_adaptive_k(indices, scores)
    assert k_star == 2
    assert selected == [0, 1]


def test_adaptive_k_drop_at_start():
    # Big drop right after top-1 -> selects top 1
    indices = [0, 1, 2, 3]
    scores = [15.0, 4.0, 3.5, 3.0]
    selected, k_star = select_adaptive_k(indices, scores)
    assert k_star == 1
    assert selected == [0]


def test_adaptive_k_flat_scores():
    # Uniform / flat scores -> fallback k=3
    indices = list(range(10))
    scores = [1.0] * 10
    selected, k_star = select_adaptive_k(indices, scores, fallback_k=3)
    assert k_star == 3
    assert selected == [0, 1, 2]


def test_adaptive_k_one_candidate():
    # Exactly one candidate -> returns that candidate with k=1
    indices = [42]
    scores = [5.5]
    selected, k_star = select_adaptive_k(indices, scores)
    assert k_star == 1
    assert selected == [42]


def test_adaptive_k_unsorted_raises():
    # Unsorted scores must raise ValueError
    indices = [0, 1, 2]
    scores = [1.0, 5.0, 2.0]
    with pytest.raises(ValueError, match="sorted in descending order"):
        select_adaptive_k(indices, scores)


def test_adaptive_k_tied_largest_gaps():
    # Two identical gaps:
    # gap at index 0: 10.0 - 7.0 = 3.0
    # gap at index 1: 7.0 - 4.0 = 3.0
    # Tied largest gaps should pick the first occurrence (k=1)
    indices = [0, 1, 2, 3]
    scores = [10.0, 7.0, 4.0, 3.0]
    selected, k_star = select_adaptive_k(indices, scores)
    assert k_star == 1
    assert selected == [0]


def test_adaptive_k_nan_raises():
    # NaN score must raise ValueError
    indices = [0, 1, 2]
    scores = [5.0, float("nan"), 1.0]
    with pytest.raises(ValueError, match="finite numeric values"):
        select_adaptive_k(indices, scores)


def test_adaptive_k_length_mismatch_raises():
    indices = [0, 1]
    scores = [5.0, 3.0, 1.0]
    with pytest.raises(ValueError, match="same length"):
        select_adaptive_k(indices, scores)
