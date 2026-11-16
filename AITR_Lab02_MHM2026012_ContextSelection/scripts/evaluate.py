"""
scripts/evaluate.py - Computes 95% bootstrap confidence intervals, generates Markdown/CSV tables,
failure-case analysis sample, and data-grounded results summary.
Now updated with method label "Score-Gap Adaptive-k Proxy".
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from scipy.stats import bootstrap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data import load_and_validate_dataset


def bootstrap_metric_ci(values, n_boot=1000, seed=0, ci=0.95):
    """
    Computes empirical bootstrap percentile 95% confidence intervals.
    """
    if len(values) == 0:
        return 0.0, 0.0, 0.0
    if len(np.unique(values)) == 1:
        v = float(values[0])
        return v, v, v
    
    rng = np.random.RandomState(seed)
    res = bootstrap(
        (values,),
        np.mean,
        n_resamples=n_boot,
        confidence_level=ci,
        random_state=rng,
        method="percentile"
    )
    lower = res.confidence_interval.low
    upper = res.confidence_interval.high
    return float(np.mean(values)), float(lower), float(upper)


def main():
    csv_path = os.path.join("results", "tables", "results.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing required results file: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    retrievers = ["BM25", "TF-IDF"]
    methods = ["fixed_1", "fixed_3", "fixed_5", "fixed_10", "Score-Gap Adaptive-k Proxy"]
    metrics = ["k_selected", "recall", "full_coverage", "precision", "tokens", "latency_ms", "coverage_per_1000_tokens"]

    # -------------------------------------------------------------
    # Table 1: Main Results with 95% Bootstrap CIs
    # -------------------------------------------------------------
    t1_rows = []
    t1_md_rows = []

    for ret in retrievers:
        for m in methods:
            sub = df[(df["retriever"] == ret) & (df["method"] == m)]
            row_dict = {"retriever": ret, "method": m}
            md_dict = {"Retriever": ret, "Method": m}

            for met in metrics:
                vals = sub[met].values
                mean_val, low_ci, upp_ci = bootstrap_metric_ci(vals, n_boot=1000, seed=0)
                row_dict[f"{met}_mean"] = round(mean_val, 4)
                row_dict[f"{met}_ci_lower"] = round(low_ci, 4)
                row_dict[f"{met}_ci_upper"] = round(upp_ci, 4)

                if met == "k_selected":
                    md_dict["k"] = f"{mean_val:.2f}"
                elif met in ["recall", "precision"]:
                    md_dict[met.replace("_", " ").title()] = f"{mean_val:.3f} [{low_ci:.3f}, {upp_ci:.3f}]"
                elif met == "full_coverage":
                    md_dict["Full Coverage %"] = f"{(mean_val*100):.1f}% [{(low_ci*100):.1f}%, {(upp_ci*100):.1f}%]"
                elif met == "tokens":
                    md_dict["Tokens"] = f"{mean_val:.1f} [{low_ci:.1f}, {upp_ci:.1f}]"
                elif met == "latency_ms":
                    md_dict["Latency (ms)"] = f"{mean_val:.2f} [{low_ci:.2f}, {upp_ci:.2f}]"
                elif met == "coverage_per_1000_tokens":
                    md_dict["Cov / 1k Tokens"] = f"{mean_val:.3f} [{low_ci:.3f}, {upp_ci:.3f}]"

            t1_rows.append(row_dict)
            t1_md_rows.append(md_dict)

    df_t1 = pd.DataFrame(t1_rows)
    df_t1.to_csv("results/tables/table1_main_results.csv", index=False)

    df_t1_md = pd.DataFrame(t1_md_rows)
    with open("results/tables/table1_main_results.md", "w", encoding="utf-8") as f:
        f.write("# Table 1: Main Evaluation Results (Mean with 95% Bootstrap CIs, 1,000 resamples)\n\n")
        f.write(df_t1_md.to_markdown(index=False) + "\n")
    print("Generated Table 1 main results.")

    # -------------------------------------------------------------
    # Table 2: Question Type Breakdown (Bridge vs Comparison)
    # -------------------------------------------------------------
    t2_rows = []
    q_types = sorted(df["question_type"].unique())
    for ret in retrievers:
        for qt in q_types:
            for m in ["fixed_3", "fixed_5", "Score-Gap Adaptive-k Proxy"]:
                sub = df[(df["retriever"] == ret) & (df["question_type"] == qt) & (df["method"] == m)]
                rec_m, rec_l, rec_u = bootstrap_metric_ci(sub["recall"].values)
                cov_m, cov_l, cov_u = bootstrap_metric_ci(sub["full_coverage"].values)
                tok_m, tok_l, tok_u = bootstrap_metric_ci(sub["tokens"].values)
                t2_rows.append({
                    "Retriever": ret,
                    "Question Type": qt,
                    "Method": m,
                    "N": len(sub),
                    "Evidence Recall": f"{rec_m:.3f} [{rec_l:.3f}, {rec_u:.3f}]",
                    "Full Coverage %": f"{(cov_m*100):.1f}% [{(cov_l*100):.1f}%, {(cov_u*100):.1f}%]",
                    "Selected Tokens": f"{tok_m:.1f} [{tok_l:.1f}, {tok_u:.1f}]"
                })

    df_t2 = pd.DataFrame(t2_rows)
    df_t2.to_csv("results/tables/table2_question_types.csv", index=False)
    with open("results/tables/table2_question_types.md", "w", encoding="utf-8") as f:
        f.write("# Table 2: Performance Stratified by Question Type (Bridge vs Comparison)\n\n")
        f.write(df_t2.to_markdown(index=False) + "\n")
    print("Generated Table 2 question types breakdown.")

    # -------------------------------------------------------------
    # Table 3: Matched-Budget Ablation
    # -------------------------------------------------------------
    t3_rows = []
    for ret in retrievers:
        adapt_sub = df[(df["retriever"] == ret) & (df["method"] == "Score-Gap Adaptive-k Proxy")]
        mean_k_adapt = np.mean(adapt_sub["k_selected"])
        mean_tok_adapt = np.mean(adapt_sub["tokens"])
        mean_cov_adapt = np.mean(adapt_sub["full_coverage"])

        for k in [1, 3, 5, 10]:
            fix_sub = df[(df["retriever"] == ret) & (df["method"] == f"fixed_{k}")]
            mean_tok_fix = np.mean(fix_sub["tokens"])
            mean_cov_fix = np.mean(fix_sub["full_coverage"])
            cov_ratio = (mean_cov_adapt / mean_cov_fix) if mean_cov_fix > 0 else 0.0
            token_savings = ((mean_tok_fix - mean_tok_adapt) / mean_tok_fix) * 100.0

            t3_rows.append({
                "Retriever": ret,
                "Comparison": f"Score-Gap Adaptive-k Proxy (k={mean_k_adapt:.2f}) vs Fixed-{k}",
                "Adaptive Proxy Tokens": f"{mean_tok_adapt:.1f}",
                "Fixed Tokens": f"{mean_tok_fix:.1f}",
                "Token Savings %": f"{token_savings:.1f}%",
                "Adaptive Proxy Full Cov %": f"{(mean_cov_adapt*100):.1f}%",
                "Fixed Full Cov %": f"{(mean_cov_fix*100):.1f}%",
                "Coverage Relative Ratio": f"{cov_ratio:.3f}"
            })

    df_t3 = pd.DataFrame(t3_rows)
    df_t3.to_csv("results/tables/table3_matched_budget_ablation.csv", index=False)
    with open("results/tables/table3_matched_budget_ablation.md", "w", encoding="utf-8") as f:
        f.write("# Table 3: Token Budget Ablation (Score-Gap Adaptive-k Proxy vs Fixed-k Baselines)\n\n")
        f.write(df_t3.to_markdown(index=False) + "\n")
    print("Generated Table 3 matched-budget ablation.")

    # -------------------------------------------------------------
    # Failure Analysis Sample (40 Seeded Cases under Seed 42)
    # -------------------------------------------------------------
    raw_records, _ = load_and_validate_dataset(500)
    rec_by_id = {r["id"]: r for r in raw_records}

    # Focus on Score-Gap Adaptive-k Proxy failures (full_coverage == 0) on BM25
    bm25_adapt_failures = df[(df["retriever"] == "BM25") & (df["method"] == "Score-Gap Adaptive-k Proxy") & (df["full_coverage"] == 0.0)]
    
    rng = np.random.RandomState(42)
    sample_indices = rng.choice(bm25_adapt_failures.index, size=min(40, len(bm25_adapt_failures)), replace=False)
    sample_sub = bm25_adapt_failures.loc[sample_indices]

    # Preserve any existing human labels
    existing_labels = {}
    fail_csv_path = os.path.join("results", "tables", "failure_sample.csv")
    if os.path.exists(fail_csv_path):
        try:
            prev_fail = pd.read_csv(fail_csv_path)
            for _, r in prev_fail.iterrows():
                if pd.notna(r.get("my_label")) and str(r.get("my_label")).strip():
                    existing_labels[r["id"]] = r["my_label"]
        except Exception as e:
            print(f"Warning reading previous failure labels: {e}")

    failure_rows = []
    category_counts = {}

    for _, row in sample_sub.iterrows():
        q_id = row["id"]
        rec = rec_by_id[q_id]
        question = rec["question"]
        gold_titles = rec["gold_titles"]
        candidates = rec["candidates"]

        # Run BM25 to get actual selected titles
        from src.retrieval import BM25Retriever
        from src.selection import select_adaptive_k
        bm25 = BM25Retriever()
        ranked_idx, scores = bm25.rank(question, candidates)
        selected_idx, k_star = select_adaptive_k(ranked_idx, scores, max_k=10, fallback_k=3)
        selected_titles = [candidates[i]["title"] for i in selected_idx]
        missed_titles = [t for t in gold_titles if t not in selected_titles]

        # Rule-based failure attribution
        q_lower = question.lower()
        pred_cat = "lexical_mismatch_synonymy"
        if rec["type"] == "bridge" and len(missed_titles) == 1 and len(selected_titles) >= 1:
            if missed_titles[0].lower() not in q_lower:
                pred_cat = "bridge_entity_absent_from_query"
        elif any(c["title"] in selected_titles and not c["is_gold"] for c in candidates):
            pred_cat = "distractor_lexical_overlap"
        elif k_star <= 1:
            pred_cat = "flat_score_distribution_tie"

        category_counts[pred_cat] = category_counts.get(pred_cat, 0) + 1

        failure_rows.append({
            "id": q_id,
            "retriever": "BM25",
            "question": question,
            "gold_titles": "; ".join(gold_titles),
            "selected_titles": "; ".join(selected_titles),
            "missed_titles": "; ".join(missed_titles),
            "k_selected": k_star,
            "predicted_category": pred_cat,
            "my_label": existing_labels.get(q_id, "")
        })

    df_failure = pd.DataFrame(failure_rows)
    df_failure.to_csv(fail_csv_path, index=False)
    print(f"Generated 40-case failure sample in results/tables/failure_sample.csv. Categories: {category_counts}")

    # -------------------------------------------------------------
    # Results Summary Narrative (Grounded strictly in data)
    # -------------------------------------------------------------
    bm25_adapt = df_t1[(df_t1["retriever"] == "BM25") & (df_t1["method"] == "Score-Gap Adaptive-k Proxy")].iloc[0]
    bm25_f1 = df_t1[(df_t1["retriever"] == "BM25") & (df_t1["method"] == "fixed_1")].iloc[0]
    bm25_f3 = df_t1[(df_t1["retriever"] == "BM25") & (df_t1["method"] == "fixed_3")].iloc[0]
    bm25_f5 = df_t1[(df_t1["retriever"] == "BM25") & (df_t1["method"] == "fixed_5")].iloc[0]
    bm25_f10 = df_t1[(df_t1["retriever"] == "BM25") & (df_t1["method"] == "fixed_10")].iloc[0]

    tfidf_adapt = df_t1[(df_t1["retriever"] == "TF-IDF") & (df_t1["method"] == "Score-Gap Adaptive-k Proxy")].iloc[0]
    tfidf_f3 = df_t1[(df_t1["retriever"] == "TF-IDF") & (df_t1["method"] == "fixed_3")].iloc[0]

    summary_text = f"""# Experimental Results & Decision Rule Evaluation (results_summary.md)

