"""
tests/test_retrieval.py - Unit tests for retrievers, zero leakage, and determinism.
"""

import pytest
import copy
from src.retrieval import BM25Retriever, TFIDFRetriever

def make_sample_pool():
    query = "Where was Marie Curie born?"
    candidates = [
        {"title": "Albert Einstein", "text": "Albert Einstein was born in Ulm, Germany.", "is_gold": False},
        {"title": "Marie Curie", "text": "Marie Curie was born in Warsaw, Poland in 1867.", "is_gold": True},
        {"title": "Isaac Newton", "text": "Isaac Newton was an English mathematician and physicist.", "is_gold": False},
        {"title": "Warsaw", "text": "Warsaw is the capital and largest city of Poland.", "is_gold": True},
        {"title": "Quantum Mechanics", "text": "A fundamental theory in physics that provides a description of nature.", "is_gold": False}
    ]
    return query, candidates

def test_retriever_ranking_quality():
    query, candidates = make_sample_pool()
    bm25 = BM25Retriever()
    ranked_idx, scores = bm25.rank(query, candidates)
    
    # Candidate 1 (Marie Curie) should score highest due to exact lexical match
    assert ranked_idx[0] == 1
    assert scores[0] > scores[1]
    
    tfidf = TFIDFRetriever()
    ranked_idx_tfidf, scores_tfidf = tfidf.rank(query, candidates)
    assert ranked_idx_tfidf[0] == 1
    assert scores_tfidf[0] > scores_tfidf[1]

def test_leakage_invariance():
    """
    STRICT LEAKAGE AUDIT:
    Verifies that the presence, absence, or modification of the 'is_gold' metadata flag
    produces 100% bit-for-bit identical ranking and scores.
    """
    query, candidates = make_sample_pool()
    bm25 = BM25Retriever()
    orig_idx, orig_scores = bm25.rank(query, candidates)

    # Make copy and blank all gold fields
    stripped_candidates = copy.deepcopy(candidates)
    for c in stripped_candidates:
        del c["is_gold"]

    stripped_idx, stripped_scores = bm25.rank(query, stripped_candidates)
    assert orig_idx == stripped_idx
    assert orig_scores == stripped_scores

    # Adversarial test: set distractor as gold and gold as false
    flipped_candidates = copy.deepcopy(candidates)
    for c in flipped_candidates:
        c["is_gold"] = not c["is_gold"]

    flipped_idx, flipped_scores = bm25.rank(query, flipped_candidates)
    assert orig_idx == flipped_idx
    assert orig_scores == flipped_scores

def test_determinism():
    """
    Repeated runs on identical inputs must yield identical numerical rankings and scores.
    """
    query, candidates = make_sample_pool()
    bm25 = BM25Retriever()
    r1, s1 = bm25.rank(query, candidates)
    r2, s2 = bm25.rank(query, candidates)
    assert r1 == r2
    assert s1 == s2
