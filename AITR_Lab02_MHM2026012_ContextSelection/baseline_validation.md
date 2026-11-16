# Baseline Verification & Reproduction Report (baseline_validation.md)

**Project**: Fixed-k versus Adaptive-k Context Selection for Multi-Hop QA: An Evidence-Coverage and Token-Efficiency Study  
**Gate**: Gate G2 (Baseline Verification Approval)  
**Status**: `[VERIFIED_APPROVED]`  
**Execution Date**: 2026-11-05  

---

## 1. Objective of Gate G2
Before conducting any novel comparison or adaptive context selection experiment, the direct BM25 retrieval baseline was implemented, executed on the 500-question HotpotQA validation partition, and verified across all four non-negotiable criteria.

---

## 2. Baseline Verification Checklist & Empirical Results

| Check Item | Description | Pre-Test Requirement | Measured Value from Code Output | Status |
| :--- | :--- | :--- | :--- | :--- |
| **B-01: Metric Engine Sanity** | Evaluated on hand-made synthetic corner cases in `tests/test_evaluation.py`. | Partial recall, full coverage, and zero-selected corner cases match mathematical definitions. | All 5 unit tests passed in 0.69s. | `[VERIFIED_PASS]` |
| **B-02: Leakage Audit** | Blanked all `is_gold` metadata flags from candidates and re-ran retrieval ranking. | Output ranking and scores must be bit-for-bit identical regardless of gold label metadata presence. | Identical rankings and scores across all 500 questions. | `[VERIFIED_PASS]` |
| **B-03: Upper Bound Sanity** | Evaluated BM25 at $k=10$ on the 10-paragraph candidate pool. | Must achieve 100% Evidence Recall and 100% Full-Coverage Rate. | **Recall = 1.0000, Full Coverage = 1.0000**. | `[VERIFIED_PASS]` |
| **B-04: Lower Bound Control** | Random selection control at $k \in \{1, 3, 5\}$ averaged across 5 random seeds. | Must establish chance-level reference performance below informed retrieval. | **$k=1$: Recall 0.1070, Full Cov 0.0000**<br>**$k=3$: Recall 0.3046, Full Cov 0.0660**<br>**$k=5$: Recall 0.5008, Full Cov 0.2252** | `[VERIFIED_RECORDED]` |
| **B-05: Execution Determinism** | Re-ran ranking pipeline twice on identical input text. | Repeated runs must return identical sorted rankings and scores. | 100% identical outputs across runs. | `[VERIFIED_PASS]` |

---

## 3. Discrepancy & Anomaly Log

- **Anomaly 1 (Corrupted rows in HotpotQA validation set)**:
  - *Observation*: During raw parquet loading, rows 27, 222, 239, 276, and 466 contained fewer than 10 candidate paragraphs (ranging from 2 to 5 paragraphs).
  - *Resolution*: Updated ingestion logic in `src/data/__init__.py` to skip truncated rows deterministically, inspecting 505 rows to yield exactly 500 valid 10-paragraph questions.
  - *Integrity Note*: Logged in `results/raw/sanity.txt` and `ai_assistance_log.md`.

---

## 4. Gate G2 Sign-Off Decision
- **Approval Decision**: **APPROVED**. The baseline satisfies all sanity, bounding, determinism, and leakage conditions. Proceed to Gate G3 main experiment.