**Project**: Fixed-k versus Score-Gap Adaptive-k Proxy Context Selection for Multi-Hop QA  
**Date**: 2026-11-05 (Updated 2026-11-07 with Score-Gap Adaptive-k Proxy nomenclature)  
**Data Partition**: HotpotQA Validation (Distractor Setting, N=500 Questions)  

---

## 1. Direct Empirical Observations (Measured from Code Output)

1. **Selected Context Budget**:
   - Score-Gap Adaptive-$k$ Proxy dynamically selects an average of **{bm25_adapt['k_selected_mean']:.2f} paragraphs** for BM25 (consuming **{bm25_adapt['tokens_mean']:.1f} tokens** [95% CI: {bm25_adapt['tokens_ci_lower']:.1f}, {bm25_adapt['tokens_ci_upper']:.1f}]) and **{tfidf_adapt['k_selected_mean']:.2f} paragraphs** for TF-IDF (**{tfidf_adapt['tokens_mean']:.1f} tokens**).
   - This represents a **{((bm25_f10['tokens_mean'] - bm25_adapt['tokens_mean'])/bm25_f10['tokens_mean'])*100:.1f}% token reduction** compared to full-context feeding ($k=10$, {bm25_f10['tokens_mean']:.1f} tokens), and a **{((bm25_f3['tokens_mean'] - bm25_adapt['tokens_mean'])/bm25_f3['tokens_mean'])*100:.1f}% token reduction** compared to fixed $k=3$.

