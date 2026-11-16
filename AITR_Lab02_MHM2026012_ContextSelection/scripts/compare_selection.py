"""
scripts/compare_selection.py - Evaluates old vs new select_adaptive_k implementations
across all 500 HotpotQA questions and both retrievers (BM25 and TF-IDF).
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data import load_and_validate_dataset
from src.retrieval import BM25Retriever, TFIDFRetriever
import src.selection as sel_new
import src.selection_old as sel_old


def main():
    print("=" * 65)
    print("COMPARING ADAPTIVE-K SELECTION: OLD VS REVISED IMPLEMENTATION")
    print("=" * 65)
    
    records, _ = load_and_validate_dataset(n_samples=500)
    retrievers = {"BM25": BM25Retriever(), "TF-IDF": TFIDFRetriever()}

    for name, ret in retrievers.items():
        diff_count = 0
        k_olds = []
        k_news = []
        for rec in records:
            ranked_idx, sorted_scores = ret.rank(rec["question"], rec["candidates"])
            _, k_o = sel_old.select_adaptive_k(ranked_idx, sorted_scores, max_k=10, fallback_k=3)
            _, k_n = sel_new.select_adaptive_k(ranked_idx, sorted_scores, max_k=10, fallback_k=3)
            k_olds.append(k_o)
            k_news.append(k_n)
            if k_o != k_n:
                diff_count += 1
        print(f"Retriever: {name}")
        print(f"  Total questions: {len(records)}")
        print(f"  Differing k: {diff_count}")
        print(f"  Mean k (old): {np.mean(k_olds):.4f}")
        print(f"  Mean k (new): {np.mean(k_news):.4f}")


if __name__ == "__main__":
    main()
