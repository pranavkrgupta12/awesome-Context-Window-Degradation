# Critical Peer Review & Manuscript Revision Log (paper/revision_log.md)

**Paper Title**: Fixed-k versus Adaptive-k Context Selection for Multi-Hop QA: An Evidence-Coverage and Token-Efficiency Study  
**Review Type**: Critical Pre-Submission Technical Review (Harsh Peer Review Standard)  
**Date**: 2026-11-05  

---

## 1. Overall Assessment
The paper presents a carefully executed, controlled comparative study (Pathway B) evaluating fixed-k vs. single-pass score-drop Adaptive-k context selection on the HotpotQA distractor benchmark. All numbers in Table 1, Table 2, Table 3, and Figures 1–3 strictly correspond to verifiable execution logs in `results/`. The reporting of negative and qualified results (specifically that Adaptive-k underperforms fixed $k=5$ on multi-hop full coverage due to missing bridge entities) is commendable and reflects high scientific integrity. However, several critical technical concerns require formal logging and revision.

---

## 2. Major Concerns & Technical Remedies

### Major Concern 1: Pathological Inflation of Coverage-per-Token in $k=1$ Baseline (Section V-B)
- **Reviewer Critique**: The paper initially stated in its protocol that Adaptive-k would be tested against all fixed-$k$ on Coverage per 1,000 tokens. However, fixed $k=1$ achieves 5.714 (BM25) and 6.388 (TF-IDF) coverage per 1k tokens simply because its token denominator is tiny (~85–100 tokens), despite achieving **0.0% Full Coverage** (since HotpotQA requires $\ge 2$ gold paragraphs). Celebrating or comparing raw recall-per-token against $k=1$ without conditioning on non-zero full-coverage is deceptive.
- **Action Taken & Revision**: Section V-B in `paper/main.tex` and `results/results_summary.md` was explicitly revised to declare a **Qualified Negative Result** for Decision Rule 1. The manuscript explicitly points out that $k=1$ is a degenerate baseline for multi-hop QA, and that Adaptive-k dominates only among operating points capable of non-zero full coverage.

### Major Concern 2: Scope Boundary Between Evidence Selection and Generative QA (Section VII)
- **Reviewer Critique**: The paper's title mentions "Multi-Hop QA", but the study exclusively evaluates paragraph retrieval metrics (recall, precision, token count) without running an LLM reader to evaluate downstream answer exact match (EM) or token F1. If an uncareful reader reads only the abstract, they might conflate "evidence recall" with "question answering accuracy".
- **Action Taken & Revision**: The Abstract, Methodology, and Limitations sections were sharpened to repeatedly clarify that this is an **evidence-coverage and context-selection study**. We explicitly note that reader models could theoretically compensate for missing evidence via parametric memory, or conversely hallucinate when distractor noise is present.

### Major Concern 3: Generalization Beyond Sparse Retrievers (Section VI)
- **Reviewer Critique**: Adaptive-k was originally demonstrated by Taguchi et al. (2025) on dense embeddings (BGE, Contriever), which feature continuous similarity distributions. BM25 scores are discrete and uncalibrated, which may exaggerate score drops between top-1 and top-2.
- **Action Taken & Revision**: Added an explicit discussion in Section VI analyzing how BM25's unnormalized score scale exacerbates premature stopping on bridge entities, and marked dense retriever verification on HotpotQA as a future extension in Section VII.

---

## 3. Minor Concerns & Editorial Corrections

1. **Table 1 / Text Precision Consistency**: Verified that all numbers in Table 1 match `results/tables/table1_main_results.csv` exactly (BM25 Adaptive-k tokens: 263.2 [235.4, 293.8]; full coverage: 21.4%).
2. **DOI Verification**: Checked that DOIs for Liu et al. (10.1162/tacl_a_00638), Paulsen (10.54364/AAIML.2026.61268), Yang et al. (10.18653/v1/D18-1259), and Hsieh et al. (10.18653/v1/2024.findings-acl.890) are authentic and resolve to primary publications.
3. **Figure Resolution**: Verified that vector PDFs and 300 DPI PNGs are generated and located in `results/figures/` and `paper/figures/`.

---

## 4. Prioritized Author Action Checklist

- [x] Document qualified negative result for Decision Rule 1.
- [x] Ensure strict consistency between results CSV, LaTeX tables, and Markdown tables.
- [x] Verify zero leakage in unit tests.
- [x] Provide Overleaf-ready bundle with verified BibTeX entries.
- [ ] Researcher manual inspection: Review the 40 failure cases in `results/tables/failure_sample.csv` and annotate the `my_label` column.
- [ ] Researcher reflection: Complete `[MY REFLECTION]` prompts in `ai_assistance_log.md`.