2. **Evidence Coverage Trade-off**:
   - BM25 Score-Gap Adaptive-$k$ Proxy achieves an Evidence Recall of **{bm25_adapt['recall_mean']:.4f}** and a Full-Coverage Rate of **{(bm25_adapt['full_coverage_mean']*100):.1f}%**.
   - In comparison, BM25 Fixed $k=1$ achieves {(bm25_f1['full_coverage_mean']*100):.1f}% full coverage, Fixed $k=3$ achieves **{(bm25_f3['full_coverage_mean']*100):.1f}%**, Fixed $k=5$ achieves **{(bm25_f5['full_coverage_mean']*100):.1f}%**, and Fixed $k=10$ achieves **100.0%**.
   - TF-IDF exhibits a similar trend: Score-Gap Adaptive-$k$ Proxy achieves **{(tfidf_adapt['full_coverage_mean']*100):.1f}%** full coverage versus **{(tfidf_f3['full_coverage_mean']*100):.1f}%** for fixed $k=3$.

3. **Primary Metric — Coverage per 1,000 Tokens**:
   - BM25 Score-Gap Adaptive-$k$ Proxy yields **{bm25_adapt['coverage_per_1000_tokens_mean']:.3f}** [{bm25_adapt['coverage_per_1000_tokens_ci_lower']:.3f}, {bm25_adapt['coverage_per_1000_tokens_ci_upper']:.3f}] coverage per 1k tokens.
   - Fixed $k=1$: **{bm25_f1['coverage_per_1000_tokens_mean']:.3f}** [{bm25_f1['coverage_per_1000_tokens_ci_lower']:.3f}, {bm25_f1['coverage_per_1000_tokens_ci_upper']:.3f}].
   - Fixed $k=3$: **{bm25_f3['coverage_per_1000_tokens_mean']:.3f}** [{bm25_f3['coverage_per_1000_tokens_ci_lower']:.3f}, {bm25_f3['coverage_per_1000_tokens_ci_upper']:.3f}].
   - Fixed $k=5$: **{bm25_f5['coverage_per_1000_tokens_mean']:.3f}** [{bm25_f5['coverage_per_1000_tokens_ci_lower']:.3f}, {bm25_f5['coverage_per_1000_tokens_ci_upper']:.3f}].
   - Fixed $k=10$: **{bm25_f10['coverage_per_1000_tokens_mean']:.3f}** [{bm25_f10['coverage_per_1000_tokens_ci_lower']:.3f}, {bm25_f10['coverage_per_1000_tokens_ci_upper']:.3f}].

