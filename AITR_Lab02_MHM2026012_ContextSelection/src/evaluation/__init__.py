"""
src/evaluation/__init__.py - Retrieval and coverage evaluation metrics.
Calculates Evidence Recall, Full-Coverage Rate, Precision, Token/Word accounting, and Coverage/Token.
"""

from typing import List, Dict, Any, Set
import re

def count_words_and_tokens(text: str) -> Dict[str, int]:
    """
    Counts words (whitespace split) and estimates tokens using a 1.33 multiplier standard in NLP.
    """
    words = len(re.findall(r"\S+", text))
    # Standard conservative token multiplier for English Wikipedia prose (~1.3 tokens per word)
    tokens = int(round(words * 1.3))
    return {
        "words": max(words, 1),
        "tokens": max(tokens, 1)
    }

def compute_retrieval_metrics(
    selected_indices: List[int],
    gold_indices: List[int],
    candidates: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Computes rigorous retrieval metrics given selected candidate indices and gold indices.
    """
    selected_set: Set[int] = set(selected_indices)
    gold_set: Set[int] = set(gold_indices)

    if not gold_set:
        raise ValueError("Gold indices set cannot be empty.")

    hits = len(selected_set & gold_set)
    k = len(selected_indices)

    # 1. Evidence Recall: fraction of gold paragraphs captured
    recall = hits / float(len(gold_set))

    # 2. Full Coverage Rate: 1.0 if ALL gold paragraphs captured, else 0.0
    full_coverage = 1.0 if gold_set.issubset(selected_set) else 0.0

    # 3. Precision: fraction of selected paragraphs that are gold
    precision = (hits / float(k)) if k > 0 else 0.0

    # 4. Input Tokens / Words of selected context
    selected_text = " ".join([f"{candidates[i]['title']} {candidates[i]['text']}" for i in selected_indices])
    counts = count_words_and_tokens(selected_text)
    words = counts["words"]
    tokens = counts["tokens"]

    # 5. Coverage per 1,000 tokens (Primary efficiency metric)
    coverage_per_1k_tokens = (recall / float(tokens)) * 1000.0 if tokens > 0 else 0.0

    return {
        "k_selected": k,
        "evidence_recall": recall,
        "full_coverage": full_coverage,
        "precision": precision,
        "selected_words": words,
        "selected_tokens": tokens,
        "coverage_per_1000_tokens": coverage_per_1k_tokens
    }
