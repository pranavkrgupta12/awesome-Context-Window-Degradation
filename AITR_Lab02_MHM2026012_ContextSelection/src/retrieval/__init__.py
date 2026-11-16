"""
src/retrieval/__init__.py - Information retrieval models (BM25 and TF-IDF).
Guarantees strict zero-leakage: retrievers only receive candidate text and query text.
"""

from typing import List, Dict, Any, Tuple
import re
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def simple_tokenize(text: str) -> List[str]:
    """
    Standard lowercased whitespace and alphanumeric tokenizer for BM25.
    """
    return re.findall(r"\w+", text.lower())

class BM25Retriever:
    """
    Classical probabilistic lexical retriever using Okapi BM25.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def rank(self, query: str, candidates: List[Dict[str, str]]) -> Tuple[List[int], List[float]]:
        """
        Ranks candidate paragraphs for a query.
        candidates: List of dicts with 'title' and 'text'. (No gold labels permitted).
        Returns:
          ranked_indices: indices sorted in descending score order.
          sorted_scores: matching scores sorted in descending order.
        """
        corpus = [f"{c['title']} {c['text']}" for c in candidates]
        tokenized_corpus = [simple_tokenize(doc) for doc in corpus]
        tokenized_query = simple_tokenize(query)

        # Handle empty query edge case
        if not tokenized_query:
            return list(range(len(candidates))), [0.0] * len(candidates)

        bm25 = BM25Okapi(tokenized_corpus, k1=self.k1, b=self.b)
        scores = bm25.get_scores(tokenized_query)
        scores = np.array(scores, dtype=float)

        # Stable sort descending
        ranked_indices = np.argsort(-scores, kind="mergesort").tolist()
        sorted_scores = scores[ranked_indices].tolist()
        return ranked_indices, sorted_scores


class TFIDFRetriever:
    """
    Vector-space retriever using TF-IDF and cosine similarity.
    """
    def __init__(self, sublinear_tf: bool = True):
        self.sublinear_tf = sublinear_tf

    def rank(self, query: str, candidates: List[Dict[str, str]]) -> Tuple[List[int], List[float]]:
        """
        Ranks candidate paragraphs using sublinear TF-IDF and cosine similarity.
        """
        corpus = [f"{c['title']} {c['text']}" for c in candidates]
        all_texts = [query] + corpus

        vectorizer = TfidfVectorizer(
            tokenizer=simple_tokenize,
            token_pattern=None,
            sublinear_tf=self.sublinear_tf,
            lowercase=True
        )
        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]
            scores = cosine_similarity(query_vec, doc_vecs)[0]
        except ValueError:
            # Handles vocabulary empty edge cases
            scores = np.zeros(len(candidates), dtype=float)

        ranked_indices = np.argsort(-scores, kind="mergesort").tolist()
        sorted_scores = scores[ranked_indices].tolist()
        return ranked_indices, sorted_scores
