"""
src/selection.py - Context selection algorithms: Fixed-k and single-pass Adaptive-k.
Implements the score-gap heuristic from Taguchi et al. (EMNLP 2025).
"""

from typing import List, Tuple
import numpy as np

def select_fixed_k(ranked_indices: List[int], k: int) -> List[int]:
    """
    Selects top-k candidate indices.
    """
    if k <= 0:
        return []
    return ranked_indices[:k]

def select_adaptive_k(
    ranked_indices: List[int],
    sorted_scores: List[float],
    max_k: int = 10,
    fallback_k: int = 3
) -> Tuple[List[int], int]:
    """
    Faithful implementation of Taguchi et al. (2025):
    Identifies the cutoff point k* by evaluating the maximum first discrete drop
    between consecutive sorted similarity scores:
        k* = argmax_{i in {1, ..., K_max - 1}} (s_i - s_{i+1})
    Returns:
        selected_indices: ranked_indices[:k*]
        k_selected: k*
    """
    n = min(len(sorted_scores), max_k)
    if n <= 1:
        return ranked_indices[:1], 1

    scores_arr = np.array(sorted_scores[:n], dtype=float)
    # Consecutive discrete score drops: s_0 - s_1, s_1 - s_2, ..., s_{n-2} - s_{n-1}
    score_drops = scores_arr[:-1] - scores_arr[1:]

    # Check for complete tie / zero drop across all candidates
    if np.allclose(score_drops, 0.0) or np.max(score_drops) <= 0.0:
        # Fallback when score distribution is uniform
        k_star = min(fallback_k, n)
    else:
        # argmax returns the first index of the maximum drop (0-indexed)
        best_idx = int(np.argmax(score_drops))
        k_star = best_idx + 1

    # Clamp k_star within [1, n]
    k_star = max(1, min(k_star, n))
    selected = ranked_indices[:k_star]
    return selected, k_star
