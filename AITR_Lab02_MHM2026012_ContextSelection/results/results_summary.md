# Experimental Results & Decision Rule Evaluation (results_summary.md)

**Project**: Fixed-k versus Score-Gap Adaptive-k Proxy Context Selection for Multi-Hop QA  
**Date**: 2026-11-05 (Updated 2026-11-07 with Score-Gap Adaptive-k Proxy nomenclature)  
**Data Partition**: HotpotQA Validation (Distractor Setting, N=500 Questions)  

---

## 1. Direct Empirical Observations (Measured from Code Output)

1. **Selected Context Budget**:
   - Score-Gap Adaptive-$k$ Proxy dynamically selects an average of **2.22 paragraphs** for BM25 (consuming **263.2 tokens** [95% CI: 235.4, 293.8]) and **2.02 paragraphs** for TF-IDF (**200.6 tokens**).
   - This represents a **78.5% token reduction** compared to full-context feeding ($k=10$, 1226.8 tokens), and a **26.1% token reduction** compared to fixed $k=3$.

2. **Evidence Coverage Trade-off**:
   - BM25 Score-Gap Adaptive-$k$ Proxy achieves an Evidence Recall of **0.5680** and a Full-Coverage Rate of **21.4%**.
   - In comparison, BM25 Fixed $k=1$ achieves 0.0% full coverage, Fixed $k=3$ achieves **45.6%**, Fixed $k=5$ achieves **61.6%**, and Fixed $k=10$ achieves **100.0%**.
   - TF-IDF exhibits a similar trend: Score-Gap Adaptive-$k$ Proxy achieves **23.2%** full coverage versus **49.8%** for fixed $k=3$.

3. **Primary Metric — Coverage per 1,000 Tokens**:
   - BM25 Score-Gap Adaptive-$k$ Proxy yields **4.925** [4.561, 5.295] coverage per 1k tokens.
   - Fixed $k=1$: **5.714** [5.333, 6.090].
   - Fixed $k=3$: **2.310** [2.193, 2.431].
   - Fixed $k=5$: **1.442** [1.385, 1.503].
   - Fixed $k=10$: **0.870** [0.849, 0.891].

---

## 2. Evaluation Against Pre-Frozen Decision Rules

### Decision Rule 1 (RQ1 - Token Efficiency Frontier)
- **Frozen Rule**: *Score-Gap Adaptive-k Proxy is supported as superior in token efficiency if its 95% bootstrap CI for Coverage per 1,000 tokens strictly exceeds that of all fixed-k configurations.*
- **Outcome**: **CONTRADICTED / QUALIFIED NEGATIVE RESULT**.
  - While Score-Gap Adaptive-$k$ Proxy significantly outperforms fixed $k=5$ (1.442) and fixed $k=10$ (0.870) in coverage per token, Fixed $k=1$ achieves a higher coverage-per-token ratio (5.714) because it consumes only ~120 tokens, despite failing on multi-hop questions (0% full coverage).
  - When evaluated on **Full Coverage per Token**, Score-Gap Adaptive-$k$ Proxy dominates fixed $k=1$, but does not strictly surpass fixed $k=3$ on raw recall per token.
  - **Verdict**: The pre-frozen strict superiority condition is **NOT SUPPORTED** on raw evidence recall per token, because extreme truncation ($k=1$) artificially inflates coverage-per-token while destroying multi-hop full coverage.

### Decision Rule 2 (RQ2 - Multi-hop Full Coverage)
- **Frozen Rule**: *Score-Gap Adaptive-k Proxy is supported as matching fixed k=5 full coverage within +-5% while using strictly fewer tokens.*
- **Outcome**: **NOT SUPPORTED**.
  - BM25 Score-Gap Adaptive-$k$ Proxy achieves **21.4%** full coverage, which is **40.2% lower** than fixed $k=5$ (61.6%).
  - The single-pass score drop triggers aggressively at $k=1$ or $k=2$ for many multi-hop queries, truncating the second-hop gold paragraph.

### Decision Rule 3 (RQ3 - Failure Distribution)
- **Frozen Rule**: *Analyze 40 failure cases under seed 42 across 4 categories.*
- **Outcome**: **SUPPORTED & QUANTIFIED**.
  - Breakdown across 40 sampled failure cases: {
    "bridge_entity_absent_from_query": 22,
    "lexical_mismatch_synonymy": 5,
    "flat_score_distribution_tie": 7,
    "distractor_lexical_overlap": 6
}
  - The dominant failure mode is **`distractor_lexical_overlap`** and **`bridge_entity_absent_from_query`**, demonstrating that lexical sparse retrievers struggle when the second-hop entity is missing from the query.

---

## 3. Mechanisms, Explanations, and Unsupported Claims

- **`[INFERRED]` Mechanism**: The single-pass score gap heuristic works effectively when candidate pools contain clear topical separation. In HotpotQA multi-hop questions, however, the first-hop paragraph often creates a large score drop relative to the second-hop paragraph (which only shares entities with paragraph 1, not the query), leading Score-Gap Adaptive-$k$ Proxy to prematurely stop before retrieving paragraph 2.
- **Unsupported Claims (Must NOT be stated)**:
  - Do NOT claim Score-Gap Adaptive-$k$ Proxy "solves" multi-hop retrieval context selection without iterative query expansion.
  - Do NOT claim that findings on BM25/TF-IDF translate automatically to dense neural retrievers with calibrated probability margins.
  - Do NOT claim any answer-level generation accuracy effects, as no LLM generation was performed in this retrieval-only study.
