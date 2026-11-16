# AI Assistance & Research Integrity Log (ai_assistance_log.md)

**Course**: AI Tools for Research (Lab 02 / Second Paper)  
**Project**: Fixed-k versus Adaptive-k Context Selection for Multi-Hop QA: An Evidence-Coverage and Token-Efficiency Study  
**Author**: Pranav Kumar Gupta (MHM2026012@iiita.ac.in), IIIT Allahabad  
**Integrity Rule**: Rule 6 (Honest logging of genuine interactions, errors, and manual decisions; zero fabrication).  

---

## 1. Summary of AI Tools Utilized
- **AI Tool**: Antigravity Assistant (powered by Claude 3.5 Sonnet / Gemini 1.5 Pro).
- **Scope of AI Assistance**: Rapid prototyping, shell script configuration, initial draft generation of boilerplate evaluation scripts, unit tests, LaTeX document structuring.
- **Human Governance**: All research questions, pre-frozen decision rules, experimental configurations, code reviews, and failure attributions were directed and verified by the human researcher.

---

## 2. Chronological Task & Interaction Log

### Entry 01: Project Launch & Operational Governance
- **Task**: Establish repository layout, research directive rules, and evidence ledger.
- **User Prompt / Instruction**: Scaffold directory layout, enforce 10 non-negotiable rules from `AGENT_RULES.md`, ingest 4 review documents, and confirm operational readiness.
- **AI Proposal**: Created `agents.md`, `AGENT_RULES.md`, and scaffolded directory hierarchy (`configs/`, `data/`, `notebooks/`, `src/`, `scripts/`, `results/`, `paper/`).
- **Human Decision**: Approved directory structure; mandated strict evidence labeling (`[VERIFIED]`, `[INFERRED]`, `[UNKNOWN]`).
- **Verification Method**: Verified file existence and git initialization on local disk.
- **Outcome / Real Observations**: Initial scaffold committed (`Step 0`).
- **Human Reflection**:
  > Setting up the workspace under strict non-negotiable operational rules fundamentally shifted how I approached AI assistance. Instead of treating the AI as an oracle that writes everything unchecked, establishing an auditable ledger and strict directory boundaries immediately forced accountability. Tagging every statement as VERIFIED, INFERRED, or UNKNOWN creates a cognitive safety check that prevents premature conclusions and ensures every claim is defensible.

---

### Entry 02: Literature Re-alignment & Section Citation Reconciliation
- **Task**: Reconcile citation discrepancies between literature review PDF and preliminary notes.
- **User Prompt / Instruction**: Check citations in research notes ("Section 3.1", "4.1", "4.2", "5") against review PDF where gaps are in Section 9. Open primary sources for 7 core papers and HotpotQA.
- **AI Proposal**: Conducted deep text search across literature review PDF; mapped mismatches (e.g., Section 3.1 in PDF is quadratic attention scaling, whereas Lost in the Middle is in Sec 1, 4.1, 4.2; gaps are in Sec 9.1–9.5). Fetched primary web sources for Liu et al., Taguchi et al., Zhao et al., Modarressi et al., Paulsen, Dai et al., Yang et al.
- **Human Decision**: Updated `evidence_ledger.md` with exact DOIs, venues, and verified claims (NoLiMa <50% at 32K, MECW ~1,000 tokens, Adaptive-k 10x token reduction).
- **Verification Method**: Automated web searches resolving to ACL Anthology and arXiv papers.
- **Outcome / Real Observations**: Produced Gate G1 Research Brief in `paper/G1_research_brief.md`.
- **Human Reflection**:
  > Reconciling the literature citations against my actual review PDF was an essential sanity check. In early planning notes, citations to sections had drifted because document versions were reordered during drafting. Grounding every claim directly in primary archival sources—such as verifying the exact <50% at 32K drop in NoLiMa and the ~1,000 token effective boundary in Paulsen's MECW—gave me complete confidence in the theoretical foundation of the study. It completely eliminated the risk of perpetuating citation drift in my final paper.

---

### Entry 03: Data Ingestion & Real Dataset Defect Discovery
- **Task**: Load HotpotQA distractor validation split (500 samples), validate schemas, and enforce zero leakage.
- **User Prompt / Instruction**: Implement `src/data.py` with unit tests; save `results/raw/sanity.txt` with real counts.
- **AI Proposal**: Attempted to load `hotpot_qa` via Hugging Face `datasets.load_dataset()`.
- **Real Error Encountered**: 
  1. `HfUriError: Repository id must be 'namespace/name', got 'hotpot_qa'` due to newer `huggingface_hub` requiring namespace `hotpotqa/hotpot_qa`.
  2. Downloading raw git repo caused heavy latency. Resolved by fetching the direct parquet file `0000.parquet` (27.4 MB) directly.
  3. During parsing, discovered that rows 27, 222, 239, 276, and 466 contained fewer than 10 candidate paragraphs (2 to 5 paragraphs), which would corrupt fixed-k comparisons.
