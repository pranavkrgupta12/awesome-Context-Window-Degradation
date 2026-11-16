# Technical Viva Examination Guide: 25 Defense Questions & Answers (VIVA_QA.md)

**Project Title**: Fixed-k versus Adaptive-k Context Selection for Multi-Hop QA: An Evidence-Coverage and Token-Efficiency Study  
**Candidate**: Pranav Kumar Gupta (MHM2026012@iiita.ac.in), IIIT Allahabad  
**Course**: AI Tools for Research (Lab 02 Viva Preparation)  

---

### Category A: Problem Formulation & Theoretical Foundations

#### Q1: What is the core research problem investigated in this project?
**Answer**: The project investigates the trade-off between evidence coverage and token efficiency in Retrieval-Augmented Generation (RAG) for multi-hop question answering. Standard RAG relies on a fixed passage budget ($k$), which either truncates required evidence on complex multi-hop queries ($k$ too small) or inflates token cost and injects distracting noise ($k$ too large), exacerbating context-window degradation. We evaluate whether single-pass score-gap Adaptive-$k$ context selection (Taguchi et al., 2025) resolves this trade-off on sparse retrieval backends.

#### Q2: What is the "Lost in the Middle" phenomenon, and how does your study relate to it?
**Answer**: Demonstrated by Liu et al. (TACL 2024), "Lost in the Middle" refers to the severe drop in LLM retrieval accuracy when target information is placed in the interior of a long prompt context rather than at the beginning or end. Our study addresses context selection at the retrieval stage: by dynamically selecting fewer, highly relevant paragraphs (reducing average tokens from 1226.8 down to 263.2), Adaptive-$k$ suppresses distractor accumulation that triggers positional attention degradation.

#### Q3: What is the Maximum Effective Context Window (MECW)?
**Answer**: Introduced by Paulsen (AAIML 2026 / arXiv:2509.21361), MECW formalizes the practical limit where an LLM's multi-step reasoning accuracy holds before degradation sets in, showing it can be up to 99% smaller than the provider-advertised nominal maximum (often degrading around ~1,000 tokens). This motivates optimizing retrieval context selection to stay strictly within the model's effective processing window.

#### Q4: Why did you choose Pathway B (Controlled Comparative Study)?
**Answer**: Pathway B allows us to rigorously evaluate relevant methods (Fixed-$k$ vs. Adaptive-$k$ across BM25 and TF-IDF) under an identical, carefully controlled protocol holding data splits, candidate pools (10 paragraphs), evaluation code, and random seeds strictly constant, isolating the algorithmic impact of score-drop thresholding.

#### Q5: What is the difference between single-hop and multi-hop question answering?
**Answer**: In single-hop QA (e.g., SQuAD), an answer can be extracted from a single isolated paragraph. In multi-hop QA (e.g., HotpotQA), answering requires finding and chaining evidence across two or more separate paragraphs (e.g., bridging an entity from document A to discover the answer in document B).

---

### Category B: Algorithm & Mathematics

#### Q6: How does the Adaptive-$k$ algorithm work mathematically?
**Answer**: Proposed by Taguchi et al. (EMNLP 2025), candidate paragraphs are scored and sorted in descending order: $s_1 \ge s_2 \ge \dots \ge s_M$. The algorithm computes the first discrete differences (score drops) between adjacent candidates: $\Delta s_i = s_i - s_{i+1}$ for $i \in \{1, \dots, M-1\}$. The cutoff $k^*$ is selected as the index that maximizes this drop:
$$k^* = \arg\max_{i \in \{1, \dots, M-1\}} (s_i - s_{i+1})$$
The prefix of top-$k^*$ paragraphs is then selected. If all score drops are zero or non-positive (uniform tie), a fallback budget $k^* = 3$ is used.

#### Q7: What are the mathematical formulations of the BM25 and TF-IDF retrievers used?
**Answer**: 
- **BM25Okapi**: Uses probabilistic inverse document frequency $\text{IDF}(w) = \ln(1 + \frac{N - n(w) + 0.5}{n(w) + 0.5})$ combined with saturated term frequency:
$$\text{TF}_{\text{BM25}} = \frac{f(w, p) \cdot (k_1 + 1)}{f(w, p) + k_1 \cdot (1 - b + b \cdot \frac{|p|}{\text{avgdl}})}$$
with standard parameters $k_1 = 1.5$ and $b = 0.75$.
- **TF-IDF**: Uses sublinear term frequency $1 + \log(\text{tf})$ and smooth inverse document frequency with cosine similarity between unit-normalized query and document vectors.

