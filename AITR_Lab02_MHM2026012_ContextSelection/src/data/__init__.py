"""
src/data/__init__.py - Data ingestion, schema validation, and paragraph preparation for HotpotQA.
Ensures zero data leakage: gold labels/titles are strictly isolated from retriever inputs.
"""

import os
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

HOTPOTQA_PARQUET_URL = (
    "https://huggingface.co/datasets/hotpotqa/hotpot_qa/resolve/"
    "refs%2Fconvert%2Fparquet/distractor/validation/0000.parquet"
)
DEFAULT_CACHE_PATH = os.path.join("data", "raw", "hotpot_dev_distractor.parquet")

def load_raw_dataset(cache_path: str = DEFAULT_CACHE_PATH) -> pd.DataFrame:
    """
    Loads HotpotQA validation set (distractor configuration).
    Caches the parquet file locally in data/raw/ if not already present.
    """
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    if not os.path.exists(cache_path):
        print(f"Downloading HotpotQA validation split from: {HOTPOTQA_PARQUET_URL}")
        df = pd.read_parquet(HOTPOTQA_PARQUET_URL)
        df.to_parquet(cache_path, index=False)
        print(f"Cached raw parquet to: {cache_path}")
    else:
        df = pd.read_parquet(cache_path)
    return df

def validate_and_parse_record(row: pd.Series) -> Dict[str, Any]:
    """
    Validates the schema and extracts clean question and candidate pools.
    Strictly verifies:
      1. Required keys exist and are non-null.
      2. Exactly 10 candidate paragraphs are present.
      3. Supporting facts specify at least one gold title.
    """
    required_fields = ["id", "question", "answer", "type", "supporting_facts", "context"]
    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            raise ValueError(f"Record {row.get('id', 'unknown')} missing required field: {field}")
            
    q_id = str(row["id"])
    question = str(row["question"]).strip()
    answer = str(row["answer"]).strip()
    q_type = str(row.get("type", "unknown"))
    
    context = row["context"]
    titles = list(context["title"])
    sentences_list = list(context["sentences"])
    
    if len(titles) != 10:
        raise ValueError(f"Record {q_id} has {len(titles)} candidate paragraphs; expected 10.")
        
    sup_facts = row["supporting_facts"]
    sup_titles = list(sup_facts["title"])
    gold_titles = set(sup_titles)
    
    if len(gold_titles) == 0:
        raise ValueError(f"Record {q_id} has 0 gold supporting titles.")
        
    paragraphs = []
    for t, sents in zip(titles, sentences_list):
        text = " ".join([s.strip() for s in sents if s.strip()])
        paragraphs.append({
            "title": t,
            "text": text,
            "is_gold": (t in gold_titles)
        })
        
    return {
        "id": q_id,
        "question": question,
        "answer": answer,
        "type": q_type,
        "gold_titles": sorted(list(gold_titles)),
        "num_gold": len(gold_titles),
        "is_multi_evidence": (len(gold_titles) >= 2),
        "candidates": paragraphs
    }

def load_and_validate_dataset(n_samples: int = 500, cache_path: str = DEFAULT_CACHE_PATH) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Loads and validates n_samples valid records from HotpotQA.
    Iterates through dataset until n_samples valid records with exactly 10 candidate paragraphs are collected.
    Returns parsed records and a validation summary dictionary.
    """
    df = load_raw_dataset(cache_path=cache_path)
    records = []
    skipped_records = []
    
    candidate_lengths = []
    gold_counts = []
    question_types = {}
    
    for idx, row in df.iterrows():
        try:
            rec = validate_and_parse_record(row)
            records.append(rec)
            candidate_lengths.append(len(rec["candidates"]))
            gold_counts.append(rec["num_gold"])
            q_type = rec["type"]
            question_types[q_type] = question_types.get(q_type, 0) + 1
            if len(records) >= n_samples:
                break
        except Exception as e:
            skipped_records.append({"row_index": int(idx), "id": str(row.get("id")), "reason": str(e)})
            
    summary = {
        "total_requested": n_samples,
        "total_valid_loaded": len(records),
        "total_inspected": len(records) + len(skipped_records),
        "skipped_records_count": len(skipped_records),
        "skipped_records": skipped_records,
        "candidate_lengths_min": min(candidate_lengths) if candidate_lengths else 0,
        "candidate_lengths_max": max(candidate_lengths) if candidate_lengths else 0,
        "candidate_lengths_all_10": all(cl == 10 for cl in candidate_lengths),
        "gold_counts_min": min(gold_counts) if gold_counts else 0,
        "gold_counts_max": max(gold_counts) if gold_counts else 0,
        "gold_ge_2_count": sum(1 for gc in gold_counts if gc >= 2),
        "gold_single_count": sum(1 for gc in gold_counts if gc == 1),
        "question_types": question_types
    }
    return records, summary
