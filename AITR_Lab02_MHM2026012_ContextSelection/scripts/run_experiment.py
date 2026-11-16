"""
scripts/run_experiment.py - Executes the full factorial context selection experiment on 500 HotpotQA questions.
Evaluates:
  2 Retrievers: BM25 and TF-IDF
  5 Selection Methods: fixed_1, fixed_3, fixed_5, fixed_10, adaptive_k
Outputs:
  - results/raw/experiment_runs.jsonl
  - results/tables/results.csv
  - results/raw/experiment_integrity.txt
"""

import sys
import os
import time
import json
import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data import load_and_validate_dataset
from src.retrieval import BM25Retriever, TFIDFRetriever
from src.selection import select_fixed_k, select_adaptive_k
from src.evaluation import compute_retrieval_metrics

def main():
    print("=" * 65)
    print("EXECUTING MAIN FACTORIAL CONTEXT SELECTION EXPERIMENT")
    print("=" * 65)
    
    os.makedirs(os.path.join("results", "raw"), exist_ok=True)
    os.makedirs(os.path.join("results", "tables"), exist_ok=True)
    
    # 1. Load dataset (500 valid questions)
    records, summary = load_and_validate_dataset(n_samples=500)
    print(f"Loaded {len(records)} verified records.")

    # 2. Instantiate retrievers
    retrievers = {
        "BM25": BM25Retriever(),
        "TF-IDF": TFIDFRetriever()
    }
    
    fixed_k_values = [1, 3, 5, 10]
    
    jsonl_path = os.path.join("results", "raw", "experiment_runs.jsonl")
    csv_path = os.path.join("results", "tables", "results.csv")
    
    rows = []
    
    start_total_time = time.time()
    
    with open(jsonl_path, "w", encoding="utf-8") as jsonl_file:
        for rec in tqdm(records, desc="Processing Questions"):
            q_id = rec["id"]
            question = rec["question"]
            candidates = rec["candidates"]
            gold_indices = [i for i, c in enumerate(candidates) if c["is_gold"]]
            multi_flag = rec["is_multi_evidence"]
            
            for ret_name, retriever in retrievers.items():
                # Measure retrieval ranking latency
                t0 = time.perf_counter()
                ranked_idx, sorted_scores = retriever.rank(question, candidates)
                rank_latency = time.perf_counter() - t0
                
                # --- Condition A: Fixed-k (1, 3, 5, 10) ---
                for k in fixed_k_values:
                    t_sel0 = time.perf_counter()
                    selected = select_fixed_k(ranked_idx, k)
                    sel_latency = time.perf_counter() - t_sel0
                    total_latency_ms = (rank_latency + sel_latency) * 1000.0
                    
                    m = compute_retrieval_metrics(selected, gold_indices, candidates)
                    
                    row = {
                        "id": q_id,
                        "retriever": ret_name,
                        "method": f"fixed_{k}",
                        "k_selected": m["k_selected"],
                        "recall": m["evidence_recall"],
                        "full_coverage": m["full_coverage"],
                        "precision": m["precision"],
                        "words": m["selected_words"],
                        "tokens": m["selected_tokens"],
                        "coverage_per_1000_tokens": m["coverage_per_1000_tokens"],
                        "latency_ms": round(total_latency_ms, 3),
                        "multi_evidence_flag": multi_flag,
                        "question_type": rec["type"]
                    }
                    rows.append(row)
                    jsonl_file.write(json.dumps(row) + "\n")
                    
                # --- Condition B: Score-Gap Adaptive-k Proxy ---
                t_sel0 = time.perf_counter()
                selected_adapt, k_star = select_adaptive_k(ranked_idx, sorted_scores, max_k=10, fallback_k=3)
                sel_latency = time.perf_counter() - t_sel0
                total_latency_ms = (rank_latency + sel_latency) * 1000.0
                
                m = compute_retrieval_metrics(selected_adapt, gold_indices, candidates)
                
                row = {
                    "id": q_id,
                    "retriever": ret_name,
                    "method": "Score-Gap Adaptive-k Proxy",
                    "k_selected": m["k_selected"],
                    "recall": m["evidence_recall"],
                    "full_coverage": m["full_coverage"],
                    "precision": m["precision"],
                    "words": m["selected_words"],
                    "tokens": m["selected_tokens"],
                    "coverage_per_1000_tokens": m["coverage_per_1000_tokens"],
                    "latency_ms": round(total_latency_ms, 3),
                    "multi_evidence_flag": multi_flag,
                    "question_type": rec["type"]
                }
                rows.append(row)
                jsonl_file.write(json.dumps(row) + "\n")
                
    elapsed_total = time.time() - start_total_time
    print(f"\nExperiment execution finished in {elapsed_total:.2f} seconds.")
    
    # Save CSV
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"Saved results dataframe to: {csv_path} (Shape: {df.shape})")
    
    # --- Integrity Audits ---
    expected_rows = len(records) * len(retrievers) * 5  # 500 * 2 * 5 = 5000
    actual_rows = len(df)
    duplicates = df.duplicated(subset=["id", "retriever", "method"]).sum()
    nan_counts = df.isna().sum().to_dict()
    has_nans = any(v > 0 for v in nan_counts.values())
    
    # Range validations
    recall_valid = (df["recall"].between(0.0, 1.0)).all()
    cov_valid = (df["full_coverage"].isin([0.0, 1.0])).all()
    prec_valid = (df["precision"].between(0.0, 1.0)).all()
    tokens_valid = (df["tokens"] > 0).all()
    latency_valid = (df["latency_ms"] >= 0.0).all()
    
    integrity_report = [
        "=" * 65,
        "EXPERIMENT DATA INTEGRITY AUDIT",
        "=" * 65,
        f"Expected Row Count   : {expected_rows}",
        f"Actual Row Count     : {actual_rows} -> {'[MATCHED]' if actual_rows == expected_rows else '[MISMATCH]'}",
        f"Duplicate Keys Check : {duplicates} duplicates -> {'[PASSED]' if duplicates == 0 else '[FAILED]'}",
        f"NaN / Missing Values : {'[NONE - PASSED]' if not has_nans else str(nan_counts)}",
        "-" * 65,
        "NUMERICAL BOUND VALIDATIONS:",
        f"  Recall in [0, 1]          : {recall_valid} -> {'[PASSED]' if recall_valid else '[FAILED]'}",
        f"  Full Coverage in {{0, 1}}   : {cov_valid} -> {'[PASSED]' if cov_valid else '[FAILED]'}",
        f"  Precision in [0, 1]       : {prec_valid} -> {'[PASSED]' if prec_valid else '[FAILED]'}",
        f"  Selected Tokens > 0       : {tokens_valid} -> {'[PASSED]' if tokens_valid else '[FAILED]'}",
        f"  Latency (ms) >= 0         : {latency_valid} -> {'[PASSED]' if latency_valid else '[FAILED]'}",
        "=" * 65,
        f"INTEGRITY STATUS     : {'[VERIFIED_PASS]' if (actual_rows == expected_rows and duplicates == 0 and not has_nans and recall_valid) else '[FAILED]'}",
        "=" * 65
    ]
    report_text = "\n".join(integrity_report)
    print(report_text)
    
    integrity_file = os.path.join("results", "raw", "experiment_integrity.txt")
    with open(integrity_file, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")
    print(f"Saved integrity report to: {integrity_file}")

if __name__ == "__main__":
    main()
