# 5-Minute Technical Demonstration Script (DEMO_SCRIPT.md)

**Project Title**: Fixed-k versus Adaptive-k Context Selection for Multi-Hop QA: An Evidence-Coverage and Token-Efficiency Study  
**Presenter**: Pranav Kumar Gupta (MHM2026012@iiita.ac.in), IIIT Allahabad  
**Course**: AI Tools for Research (Lab 02 Viva & Demonstration)  
**Total Target Duration**: 5 Minutes  

---

## Minute 0:00 – 1:00: Context, Problem & Research Question
- **Action**: Open [README.md](file:///c:/Users/bipin/OneDrive/Desktop/atr-ppr/README.md) and show repository structure.
- **Spoken Walkthrough**:
  > *"Good morning. My research project addresses the tension between context-window degradation and retrieval-augmented generation in multi-hop question answering.*
  >
  > *While LLMs can accept large context windows, empirical research—such as Liu et al.'s 'Lost in the Middle' and Paulsen's MECW—demonstrates that models suffer severe degradation when buried in irrelevant distractor context. RAG mitigates this by selecting context passages, but standard RAG uses a static number of passages: fixed-$k$. If $k$ is too small, we miss evidence on multi-hop questions. If $k$ is too large, we inflate tokens and inject distractor noise.*
  >
  > *Our study evaluates a recent proposal by Taguchi et al. (EMNLP 2025): single-pass score-gap Adaptive-$k$, which dynamically cuts off context at the largest discrete score drop ($k^* = \arg\max_i (s_i - s_{i+1})$). We ask: Does Adaptive-$k$ achieve a superior evidence-coverage-per-token frontier across sparse retrievers (BM25 and TF-IDF), and does it match fixed $k=5$ full coverage on multi-hop queries?"*

---

## Minute 1:00 – 2:00: Experimental Protocol & Zero-Leakage Architecture
- **Action**: Open [paper/protocol.md](file:///c:/Users/bipin/OneDrive/Desktop/atr-ppr/paper/protocol.md) and highlight the Mermaid diagram and frozen protocol.
- **Spoken Walkthrough**:
  > *"Before inspecting any results, we strictly froze our experimental protocol under git tag `protocol-frozen`. We evaluated 500 questions from the HotpotQA validation distractor split.*
  >
  > *Each question has exactly 10 candidate Wikipedia paragraphs, containing $\ge 2$ gold paragraphs and hard distractors. We enforced strict zero-leakage: gold labels and title metadata are stripped before the retriever scores candidates. Our test suite in `tests/test_retrieval.py` mathematically proves that flipping or blanking gold metadata results in bit-for-bit identical rankings.*
  >
  > *We also pre-froze three decision rules: specifically testing whether Adaptive-$k$'s 95% bootstrap confidence interval for coverage per token exceeds all fixed-$k$ baselines, and whether it matches fixed $k=5$ full coverage within $\pm 5\%$."*

---

## Minute 2:00 – 3:00: Live Code Execution & Sanity Check
- **Action**: Switch to terminal and run the reproduction script:
  ```powershell
  python scripts/reproduce_small.py
  ```
- **Spoken Walkthrough**:
  > *"To demonstrate complete reproducibility, I am executing our fast reproduction script `reproduce_small.py`, which evaluates 50 questions across all 10 experimental conditions in real time.*
  >
  > *[Wait 0.5s for output table to display]*
  >
  > *As you can see, 500 evaluations executed in under one second. The BM25 baseline at $k=10$ achieves exactly 100.0% recall, satisfying our upper bound sanity condition, while our random baseline control at $k=1$ achieves 10.7% recall, confirming that informed retrieval is functioning correctly."*

---

## Minute 3:00 – 4:00: Main Results & The Qualified Negative Finding
- **Action**: Open [results/figures/figure1_coverage_vs_tokens.pdf](file:///c:/Users/bipin/OneDrive/Desktop/atr-ppr/results/figures/figure1_coverage_vs_tokens.pdf) and [results/tables/table1_main_results.md](file:///c:/Users/bipin/OneDrive/Desktop/atr-ppr/results/tables/table1_main_results.md).
- **Spoken Walkthrough**:
  > *"Looking at Table 1 and Figure 1, two major empirical findings emerge:*
  >
  > *First, Adaptive-$k$ provides massive token reduction and distractor suppression. For BM25, it selects an average of $k=2.22$ paragraphs, using only 263.2 tokens compared to 1226.8 tokens for full context—a 78.5% token reduction—while elevating precision to 73.9%, compared to only 32.0% for fixed $k=5$.*
  >
  > *Second, we report an honest, qualified negative result: Adaptive-$k$ does NOT match fixed $k=5$ multi-hop coverage. Adaptive-$k$ achieves only 21.4% full coverage on multi-hop questions, whereas fixed $k=5$ achieves 61.6%. Consequently, our pre-frozen Decision Rule 2 is rejected by the empirical evidence."*

---

## Minute 4:00 – 5:00: Failure Analysis & Conclusion
- **Action**: Open [results/figures/figure3_failure_distribution.pdf](file:///c:/Users/bipin/OneDrive/Desktop/atr-ppr/results/figures/figure3_failure_distribution.pdf) and [paper/main.tex](file:///c:/Users/bipin/OneDrive/Desktop/atr-ppr/paper/main.tex).
- **Spoken Walkthrough**:
  > *"To diagnose why Adaptive-$k$ underperformed on full coverage, we conducted a failure analysis on 40 sampled failure cases under seed 42. As Figure 3 shows, 55% of all missed-evidence cases are caused by 'Bridge Entity Absent from Query'.*
  >
  > *In multi-hop questions, paragraph 1 connects to the query, but paragraph 2 connects only to paragraph 1. Because paragraph 2 lacks query keywords, BM25 creates a massive score cliff between paragraph 1 and paragraph 2. Adaptive-$k$ identifies this cliff and immediately stops, prematurely dropping the necessary second hop.*
  >
  > *Our conclusion is clear and defensible: single-pass score-drop Adaptive-$k$ is an outstanding, cost-effective distractor filter for single-hop questions, but multi-hop QA fundamentally requires iterative query expansion rather than static score-drop thresholding. Thank you, and I welcome any questions."*
