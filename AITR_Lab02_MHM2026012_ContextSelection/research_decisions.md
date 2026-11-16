# Research Decisions Log (research_decisions.md)

**Project**: Investigating Position-Dependent Context Degradation and Retrieval-Based Mitigation in Long-Context Question Answering  
**Course**: AI Tools for Research (Lab 02 / Second Paper)  
**Researcher**: Pranav Kumar Gupta (MHM2026012@iiita.ac.in)  
**Date Initialized**: 2026-11-05  
**Current Milestone**: Gate G1 (Research Brief & Workspace Launch)  

---

## 1. Project Status Summary

| Component | Status | Source / Notes |
| :--- | :--- | :--- |
| **Research Area** | `[VERIFIED]` | Context-Window Degradation and Retrieval Mitigation (Completed Lit Review) |
| **Literature Review** | `[VERIFIED]` | Completed and synthesized in `inputs/literature_review.md` |
| **Candidate Gaps** | `[VERIFIED]` | 5 testable gaps formulated; 3 top gaps ranked |
| **Research Question** | `[PROVISIONAL]` | Position $\times$ Context Length Degradation vs. Retrieval Mitigation |
| **Dataset Selection** | `[UNKNOWN]` | To be audited for license, length control, and leakage (Gate G2) |
| **Model Selection** | `[UNKNOWN]` | Dependent on hardware/API budget confirmation |
| **Baseline Method** | `[PROVISIONAL]` | Direct Long-Context QA (prompting with full distractor context) |
| **Experimental Protocol**| `[NOT FROZEN]` | Will freeze at Gate G2/G3 before viewing main experiment results |
| **Code Implementation** | `[NOT YET VERIFIED]` | Initial repo layout scaffolded; implementation begins in Gate G2 |
| **Experimental Results**| `[UNKNOWN]` | No main runs conducted yet |
| **Paper Manuscript** | `[NOT STARTED]` | Target: 6–10 page IEEE/ACM format |

---

## 2. Evidence Ledger Summary

- **`[VERIFIED]`**:
  - LLMs exhibit performance degradation when key evidence is situated in the middle of long input sequences (Lost in the Middle, Liu et al., 2024).
  - Standard NIAH evaluations with exact lexical matching can mask deeper semantic retrieval failures (NoLiMa, Modarressi et al., 2025).
  - Effective usable context window (MECW) is typically substantially shorter than advertised nominal capacity (Paulsen, 2025).
  - Distractor density and in-context feature placement significantly impact needle retrieval (DENIAHL, Dai et al., 2024).
  - Retrieval-Augmented Generation (RAG) and LongRAG reduce unnecessary context tokens but introduce trade-offs between local precision and global document coherence (Lewis et al., 2020; Zhao et al., 2024).
  - Dynamic context selection (Adaptive-k) can adapt token budgets to query requirements (Taguchi et al., 2025).

- **`[INFERRED]`**:
  - As irrelevant distractor context expands (from 2K to 16K tokens), the performance penalty for middle-positioned evidence ($D_{\text{position}}$) increases non-linearly.
  - Supplying only top-k retrieved chunks will reduce or eliminate position-dependent degradation, because the evidence is concentrated into a much smaller effective prompt window.
  - A trade-off exists where retrieval improves single-hop localized queries but may introduce retrieval error if distractors share semantic overlap with queries.

- **`[UNKNOWN]` (Pending Verification)**:
  - Exact token-level thresholds where selected LLM fails on middle-placed needles.
  - Exact latency and cost overhead of running dense retrieval + reranking vs. direct long-context prompting across $2\text{K} - 16\text{K}$ tokens.

---

## 3. Protocol Deviations Log

*Any change to frozen metrics, models, splits, prompts, or seeds after Gate G2 protocol freeze MUST be logged here.*

| Date | Proposed Change | Reason for Deviation | Impact on Prior Runs | Human Approval |
| :--- | :--- | :--- | :--- | :--- |
| **2026-11-07** | **Algorithm Clarification & Nomenclature Renaming**: Refactored `select_adaptive_k` in `src/selection.py` to pure Python with defensive checks (finite/NaN validation, descending sort check, dimension check) and explicit flat-score fallback ($k=3$). Renamed method throughout repo to **"Score-Gap Adaptive-k Proxy"**. | Author audit post-freeze. Clarifies that the score-gap heuristic applied to BM25/TF-IDF with flat fallback is an experimental proxy inspired by Taguchi et al. (2025), not an identical reproduction of their dense probability margin algorithm. | **Zero numerical change**: Verified empirically on all 500 questions for BM25 and TF-IDF (0 differing $k$ values; mean $k$ remains 2.2200 for BM25 and 2.0180 for TF-IDF; all recall, precision, tokens, and CIs identical). | **Approved by Author (2026-11-07)** |
| **2026-11-07** | **Post-Freeze Exploratory Addition of Fixed $k=2$ Baseline**: Evaluated fixed $k=2$ across all 500 questions for BM25 and TF-IDF, appending 1,000 records to `results/tables/results.csv`. | Matched-budget exploratory investigation. Because Score-Gap Adaptive-$k$ Proxy selects on average $k \approx 2.02$ (TF-IDF) and $k \approx 2.22$ (BM25), Fixed $k=2$ serves as the closest integer budget comparator to isolate whether Adaptive-$k$'s lower full coverage is a consequence of small budget size ($k \approx 2$) or dynamic cutoff error. | **Additive Only / Zero Modification**: All existing 5,000 rows in `results.csv` remain completely untouched. 1,000 new rows for `method: "fixed_2"` appended. Output generated in `results/tables/table3_matched_budget.csv` and `paper/table3_matched_budget.tex`. | **Approved by Author (2026-11-07)** |

---

## 4. Immediate Next Actions
1. Confirm researcher hardware (GPU/VRAM or Colab) and API budget.
2. Complete Gate G1 One-Page Research Brief.
3. Select and verify candidate dataset with zero leakage guarantee.
4. Implement minimal direct long-context baseline module and run sanity check test.
