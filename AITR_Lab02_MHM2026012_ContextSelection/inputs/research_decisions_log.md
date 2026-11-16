# Research Decisions Log (inputs/research_decisions_log.md)

**Project**: Context-Window Degradation and Its Impact on Long-Document Research Synthesis  
**Stage**: Literature Review $\rightarrow$ Verified Gap $\rightarrow$ Research Question  
**Status**: Preliminary / Evidence verification required  

---

## 1. Project Scope
The completed literature review investigates the gap between nominal context-window capacity of Large Language Models (LLMs) and their effective ability to retrieve, reason over, and synthesize information as context length increases.

The review focuses on:
- Lost in the Middle
- Needle-in-a-Haystack (NIAH)
- NoLiMa
- DENIAHL
- Maximum Effective Context Window (MECW)
- Retrieval-Augmented Generation (RAG)
- LongRAG
- Adaptive-k / adaptive context selection
- Limitations of long-document synthesis

The implementation paper should narrow the scope to one experimentally testable question.

---

## 2. Evidence Ledger

### VERIFIED — From the supplied literature review
1. **Position-dependent long-context degradation**: Information in the middle of a long context can be harder for an LLM to use than near beginning or end (Liu et al., 2024).
2. **NIAH-style evaluation**: Hiding a relevant fact inside increasingly large amounts of irrelevant context.
3. **Beyond-literal retrieval**: NoLiMa as an evaluation framework testing retrieval beyond simple lexical matching (Modarressi et al., 2025).
4. **Contextual and positional effects**: DENIAHL evaluates contextual features, placement, and density (Dai et al., 2024).
5. **Nominal versus effective context**: Maximum Effective Context Window (MECW) distinct from advertised maximum (Paulsen, 2025).
6. **Retrieval-based mitigation**: RAG supplies relevant retrieved passages instead of the entire long context.
7. **LongRAG**: Retrieval-augmented approach for long-context QA (Zhao et al., 2024).
8. **Adaptive context selection**: Adaptive-k dynamically selects context supplied to the model (Taguchi et al., 2025).

---

## 3. INFERRED Claims
1. As irrelevant context increases, performance difference between edge and middle positions may increase.
2. Retrieval-based context selection may reduce position-dependent degradation by removing irrelevant context.
3. A smaller amount of highly relevant context may outperform a larger amount of noisy context.
4. Retrieval may improve localized QA while harming distributed multi-region synthesis.
5. Adaptive context selection may provide a better accuracy-efficiency trade-off than fixed-k retrieval.

---

## 4. UNKNOWN / Verification Required
- Exact experimental conditions and numerical findings of Liu et al. (2024).
- Statement that majority of evaluated models in NoLiMa fall below 50% retrieval success at 32K tokens.
- Exact conditions behind reported MECW degradation at ~1,000 tokens.
- Exact DENIAHL findings on placement and feature density.
- Exact LongRAG experimental design and gains.
- Exact Adaptive-k token-efficiency and accuracy results.
- Whether chunk-based retrieval demonstrably harms holistic long-document synthesis under controlled experiments.
- Whether the proposed experiment has already been conducted in substantially the same form.

---

## 5. Candidate Gaps & Rankings
- **Rank 1**: Retrieval as mitigation for position-dependent degradation ($RQ$: Does retrieval-based context selection reduce position-dependent context degradation compared with direct long-context processing?).
- **Rank 2**: Position $\times$ Context Length ($RQ$: How does position-dependent degradation change as context length increases?).
- **Rank 3**: Context Quality vs. Context Quantity ($RQ$: Does providing less but more relevant context outperform larger amounts of noisy context?).

---

## 6. Recommended Provisional Direction
- **Title**: Investigating Position-Dependent Context Degradation and Retrieval-Based Mitigation in Long-Context Question Answering
- **Core RQ**: As irrelevant context increases, how does the position of relevant information affect LLM question-answering performance, and can retrieval-based context selection reduce this degradation?
- **Factors / Independent Variables**:
  1. Context length (candidate levels: 2K, 4K, 8K, 16K)
  2. Information position (Beginning, 25%, Middle, 75%, End)
  3. Processing method (Direct Long-Context Baseline vs. Retrieval Comparator)
- **Metrics / Dependent Variables**: EM, F1, Input tokens, Latency.
- **Deeper Analysis**: Position degradation metric $D_{position} = \text{Performance}_{edge} - \text{Performance}_{middle}$, Context degradation $D_{context} = \text{Performance}_{short} - \text{Performance}_{long}$, Retrieval benefit $B_{RAG} = \text{Performance}_{RAG} - \text{Performance}_{Direct}$, Token efficiency $\text{Efficiency} = \frac{F1}{\text{Input Tokens}}$.