#### Q8: How is the primary metric "Coverage per 1,000 Tokens" defined?
**Answer**:
$$\text{Coverage per 1k Tokens} = \frac{\text{Evidence Recall}}{\text{Selected Tokens}} \times 1000$$
where $\text{Evidence Recall} = \frac{|\mathcal{S} \cap \mathcal{P}_{\text{gold}}|}{|\mathcal{P}_{\text{gold}}|}$, and Selected Tokens represents the word count multiplied by the 1.3 token expansion factor.

#### Q9: How did you compute uncertainty and confidence intervals?
**Answer**: We utilized non-parametric percentile bootstrap resampling with 1,000 resamples over the 500 questions, using a fixed random seed (`seed=0`). The 95% confidence interval is determined by the 2.5th and 97.5th percentiles of the bootstrap distribution: $[\theta_{0.025}, \theta_{0.975}]$.

#### Q10: Why is sorting stability important when calculating $k^*$?
**Answer**: If candidate paragraphs have identical scores (e.g., zero keyword match with the query), unstable sorting algorithms could arbitrarily shuffle candidates across runs. We explicitly used `kind="mergesort"` in NumPy to guarantee deterministic, stable sorting.

---

### Category C: Data Integrity, Leakage & Preprocessing

#### Q11: What dataset did you use, what is its license, and what is its configuration?
**Answer**: We used HotpotQA (Yang et al., EMNLP 2018), released under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0). We evaluated the official validation set in the "distractor" setting, where each question is paired with exactly 10 candidate paragraphs (2 gold and 8 distractor paragraphs).

#### Q12: How did you prevent data and label leakage in the retrieval pipeline?
**Answer**: The raw candidate paragraphs contain `is_gold` boolean metadata. In `src/data/__init__.py`, this metadata is stripped, and the retriever receives only plain dictionaries containing `title` and `text`. In `tests/test_retrieval.py`, we implemented `test_leakage_invariance()`, proving that blanking or permuting gold labels yields bit-for-bit identical scores and rankings.

#### Q13: Did you discover any data anomalies or defective rows in HotpotQA?
**Answer**: Yes. When inspecting the first 500 rows of the validation set, rows 27, 222, 239, 276, and 466 had fewer than 10 candidate paragraphs (ranging from 2 to 5 paragraphs). Ingesting these would have corrupted fair comparisons against fixed $k \in \{5, 10\}$. We updated our ingestion pipeline to skip defective rows deterministically, inspecting 505 rows to collect exactly 500 valid 10-paragraph records. This is transparently logged in `results/raw/sanity.txt`.

#### Q14: How are question types distributed across your 500 questions?
**Answer**: The 500 valid questions consist of 408 "bridge" questions (81.6%) and 92 "comparison" questions (18.4%), and 100% of the questions require $\ge 2$ gold supporting paragraphs.

---

### Category D: Experimental Results & Findings

#### Q15: What were the headline empirical results for Adaptive-$k$ on BM25?
**Answer**: On BM25, Adaptive-$k$ selected an average of $k=2.22$ paragraphs, using **263.2 tokens** [95% CI: 235.4, 293.8]. It achieved **0.568 Evidence Recall** [0.545, 0.591], **21.4% Full Coverage** [17.8%, 25.2%], and **0.739 Precision** [0.706, 0.769], yielding **4.925 Coverage per 1k Tokens** with an average latency of 0.68 ms.

#### Q16: How much token savings did Adaptive-$k$ achieve?
**Answer**: Adaptive-$k$ achieved a **78.5% token reduction** compared to full-context feeding ($k=10$, 1226.8 tokens) and a **26.1% token reduction** compared to fixed $k=3$ (356.2 tokens).

#### Q17: Did your experiment confirm your pre-frozen Decision Rule 1?
**Answer**: It resulted in a **qualified negative outcome**. While Adaptive-$k$ vastly outperformed fixed $k=3, 5, 10$ on coverage per token (4.925 vs 2.310 at $k=3$ and 1.442 at $k=5$), fixed $k=1$ scored 5.714 coverage per token because of extreme token brevity (~101 tokens). However, fixed $k=1$ achieved **0.0% full coverage** because every multi-hop question requires at least two paragraphs. Thus, while Adaptive-$k$ is the most efficient method capable of non-zero multi-hop coverage, it did not strictly exceed the pathological $k=1$ baseline.