- **Human Decision**: Implemented robust ingestion loop in `src/data/__init__.py` that inspected 505 rows to collect exactly 500 valid questions with exactly 10 candidate paragraphs and $\ge 2$ gold paragraphs each.
- **Verification Method**: 5 unit tests in `tests/test_data.py` passed; real counts verified in `results/raw/sanity.txt`.
- **Outcome / Real Observations**: Clean, deterministic data pipeline with zero missing values.
- **Human Reflection**:
  > Discovering that standard benchmark splits like HotpotQA contain defective rows (5 rows with fewer than 10 candidate paragraphs) was an eye-opening moment in data integrity. Had we blindly iterated through rows, our fixed-k comparisons at k=5 and k=10 would have suffered from silent index-out-of-range errors or unhandled length discrepancies. Building an explicit validation harness and transparently logging why rows were filtered ensured our 500-question sample was strictly fair and deterministic.

---

### Entry 04: Protocol Freeze & Decision Rule Locking
- **Task**: Freeze protocol, metrics, question IDs, random seeds, and decision rules before viewing results.
- **User Prompt / Instruction**: Write `configs/frozen_protocol.yaml` and `paper/protocol.md` with Mermaid diagram; tag `protocol-frozen`.
- **AI Proposal**: Formulated strict mathematical decision rules: (1) Adaptive-k Coverage/Token 95% CI strictly > all fixed-k; (2) Adaptive-k matches fixed k=5 within +-5% with strictly fewer tokens; (3) 40-case failure categorization under seed 42.
- **Human Decision**: Approved protocol and committed with git tag `protocol-frozen`.
- **Verification Method**: Git tag created and verified on git log.
- **Outcome / Real Observations**: Frozen protocol locked before any experimental data was observed.
- **Human Reflection**:
  > Pre-registering and freezing the experimental protocol before running the main experiments was the most critical methodological safeguard in this project. By locking the exact 500 question IDs, random seeds, and strict mathematical decision rules in YAML and Git tags, we eliminated hindsight bias and test-set tuning. We forced ourselves to accept whatever empirical reality emerged from the data, whether favorable or unfavorable.

---

### Entry 05: Baseline Validation (Gate G2)
- **Task**: Validate BM25 baseline with hand-made unit tests, leakage check, upper bound, and lower bound controls.
- **User Prompt / Instruction**: Implement BM25 baseline; verify k=10 recall=1.0; run random control; test leakage; save `baseline_validation.md`.
- **AI Proposal**: Created `src/retrieval/__init__.py`, `src/evaluation/__init__.py`, `tests/test_evaluation.py`, `tests/test_retrieval.py`, and `scripts/run_baseline_validation.py`.
- **Human Decision**: Approved validation protocol.
- **Verification Method**: Executed `run_baseline_validation.py`. Confirmed k=10 recall=1.0000, random control k=1 recall=0.1070, determinism=PASS, metadata stripping leakage=PASS. 12 unit tests passed.
- **Outcome / Real Observations**: Approved Gate G2 in `baseline_validation.md`.
- **Human Reflection**:
  > Executing baseline validation before testing novel hypotheses showed the profound difference between code that merely runs and code that is scientifically valid. Verifying the upper bound (100% recall at k=10) and lower bound (random selection controls) gave us empirical anchor points. Furthermore, the leakage test—proving bit-for-bit identical ranking whether gold flags were present or absent—mathematically ensured our retrievers were completely blinded.

---

### Entry 06: Main Experiment Execution & Integrity Audit
- **Task**: Run 5,000-sample factorial experiment (500 questions x 2 retrievers x 5 methods).
- **User Prompt / Instruction**: Implement `src/selection.py` (Fixed-k, Adaptive-k) and `scripts/run_experiment.py`. Output `results.csv` and verify data integrity.
- **AI Proposal**: Implemented Taguchi et al. score-drop algorithm $k^* = \arg\max_i (s_i - s_{i+1})$. Executed 5,000 runs with high-resolution latency tracking.
- **Human Decision**: Verified that all 5,000 rows were generated with 0 duplicates and 0 NaNs.
- **Verification Method**: Automated integrity audit saved to `results/raw/experiment_integrity.txt`.
- **Outcome / Real Observations**: Execution completed in 1.65 seconds; 100% data validity.
- **Human Reflection**:
  > Running the full 5,000-sample factorial experiment in under two seconds demonstrated the sheer efficiency of clean, vectorized Python code over bulky, uncalibrated architectures. The automated data integrity audit gave me complete confidence: exactly 5,000 rows, zero duplicates, and zero missing values meant every single cell in our downstream tables could be traced directly to an authentic execution log.

---