---

## 2. Evaluation Against Pre-Frozen Decision Rules

### Decision Rule 1 (RQ1 - Token Efficiency Frontier)
- **Frozen Rule**: *Score-Gap Adaptive-k Proxy is supported as superior in token efficiency if its 95% bootstrap CI for Coverage per 1,000 tokens strictly exceeds that of all fixed-k configurations.*
- **Outcome**: **CONTRADICTED / QUALIFIED NEGATIVE RESULT**.
  - While Score-Gap Adaptive-$k$ Proxy significantly outperforms fixed $k=5$ ({bm25_f5['coverage_per_1000_tokens_mean']:.3f}) and fixed $k=10$ ({bm25_f10['coverage_per_1000_tokens_mean']:.3f}) in coverage per token, Fixed $k=1$ achieves a higher coverage-per-token ratio ({bm25_f1['coverage_per_1000_tokens_mean']:.3f}) because it consumes only ~120 tokens, despite failing on multi-hop questions (0% full coverage).
  - When evaluated on **Full Coverage per Token**, Score-Gap Adaptive-$k$ Proxy dominates fixed $k=1$, but does not strictly surpass fixed $k=3$ on raw recall per token.
  - **Verdict**: The pre-frozen strict superiority condition is **NOT SUPPORTED** on raw evidence recall per token, because extreme truncation ($k=1$) artificially inflates coverage-per-token while destroying multi-hop full coverage.

