# AI Tools for Research — Assignment Brief (Paper 2)

**Title**: AI-assisted coding, vibe coding and evidence-based experimentation  
**Course**: AI Tools for Research (Second Paper)  
**Author / Student**: Pranav Kumar Gupta  

---

## 1. The Challenge
Your first paper mapped the research landscape. Your second paper must ask a focused question, build or reproduce a working solution, and investigate it through real, reproducible experiments.

Use your completed literature review as an evidence base, not text to recycle. Verify original studies, select one tractable problem, establish a baseline, use AI tools to implement and debug code, evaluate a meaningful research contribution, and write a second paper supported by measured results.

**Research journey**:
$$\text{REVIEW} \rightarrow \text{VERIFIED GAP} \rightarrow \text{QUESTION} \rightarrow \text{BASELINE} \rightarrow \text{VALIDATION} \rightarrow \text{EXPERIMENT} \rightarrow \text{EVIDENCE} \rightarrow \text{PAPER} \rightarrow \text{REPRODUCE}$$

A successful project includes an evidence-based research question, actual executable code, a verified baseline, a fair experimental comparison, a meaningful analysis, a complete paper, and a documented repository. A carefully analyzed negative result can be as valuable as an improvement.

---

## 2. Learning Outcomes
- Connect implementation study explicitly to verified findings from the previous literature review.
- Formulate research questions, hypotheses (when applicable), and measurable success criteria.
- Use AI-assisted coding and vibe coding to specify, generate, read, run, test, debug, and improve code.
- Reproduce or validate a trusted baseline before claiming benefits from any modification.
- Design fair comparisons, prevent data leakage, and analyze real results critically.
- Write an evidence-grounded implementation paper with LaTeX/Overleaf and reproducible figures.
- Document the human–AI collaboration and explain technical decisions without relying on AI output as authority.

---

## 3. The Research Standard
- **Continuity**: Remain in the research area of your completed review.
- **Execution**: Produce working and tested code. Screenshots, mock-ups, or application interfaces alone are insufficient.
- **Evidence**: All reported numbers, tables, plots, and conclusions must come from actual experiments or explicitly attributed sources.
- **Comparison**: Include two appropriate baselines/comparators where feasible; justify an equivalent rigorous design when not.
- **Depth**: Add at least one deeper analysis: ablation, error or failure cases, robustness, sensitivity, or resource efficiency.
- **Reproducibility**: Record data protocol, environment, parameters, random seeds, and commands needed to regenerate key results.
- **Ownership**: Understand submitted code, trace its origin, validate AI suggestions, and explain important decisions.

---

## 4. Approved Pathways to a Contribution
- **Pathway A (Reproduction + extension)**: Reproduce a published method, then study a justified new condition or component.
- **Pathway B (Controlled comparative study)**: Evaluate relevant methods under a common, carefully chosen protocol that answers a specific question.
- **Pathway C (Targeted modification)**: Change one technically justified component of a baseline.
- **Pathway D (Hybrid/prototype + evaluation)**: Combine methods or build a prototype to investigate a computational hypothesis.

---

## 5. Milestones & Approval Gates
- **G1 (Research brief)**: 1-page gap/problem brief, original supporting papers, question, pathway, compute and data feasibility. Ready when narrow, literature-supported, and experimentally testable.
- **G2 (Baseline verification)**: Accessible dataset, environment test, runnable baseline, measured output, validation report. Ready when baseline behavior and protocol have been checked, not merely executed.
- **G3 (Experimental evidence)**: Frozen comparison protocol, outputs/logs, result table and plots, one deeper analysis. Ready when experimental claims are traceable to genuine runs and evaluated fairly.
- **G4 (Paper and reproducibility)**: Paper PDF + LaTeX, GitHub repository, AI audit, 5-minute demonstration. Ready when methods, outputs, and provenance can be inspected and defended.

---

## 6. Prompt Studio & Methodological Requirements
- Maintain an evidence ledger with three labels: `VERIFIED`, `INFERRED`, `UNKNOWN`.
- Never fabricate results, p-values, figures, execution logs, or bibliographic entries.
- Prevent test-set tuning and data leakage.
- Never commit secrets or restricted data.
