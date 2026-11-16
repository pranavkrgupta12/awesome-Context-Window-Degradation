# Research Gaps — Context-Window Degradation and Long-Context QA (inputs/research_gaps.md)

**Project Scope**: Context-Window Degradation and Its Impact on Long-Document Research Synthesis  
**Evidence Taxonomy**: `[VERIFIED]`, `[INFERRED]`, `[UNKNOWN]`  

---

## 1. Five Computationally Testable Research Gaps

### Gap 1 — Position $\times$ Context Length
- **Evidence from review**: Section 3.1 states relevant information in the middle of long contexts can be harder to use; describes U-shaped pattern (Liu et al., 2024).
- **Inference**: Magnitude of position effect may increase systematically as context length increases.
- **RQ**: How does the performance gap between edge-position and middle-position relevant information change as context length increases?
- **Candidate Metric**: $D_{position}(L) = \text{Performance}_{edge}(L) - \text{Performance}_{middle}(L)$.

### Gap 2 — Retrieval as a Mitigation for Position-Dependent Degradation
- **Evidence from review**: Section 4.1 discusses RAG and LongRAG (Zhao et al., 2024; Liu et al., 2024).
- **Inference**: Retrieval may reduce position-dependent degradation because relevant evidence is extracted and presented in a smaller context.
- **RQ**: Does retrieval-based context selection reduce position-dependent degradation compared with direct long-context processing?
- **Candidate Comparison**: Direct LLM ($Full\ Context \rightarrow LLM \rightarrow Answer$) vs. Retrieval+LLM ($Full\ Context \rightarrow Retriever \rightarrow Selected\ Passages \rightarrow LLM \rightarrow Answer$).

### Gap 3 — Context Quality vs. Context Quantity
- **Evidence from review**: Section 4.2 discusses Adaptive-k (Taguchi et al., 2025).
- **Inference**: A smaller amount of highly relevant context may outperform a larger amount of increasingly noisy context.
- **RQ**: Does providing less but more relevant context outperform larger amounts of increasingly noisy context?
- **Candidate Metric**: $\text{Efficiency} = \frac{F1}{\text{InputTokens}}$.

### Gap 4 — Retrieval vs. Global / Distributed Synthesis
- **Evidence from review**: Section 5 notes chunk-based retrieval can struggle with holistic synthesis across a very long document.
- **Inference**: Retrieval improves localized QA but hurts distributed multi-evidence synthesis.
- **Status**: Verification required on original studies.

### Gap 5 — Fixed-k vs. Adaptive-k Retrieval
- **Evidence from review**: Adaptive-k dynamically selects number of retrieved passages.
- **Inference**: Dynamic context selection provides better accuracy-efficiency trade-offs than static top-k.

---

## 2. Top Three Ranked Gaps
1. **Rank 1**: Retrieval as mitigation for position degradation (Significance: Very High, Resources: Moderate, Feasibility: Very High, Measurability: Very High).
2. **Rank 2**: Position $\times$ Context Length (Significance: High, Resources: Low-Moderate, Feasibility: Very High, Measurability: Very High).
3. **Rank 3**: Context Quality vs. Quantity (Significance: High, Resources: Moderate, Feasibility: High, Measurability: Very High).

---

## 3. Recommended Provisional Research Direction
- **Title**: Investigating Position-Dependent Context Degradation and Retrieval-Based Mitigation in Long-Context Question Answering
- **Core RQ**: As irrelevant context increases, how does the position of relevant information affect LLM question-answering performance, and can retrieval-based context selection reduce this degradation?
- **Design**: Direct long-context baseline vs. retrieval comparator; Factors = Context Length (e.g., Short, Medium, Long) $\times$ Evidence Position (Beginning, Middle, End) $\times$ Method (Direct vs. Retrieval).
- **Core Principle**: No claim should be presented as a research result unless supported either by a verified original publication or by a reproducible experiment actually conducted in this project. Negative or null findings are valid results.
