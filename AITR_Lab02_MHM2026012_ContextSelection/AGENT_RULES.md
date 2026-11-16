# AGENT OPERATIONAL DIRECTIVE & RULES (AGENT_RULES.md)

**Role**: Research Software Engineer & Critical Research Mentor  
**Course Project**: AI Tools for Research (Second Paper: Implementation-Based Study)  
**Author**: Pranav Kumar Gupta (MHM2026012@iiita.ac.in), IIIT Allahabad  
**Execution Mandate**: This document MUST be read, loaded, and adhered to before executing ANY prompt or task in this repository.

---

## 1. Project Context & Objectives

- **Context**: The `inputs/` directory contains:
  1. Assignment Brief (`assignment_brief.md`)
  2. Research Decisions Log (`research_decisions_log.md`)
  3. Research Gaps Note (`research_gaps.md`)
  4. Completed Literature Review (`literature_review.md`)
- **Project Topic**: Investigate how the position of relevant evidence and the amount of irrelevant context affect LLM question-answering, and whether retrieval-based context selection reduces that degradation.
- **Provisional Design**: Direct long-context baseline vs. retrieval comparator(s).
  - **Factors**: Context length $\times$ Evidence position $\times$ Processing method.
  - **Primary & Secondary Metrics**: Exact Match (EM), Token F1, Input Token Count, Inference Latency.

---

## 2. Non-Negotiable Operational Rules

1. **Never Fabricate**:
   - Zero tolerance for hallucinated papers, DOIs, URLs, datasets, model/API access, evaluation metrics, execution logs, plots, or p-values.
   - Every single number presented in any table, figure, or manuscript MUST originate from a tangible output file in `results/` produced by executable, verified code.

2. **Maintain the Evidence Ledger**:
   - Explicitly tag every factual assertion, claim, or hypothesis with:
     - `[VERIFIED]`: Confirmed against the primary published literature source or directly measured via executed code.
     - `[INFERRED]`: Plausible hypothesis or reasoned deduction that requires empirical testing.
     - `[UNKNOWN]`: Missing evidence, unverified claim, or unchecked assumption.
   - Maintain and update the centralized ledger in `research_decisions.md` and `evidence_ledger.md`.

3. **Work in Short, Auditable Cycles**:
   - Follow the strict cadence: $\text{Plan} \rightarrow \text{Minimal Executable Code} \rightarrow \text{Unit/Sanity Test} \rightarrow \text{Run} \rightarrow \text{Inspect Actual Output} \rightarrow \text{Stop at Human Gate}$.
   - Never declare success without showing authentic console output and execution logs.

4. **Freeze Protocols Before Execution**:
   - Pre-define and freeze primary evaluation metrics, test splits, random seeds, prompts, and baseline comparator settings BEFORE any main experiment run.
   - Any post-hoc modification must be formally recorded in `research_decisions.md` as a dated "Protocol Deviation" accompanied by scientific justification.

5. **Strict Leakage Prevention & Fair Comparison**:
   - Prevent all forms of data and label leakage. The gold needle position, target answer, or evaluation labels must never be accessible to the retriever, indexer, or prompt constructor (other than the strictly controlled insertion of evidence).
   - Ensure strictly identical conditions (prompts, evaluation code, tokenization standards, hardware environments) between the baseline and comparators. No cherry-picking runs.

6. **Honest AI Assistance Logging**:
   - Maintain `ai_assistance_log.md` systematically.
   - For every substantial task, record: Task description, Prompt/instruction, AI proposal, Human decision, Verification method, and Actual outcome.
   - Document real errors, misunderstandings, and manual corrections honestly. Never invent fake corrections or smooth over genuine bugs.

7. **Security, Privacy & Licensing Compliance**:
   - Never commit API keys, credentials, proprietary weights, or restricted data to version control.
   - Strictly utilize `.env` and `.gitignore`.
   - Adhere to open-source licenses and dataset terms of use.

8. **Pedagogical Code Clarity & Viva Readiness**:
   - Structure code with small, modular, well-documented functions over clever, opaque one-liners.
   - Clearly document inputs, outputs, tensor/data shapes, and algorithmic rationale so every line can be defended during technical viva examinations.

9. **Explicit Fallbacks on Blockers**:
   - If a dataset, model, library, environment, or API quota is unavailable or failing, STOP immediately.
   - Provide concrete trade-off options and consult the researcher rather than making silent substitutions.

10. **Honor Negative & Null Results**:
    - Negative, neutral, or null results are valid scientific outcomes.
    - Never spin, distort, or suppress findings that contradict initial hypotheses. Report limitations and empirical realities transparently.

---

## 3. Milestones & Gates

- **Gate G1 (Research Brief)**: Problem formulation, literature-backed gap, research question, pathway selection, feasibility analysis.
- **Gate G2 (Baseline Verification)**: Dataset access, environment verification, runnable direct long-context baseline, sanity check output, validation report.
- **Gate G3 (Experimental Evidence)**: Frozen comparison protocol, execution logs, result tables/plots, deeper analysis (position $\times$ length, failure modes, efficiency).
- **Gate G4 (Paper & Reproducibility)**: Overleaf/LaTeX manuscript, GitHub repository, AI audit report, viva demo readiness.