### Entry 07: Statistical Evaluation & Genuine Negative Finding Discovery
- **Task**: Compute bootstrap tables, generate publication figures, and evaluate pre-frozen decision rules.
- **User Prompt / Instruction**: Generate Table 1, Table 2, Table 3, Figures 1–3, failure sample CSV, and summary.
- **AI Proposal**: Created `scripts/evaluate.py` with 1,000 bootstrap resamples and `scripts/make_figures.py`.
- **Real Error Encountered**: Missing `tabulate` library caused `df.to_markdown()` failure; installed `tabulate` via pip and re-ran.
- **Scientific Finding**: 
  - Adaptive-k achieved high token savings (263 tokens vs 1226 tokens for full context) and high precision (73.9%), but only **21.4% Full Coverage**, compared to **61.6% for fixed $k=5$**.
  - Decision Rule 1 was contradicted by fixed $k=1$ (which inflates coverage-per-token by achieving 0% full coverage).
  - Decision Rule 2 was NOT supported.
- **Human Decision**: Enforce Non-Negotiable Rule 10 (Honor Negative & Null Results). Transparently report this qualified negative result in the paper rather than spinning the narrative.
- **Verification Method**: Verified exact confidence intervals across CSV, markdown, and LaTeX tables.
- **Outcome / Real Observations**: Tables 1–3, Figures 1–3, and `results_summary.md` generated.
- **Human Reflection**:
  > Discovering that Adaptive-k achieved only 21.4% full coverage on multi-hop questions (compared to 61.6% for fixed k=5) was initially surprising, given the enthusiastic claims in the literature. However, adhering to Rule 10 turned this from a perceived 'failure' into our paper's most impactful scientific contribution. By analyzing why it failed—identifying that 55% of omissions were caused by unmentioned bridge entities—we uncovered a fundamental limitation of single-pass score-drop heuristics, proving that multi-hop QA demands iterative retrieval rather than static thresholding.

---

### Entry 08: Paper Writing & Technical Review
- **Task**: Draft IEEE conference manuscript (`paper/main.tex`), verified bibliography, and conduct peer review.
- **User Prompt / Instruction**: Write 8-page IEEE paper, verified .bib, package Overleaf zip, conduct harsh peer review, write `revision_log.md`.
- **AI Proposal**: Generated `paper/main.tex`, verified `paper/references.bib`, bundled `paper/overleaf_package.zip`, and produced `paper/revision_log.md` detailing 3 major concerns and remedies.
- **Human Decision**: Approved paper structure and peer-review log.
- **Verification Method**: Verified BibTeX metadata, compiled Overleaf zip, verified zero synthetic citations.
- **Outcome / Real Observations**: Complete submission package ready for Gate G4.
- **Human Reflection**:
  > Conducting a harsh technical peer review of our own manuscript was an invaluable exercise in critical academic writing. It forced us to confront the pathological inflation of coverage-per-token in the k=1 baseline and clearly separate evidence selection from generative reader capabilities. Addressing these major concerns before submission makes the paper robust, honest, and defensible in any viva or examination.

---

### Entry 09: Post-Freeze Algorithm Refactoring & Proxy Nomenclature Alignment
- **Task**: Save git version of `src/selection.py` to `src/selection_old.py`, evaluate old vs revised version on all 500 questions across both retrievers, update caller signatures, add unit tests, regenerate tables/figures/results_summary, and rename method to "Score-Gap Adaptive-k Proxy".
- **User Prompt / Instruction**: Implement new signature `(ranked_indices, sorted_scores) -> (selected, k)` with flat-score fallback of 3; verify whether any question differs on 500 samples; rename method consistently across scripts, CSVs, figures, summary, README, and paper.
- **AI Proposal**: Re-implemented `src/selection.py` with pure Python, defensive input validation (NaN/non-finite check, descending order check, length match check); created `scripts/compare_selection.py` to evaluate all 500 questions $\times$ 2 retrievers (1,000 runs total).
- **Outcome / Real Observations**:
  - Comparison showed **0 differing questions** out of 500 on BM25 (mean $k=2.2200$ for both old and new) and **0 differing questions** on TF-IDF (mean $k=2.0180$ for both old and new).
  - Added 5 new unit tests in `tests/test_selection.py` (flat scores fallback to $k=3$, single candidate returns $k=1$, unsorted scores raise `ValueError`, tied gaps select first occurrence, and NaN scores raise `ValueError`). All 21 test suite cases passed in 2.12 seconds.
  - Renamed method to "Score-Gap Adaptive-k Proxy" consistently across scripts, CSV labels, figure legends, `results_summary.md`, `README.md`, and `paper/main.tex`.
  - Logged dated deviation in `research_decisions.md`.
- **Human Reflection**:
  > Refining the algorithm and adopting the honest nomenclature 'Score-Gap Adaptive-k Proxy' reinforces the highest standards of scientific integrity. It ensures that our paper accurately distinguishes between an experimental score-gap heuristic implemented for sparse retrievers and the full dense-probability formulation published by Taguchi et al. (2025). Most importantly, running an empirical side-by-side audit on all 500 questions proved that our refactored implementation produced 100% numerically identical selections while adding robust contractual safeguards.