#### Q18: Did Adaptive-$k$ match fixed $k=5$ on multi-hop full coverage (Decision Rule 2)?
**Answer**: No. Pre-frozen Decision Rule 2 expected Adaptive-$k$ to match fixed $k=5$ within $\pm 5\%$. In reality, Adaptive-$k$ achieved only **21.4% full coverage** compared to **61.6% for fixed $k=5$** on BM25 (and 23.2% vs. 67.2% on TF-IDF). The hypothesis was rejected by the empirical evidence.

#### Q19: Why does Adaptive-$k$ underperform fixed $k=5$ on multi-hop questions?
**Answer**: Our qualitative failure analysis on 40 sampled failure cases revealed that **55% of failures are caused by bridge entities absent from the query**. In bridge questions, paragraph 1 matches the query, but paragraph 2 shares keywords only with paragraph 1. Consequently, sparse retrievers produce a massive score gap immediately between paragraph 1 and paragraph 2. Adaptive-$k$ detects this drop and immediately halts at $k=1$ or $k=2$, dropping the second gold piece.

#### Q20: How did performance compare between Bridge and Comparison questions?
**Answer**: Both retrievers performed significantly better on Comparison questions than on Bridge questions. For BM25 Adaptive-$k$, full coverage on comparison queries was **29.3%** versus **19.6%** on bridge queries. In comparison questions, both entities are typically explicitly named in the question prompt (e.g., *"Were Scott Derrickson and Ed Wood of the same nationality?"*), giving both gold paragraphs high initial retrieval scores.

---

### Category E: Research Integrity, Limitations & Viva Defense

#### Q21: Why is reporting negative or null results considered scientifically valuable in this project?
**Answer**: In accordance with Non-Negotiable Rule 10, negative results prevent publication bias and ungrounded claims. Revealing that single-pass score-gap Adaptive-$k$ fails on multi-hop bridge questions provides a crucial negative finding: dynamic thresholding cannot substitute for iterative multi-step retrieval when reasoning requires traversing latent entity hops.

#### Q22: What are the primary threats to validity / limitations of this study?
**Answer**:
1. *Retrieval-only scope*: We evaluate evidence selection rather than end-to-end LLM generative QA accuracy.
2. *Fixed candidate pool*: Evaluated on HotpotQA distractor setting ($M=10$ paragraphs) rather than an open-domain web corpus.
3. *Sparse retrievers*: Evaluated on BM25 and TF-IDF; dense embeddings with continuous cosine geometries may produce different score drops.

#### Q23: How did you verify that your baseline implementation was correct before testing Adaptive-$k$?
**Answer**: At Gate G2, we enforced three sanity checks:
1. *Upper Bound*: Fixed $k=10$ over 10 candidate paragraphs produced exactly 100.0% evidence recall and 100.0% full coverage across all 500 questions.
2. *Lower Bound*: Random selection control at $k=1, 3, 5$ across 5 seeds yielded 10.7%, 30.5%, and 50.1% recall, establishing baseline chance levels.
3. *Determinism*: Re-running the pipeline produced 100% bit-for-bit identical rankings and scores.

#### Q24: What packages were used, and how was the repository frozen?
**Answer**: We used `rank_bm25` (0.2.2), `scikit-learn` (1.9.1), `numpy` (2.5.4), `pandas` (3.1.1), `scipy` (1.18.1), and `matplotlib` (3.11.2). The complete environment was verified via `scripts/env_check.py`, and the protocol was locked via git tag `protocol-frozen`.

#### Q25: If you had another week and a GPU cluster, what would be your next scientific step?
**Answer**: I would implement an iterative two-pass Adaptive-$k$ pipeline: in pass 1, Adaptive-$k$ selects the top anchor passage; an LLM or cross-encoder extracts the bridge entity, reformulates the query, and triggers pass 2 to retrieve the second-hop passage. I would compare this iterative design against dense neural retrievers (such as BGE or Contriever) and evaluate downstream answer EM/F1 using a local open LLM (such as Llama-3-8B).
