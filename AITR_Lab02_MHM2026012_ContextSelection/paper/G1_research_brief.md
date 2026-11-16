# Gate G1 Research Brief

**Course**: AI Tools for Research (Lab 02 / Second Paper)  
**Project Title**: Fixed-k versus Adaptive-k Context Selection for Multi-Hop QA: An Evidence-Coverage and Token-Efficiency Study  
**Author / Student**: Pranav Kumar Gupta (MHM2026012@iiita.ac.in), IIIT Allahabad  
**Date**: 2026-11-05  
**Milestone**: Gate G1 (Research Brief Approval)  

---

## 1. One-Page Research Brief Table

| Field | Project Information & Verified Specifications |
| :--- | :--- |
| **Review topic and key papers** | **Topic**: Context-window degradation, evidence coverage, and retrieval context selection.<br>**Key Papers**:<br>1. Taguchi et al. (EMNLP 2025): *Efficient Context Selection for Long-Context QA: No Tuning, No Iteration, Just Adaptive-k*<br>2. Liu et al. (TACL 2024): *Lost in the Middle: How Language Models Use Long Contexts*<br>3. Yang et al. (EMNLP 2018): *HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering*<br>4. Modarressi et al. (ICML 2025): *NoLiMa: Long-Context Evaluation Beyond Literal Matching*<br>5. Paulsen (AAIML 2026): *Context Is What You Need: The Maximum Effective Context Window for Real World Limits of LLMs* |
| **Research gap** | **Source Evidence**: Review Section 6.2 & Section 9.2 ("Evidence Coverage as a First-Class Metric").<br>**Specific Gap**: Fixed-budget retrieval ($k \in \{1, 3, 5, 10\}$) forces an arbitrary trade-off between under-retrieving critical evidence on multi-hop questions (low full-coverage rate) and over-retrieving irrelevant distractor paragraphs (token inflation and noise). Whether single-pass score-drop Adaptive-$k$ consistently optimizes the evidence coverage-per-token frontier across different sparse retrievers (BM25 vs. TF-IDF) without model fine-tuning remains uncharacterized under controlled multi-evidence splits. |
| **Research question** | **Primary RQ1**: Does Adaptive-$k$ context selection achieve a statistically superior evidence-coverage-per-1000-tokens trade-off compared to fixed-$k$ ($k \in \{1, 3, 5, 10\}$) across sparse retrieval backends?<br>**Sub-question RQ2**: How does the full-coverage rate of Adaptive-$k$ compare across single-evidence vs. multi-evidence (distributed $\ge 2$ gold paragraphs) queries?<br>**Sub-question RQ3 (Deeper Analysis)**: What failure modes predominate when necessary evidence is missed by Adaptive-$k$ (e.g., lexical mismatch, bridge entity absent from question, flat score distributions)? |
| **Study pathway** | **Pathway B (Controlled Comparative Study)**: Controlled factorial evaluation holding questions, candidate paragraph pools (10 paragraphs per query), tokenization, and evaluation protocol constant while varying retriever (BM25 vs. TF-IDF) and selection strategy (Fixed-$k$ vs. Adaptive-$k$). |
| **Dataset or measurement setup** | **Dataset**: HotpotQA (Yang et al., 2018), distractor setting, validation split, first 500 questions (fixed deterministically by question IDs).<br>**License**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).<br>**Setup**: Each sample contains 1 question, 10 candidate paragraphs (2 gold, 8 distractors), and sentence-level supporting fact annotations. Zero leakage: gold labels/titles stripped before passing to retriever. |
| **Baseline / comparators** | **Baseline**: Fixed-$k$ BM25 retrieval ($k=1, 3, 5, 10$).<br>**Comparators**:<br>1. Fixed-$k$ TF-IDF retrieval ($k=1, 3, 5, 10$).<br>2. Adaptive-$k$ selection on BM25 score distributions ($k = \arg\max_i (s_i - s_{i+1})$).<br>3. Adaptive-$k$ selection on TF-IDF score distributions.<br>4. Random-selection control (lower reference bound, averaged over 5 seeds). |
| **Primary metric and control** | **Primary Metric**: Evidence Coverage per 1,000 input tokens ($\frac{\text{Evidence Recall}}{\text{Selected Tokens}} \times 1000$).<br>**Secondary Metrics**: Evidence Recall (fraction of gold paragraphs retrieved), Full-Coverage Rate (fraction of questions where 100% of gold paragraphs are selected), Selection Precision, Input Word/Token Count, and Selection Latency (ms).<br>**Control & Uncertainty**: 95% bootstrap confidence intervals (1,000 resamples, fixed random seed 0). |
| **Computing and risks** | **Computing**: Local CPU execution; fast pilot on 500 samples requires $<10$ minutes wall-clock time and $<1$ GB RAM. No GPU required for sparse retrieval phase.<br>**Risks & Fallbacks**: If memory or execution time is constrained, fallback immediately to first 200 questions with protocol deviation recorded in `research_decisions.md`. If score distributions are degenerate/flat (ties), implement fallback to $k=3$ with clear diagnostic logging. |
| **First executable milestone** | Minimal runnable environment sanity check and HotpotQA schema loader verifying 500 questions, 10 paragraphs per question, and $\ge 2$ gold paragraphs per question with zero missing fields (`results/raw/sanity.txt`). |

---

## 2. Go / No-Go Decision & Fallback Plan

- **Go / No-Go Decision**: **GO**. 
  - Data access is confirmed via the official Hugging Face / HotpotQA distribution.
  - Dependencies (`datasets`, `rank_bm25`, `scikit-learn`, `numpy`, `scipy`) are installed and verified in `results/env_check.txt`.
  - The study operates purely on reproducible algorithmic heuristics, preventing API rate-limit failure risks during the primary comparative evaluation.

- **Pre-defined Fallbacks**:
  1. *Sample Size Fallback*: If running all 500 samples exceeds 15 minutes, reduce evaluation set to first 200 questions, documenting the deviation.
  2. *Adaptive-k Degeneracy Fallback*: If all scores $s_i$ are identical ($s_i - s_{i+1} = 0$), default to $k=3$ (median budget) and record a "ranking-tie" failure event.
  3. *Downstream LLM Fallback*: Downstream LLM reader generation is strictly optional; if local LLM or API keys are unavailable, the study concludes with rigorous retrieval evidence coverage and token efficiency findings without synthetic generation claims.