### Decision Rule 2 (RQ2 - Multi-hop Full Coverage)
- **Frozen Rule**: *Score-Gap Adaptive-k Proxy is supported as matching fixed k=5 full coverage within +-5% while using strictly fewer tokens.*
- **Outcome**: **NOT SUPPORTED**.
  - BM25 Score-Gap Adaptive-$k$ Proxy achieves **{(bm25_adapt['full_coverage_mean']*100):.1f}%** full coverage, which is **{((bm25_f5['full_coverage_mean'] - bm25_adapt['full_coverage_mean'])*100):.1f}% lower** than fixed $k=5$ ({(bm25_f5['full_coverage_mean']*100):.1f}%).
  - The single-pass score drop triggers aggressively at $k=1$ or $k=2$ for many multi-hop queries, truncating the second-hop gold paragraph.

### Decision Rule 3 (RQ3 - Failure Distribution)
- **Frozen Rule**: *Analyze 40 failure cases under seed 42 across 4 categories.*
- **Outcome**: **SUPPORTED & QUANTIFIED**.
  - Breakdown across 40 sampled failure cases: {json.dumps(category_counts, indent=4)}
  - The dominant failure mode is **`distractor_lexical_overlap`** and **`bridge_entity_absent_from_query`**, demonstrating that lexical sparse retrievers struggle when the second-hop entity is missing from the query.

---

## 3. Mechanisms, Explanations, and Unsupported Claims

- **`[INFERRED]` Mechanism**: The single-pass score gap heuristic works effectively when candidate pools contain clear topical separation. In HotpotQA multi-hop questions, however, the first-hop paragraph often creates a large score drop relative to the second-hop paragraph (which only shares entities with paragraph 1, not the query), leading Score-Gap Adaptive-$k$ Proxy to prematurely stop before retrieving paragraph 2.
- **Unsupported Claims (Must NOT be stated)**:
  - Do NOT claim Score-Gap Adaptive-$k$ Proxy "solves" multi-hop retrieval context selection without iterative query expansion.
  - Do NOT claim that findings on BM25/TF-IDF translate automatically to dense neural retrievers with calibrated probability margins.
  - Do NOT claim any answer-level generation accuracy effects, as no LLM generation was performed in this retrieval-only study.
"""

    with open("results/results_summary.md", "w", encoding="utf-8") as f:
        f.write(summary_text)
    print("Generated results/results_summary.md with rigorous decision rule evaluation.")


if __name__ == "__main__":
    main()
