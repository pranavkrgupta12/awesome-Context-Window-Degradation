# Data Access, Licensing, and Preprocessing Protocol

## 1. Overview
This directory governs datasets evaluated in the project. In accordance with the non-negotiable research rules, raw datasets are not committed directly to the git repository if restricted or large. Instead, deterministic download and construction scripts are provided.

## 2. Dataset Selection Criteria
To support reproducible evaluation of long-context degradation and retrieval mitigation, candidate datasets must satisfy:
1. **Public Accessibility & Open License**: Permissive license (e.g., Apache 2.0, MIT, CC-BY) for academic research.
2. **Context Length Suitability**: Ability to construct controlled sequences ranging from $2\text{K}$ to $16\text{K}+$ tokens.
3. **Controlled Evidence Placement**: Clear division into target evidence (needle / gold context) and controlled distractor documents / background text.
4. **Unambiguous Ground Truth**: Questions with exact answers or reference spans suited for objective Exact Match (EM) and token F1 scoring.
5. **No Data Leakage**: Clear separation of test queries from prompt background, with no query-answer leakage during retrieval indexing.

## 3. Directory Layout
```
data/
├── README.md               # This specification document
├── raw/                    # Raw downloaded files (git-ignored)
├── processed/              # Formatted evaluation sets with controlled positions
└── splits/                 # Frozen train/dev/test splits with locked seeds
```

## 4. Current Status: `[UNKNOWN]`
- A candidate dataset (such as NaturalQuestions Multi-doc, SQuAD distractors, or NoLiMa/NIAH long-context partitions) will be verified and frozen during Gate G2.
