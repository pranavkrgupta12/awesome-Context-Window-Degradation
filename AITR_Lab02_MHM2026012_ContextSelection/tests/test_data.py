"""
tests/test_data.py - Unit tests for data schema validation, parsing, and leakage guards.
"""

import pytest
import pandas as pd
from src.data import validate_and_parse_record

def make_mock_row(num_candidates=10, num_gold=2, missing_field=None):
    titles = [f"Article_{i}" for i in range(num_candidates)]
    sentences = [[f"This is sentence 1 of article {i}.", f"Sentence 2 of article {i}."] for i in range(num_candidates)]
    gold_titles = titles[:num_gold]
    
    data = {
        "id": "mock_id_001",
        "question": "Which article contains the answer?",
        "answer": "Article_0",
        "type": "bridge",
        "level": "hard",
        "supporting_facts": {
            "title": gold_titles,
            "sent_id": [0] * len(gold_titles)
        },
        "context": {
            "title": titles,
            "sentences": sentences
        }
    }
    if missing_field:
        del data[missing_field]
    return pd.Series(data)

def test_valid_record_parsing():
    row = make_mock_row(num_candidates=10, num_gold=2)
    parsed = validate_and_parse_record(row)
    
    assert parsed["id"] == "mock_id_001"
    assert len(parsed["candidates"]) == 10
    assert parsed["num_gold"] == 2
    assert parsed["is_multi_evidence"] is True
    assert parsed["gold_titles"] == ["Article_0", "Article_1"]
    
    # Check candidates structure
    gold_flags = [c["is_gold"] for c in parsed["candidates"]]
    assert sum(gold_flags) == 2
    assert gold_flags[0] is True
    assert gold_flags[1] is True
    assert gold_flags[2] is False

def test_missing_field_raises():
    row = make_mock_row(missing_field="question")
    with pytest.raises(ValueError, match="missing required field: question"):
        validate_and_parse_record(row)

def test_invalid_candidate_count_raises():
    row = make_mock_row(num_candidates=8)
    with pytest.raises(ValueError, match="expected 10"):
        validate_and_parse_record(row)

def test_zero_gold_raises():
    row = make_mock_row(num_candidates=10, num_gold=0)
    with pytest.raises(ValueError, match="0 gold supporting titles"):
        validate_and_parse_record(row)

def test_single_evidence_flag():
    row = make_mock_row(num_candidates=10, num_gold=1)
    parsed = validate_and_parse_record(row)
    assert parsed["num_gold"] == 1
    assert parsed["is_multi_evidence"] is False
