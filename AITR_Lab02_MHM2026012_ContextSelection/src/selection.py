"""
src/selection.py - Fixed-k and score-gap-based context selection.

The score-gap selector is inspired by the Adaptive-k principle described by
Taguchi et al. (EMNLP 2025), but this implementation is not claimed to be an
exact reproduction. In this project it is applied to BM25 and TF-IDF scores
and includes a project-specific fallback for flat score distributions.
"""

from typing import List, Tuple


def select_fixed_k(ranked_indices: List[int], k: int) -> List[int]:
    """Return the first k ranked candidate indices."""
    if k <= 0:
        return []
    return ranked_indices[:k]


def select_adaptive_k(
    ranked_indices: List[int],
    sorted_scores: List[float],
    max_k: int = 10,
    fallback_k: int = 3,
) -> Tuple[List[int], int]:
    """
    Select passages using the maximum consecutive score-gap heuristic.

    The input scores must be aligned with ranked_indices and sorted in
    descending order. Among the first `max_k` candidates, calculate

        gap_i = score_i - score_(i+1)

    and retain the candidates before the largest gap. The returned k is
    therefore the zero-based gap index plus one.

    Project-specific safeguards:
      * If there are no candidates, return ([], 0).
      * If there is one candidate, return that candidate.
      * If all considered consecutive gaps are exactly zero, select up to
        `fallback_k` candidates.

    `max_k=10` and `fallback_k=3` are experiment settings, not claimed here
    to be rules from Taguchi et al. (2025).

    Note:
        This function retains the name `select_adaptive_k` for compatibility
        with existing project code. In the paper, describe it as a
        "score-gap proxy inspired by Adaptive-k", not as a faithful
        implementation of the original method.
    """
    if len(ranked_indices) != len(sorted_scores):
        raise ValueError(
            "ranked_indices and sorted_scores must have the same length "
            "and refer to the same ranking."
        )

    if max_k <= 0 or not ranked_indices:
        return [], 0

    n = min(len(sorted_scores), max_k)
    scores = [float(score) for score in sorted_scores[:n]]

    if any(not (score == score and abs(score) != float("inf")) for score in scores):
        raise ValueError("sorted_scores must contain only finite numeric values.")

    if any(scores[i] < scores[i + 1] for i in range(n - 1)):
        raise ValueError("sorted_scores must be sorted in descending order.")

    if n == 1:
        return ranked_indices[:1], 1

    # Consecutive drops: s[0]-s[1], s[1]-s[2], ..., s[n-2]-s[n-1].
    score_drops = [
        scores[i] - scores[i + 1]
        for i in range(n - 1)
    ]

    # A flat score sequence has no positive score boundary.
    # This fallback is specific to our experiment, not attributed to the paper.
    if max(score_drops) == 0.0:
        k_star = min(max(1, fallback_k), n)
    else:
        # max() returns the first occurrence in a tie, matching argmax behavior.
        best_idx = max(range(len(score_drops)), key=score_drops.__getitem__)
        k_star = best_idx + 1

    selected = ranked_indices[:k_star]
    return selected, k_star
