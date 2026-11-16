"""
scripts/matched_budget.py - Matched-Budget Comparative Evaluation:
Compares Score-Gap Adaptive-k Proxy with Fixed-k baselines (k=1, exploratory k=2, and k=3).
Computes paired question-level percentile bootstrap 95% CIs (1,000 resamples, seed 0).
Generates results/tables/table3_matched_budget.csv and a publication-ready LaTeX table.
"""

import sys
import os
import time
import numpy as np
import pandas as pd
from scipy.stats import bootstrap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data import load_and_validate_dataset
from src.retrieval import BM25Retriever, TFIDFRetriever
from src.selection import select_fixed_k
from src.evaluation import compute_retrieval_metrics


def bootstrap_ci(values, n_boot=1000, seed=0, ci=0.95):
    """
    Computes 95% percentile bootstrap confidence intervals.
    """
    vals = np.asarray(values, dtype=float)
    if len(vals) == 0:
        return 0.0, 0.0, 0.0
    if len(np.unique(vals)) == 1:
        v = float(vals[0])
        return v, v, v
    
    rng = np.random.RandomState(seed)
    res = bootstrap(
        (vals,),
        np.mean,
        n_resamples=n_boot,
        confidence_level=ci,
        random_state=rng,
        method="percentile"
    )
    return float(np.mean(vals)), float(res.confidence_interval.low), float(res.confidence_interval.high)


def ensure_exploratory_fixed_2(csv_path):
    """
    Runs exploratory fixed k=2 evaluation for both BM25 and TF-IDF if not already present in results.csv.
    Appends the 1,000 exploratory rows without modifying any existing rows.
    """
    df = pd.read_csv(csv_path)
    existing_methods = df["method"].unique()
    
    if "fixed_2" in existing_methods:
        print(f"[INFO] Exploratory fixed_2 already present in {csv_path} ({len(df)} total rows).")
        return df

    print("[ACTION] Running exploratory fixed k=2 baseline for BM25 and TF-IDF (N=500 questions)...")
    records, _ = load_and_validate_dataset(n_samples=500)
    retrievers = {
        "BM25": BM25Retriever(),
        "TF-IDF": TFIDFRetriever()
    }
    
    new_rows = []
    for rec in records:
        q_id = rec["id"]
        question = rec["question"]
        candidates = rec["candidates"]
        gold_indices = [i for i, c in enumerate(candidates) if c["is_gold"]]
        multi_flag = rec["is_multi_evidence"]
        q_type = rec["type"]
        
        for ret_name, retriever in retrievers.items():
            t0 = time.perf_counter()
            ranked_idx, sorted_scores = retriever.rank(question, candidates)
            rank_latency = time.perf_counter() - t0
            
            t_sel0 = time.perf_counter()
            selected = select_fixed_k(ranked_idx, 2)
            sel_latency = time.perf_counter() - t_sel0
            total_latency_ms = (rank_latency + sel_latency) * 1000.0
            
            m = compute_retrieval_metrics(selected, gold_indices, candidates)
            new_rows.append({
                "id": q_id,
                "retriever": ret_name,
                "method": "fixed_2",
                "k_selected": 2,
                "recall": m["evidence_recall"],
                "full_coverage": m["full_coverage"],
                "precision": m["precision"],
                "words": m["selected_words"],
                "tokens": m["selected_tokens"],
                "coverage_per_1000_tokens": m["coverage_per_1000_tokens"],
                "latency_ms": round(total_latency_ms, 3),
                "multi_evidence_flag": multi_flag,
                "question_type": q_type
            })

    df_new = pd.DataFrame(new_rows)
    df_combined = pd.concat([df, df_new], ignore_index=True)
    df_combined.to_csv(csv_path, index=False)
    print(f"[SUCCESS] Appended 1,000 exploratory fixed_2 rows. Total rows in {csv_path}: {len(df_combined)}")
    return df_combined


def main():
    print("=" * 78)
    print("MATCHED-BUDGET COMPARATIVE EVALUATION SCRIPT")
    print("=" * 78)
    
    csv_path = os.path.join("results", "tables", "results.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing results file: {csv_path}")

    # 1. Ensure exploratory fixed_2 is evaluated and logged in results.csv
    df = ensure_exploratory_fixed_2(csv_path)

    retrievers = ["BM25", "TF-IDF"]
    proxy_name = "Score-Gap Adaptive-k Proxy"
    fixed_configs = [
        ("fixed_1", "Fixed k=1", 1.0),
        ("fixed_2", "Fixed k=2 (Exploratory)", 2.0),
        ("fixed_3", "Fixed k=3 (Nearest Budget)", 3.0),
    ]

    metrics = [
        ("recall", "Evidence Recall", False),
        ("full_coverage", "Full Coverage %", True),
        ("precision", "Precision", False),
        ("tokens", "Selected Tokens", False)
    ]

    # 2. Sanity Check / Comparison with existing results.csv numbers
    print("\n--- BASELINE MEAN SANITY CHECK (MUST MATCH EXISTING RESULTS.CSV EXACTLY) ---")
    print(f"{'Retriever':<8} | {'Method':<28} | {'Recall':<8} | {'Full Cov %':<10} | {'Precision':<10} | {'Tokens':<8}")
    print("-" * 80)
    for ret in retrievers:
        for m_id, m_label, _ in [("fixed_3", "Fixed k=3", 3.0), (proxy_name, proxy_name, 2.22)]:
            sub = df[(df["retriever"] == ret) & (df["method"] == m_id)]
            r_mean = sub["recall"].mean()
            c_mean = sub["full_coverage"].mean() * 100
            p_mean = sub["precision"].mean()
            t_mean = sub["tokens"].mean()
            print(f"{ret:<8} | {m_label:<28} | {r_mean:<8.4f} | {c_mean:<9.2f}% | {p_mean:<10.4f} | {t_mean:<8.2f}")
    print("-" * 80)

    # 3. Compute Bootstrap CIs and Paired Differences
    csv_all_rows = []
    latex_rows = []

    for ret in retrievers:
        df_ret = df[df["retriever"] == ret]
        pivot_dict = {}
        for m_id in ["fixed_1", "fixed_2", "fixed_3", proxy_name]:
            sub = df_ret[df_ret["method"] == m_id].sort_values("id")
            pivot_dict[m_id] = sub

        proxy_sub = pivot_dict[proxy_name]
        k_proxy_mean = float(proxy_sub["k_selected"].mean())

        # Method level stats for Fixed configs
        for f_id, f_label, f_k in fixed_configs:
            f_sub = pivot_dict[f_id]
            f_row = {
                "Retriever": ret,
                "Row_Type": "Configuration Baseline",
                "Label": f_label,
                "Mean_k": f_k,
            }
            for m_key, m_name, is_pct in metrics:
                vals = f_sub[m_key].values
                if is_pct:
                    vals = vals * 100.0
                m_val, l_val, u_val = bootstrap_ci(vals, seed=0)
                f_row[f"{m_key}_mean"] = round(m_val, 4)
                f_row[f"{m_key}_ci_low"] = round(l_val, 4)
                f_row[f"{m_key}_ci_upp"] = round(u_val, 4)
            csv_all_rows.append(f_row)

        # Method level stats for Proxy
        proxy_row = {
            "Retriever": ret,
            "Row_Type": "Configuration Baseline",
            "Label": proxy_name,
            "Mean_k": round(k_proxy_mean, 2),
        }
        proxy_stats = {}
        for m_key, m_name, is_pct in metrics:
            vals = proxy_sub[m_key].values
            if is_pct:
                vals = vals * 100.0
            m_val, l_val, u_val = bootstrap_ci(vals, seed=0)
            proxy_stats[m_key] = (m_val, l_val, u_val)
            proxy_row[f"{m_key}_mean"] = round(m_val, 4)
            proxy_row[f"{m_key}_ci_low"] = round(l_val, 4)
            proxy_row[f"{m_key}_ci_upp"] = round(u_val, 4)
        csv_all_rows.append(proxy_row)

        # Baseline LaTeX rows for this retriever
        f1_stats = {m: bootstrap_ci(pivot_dict['fixed_1'][m].values * (100 if is_p else 1), seed=0) for m, _, is_p in metrics}
        f2_stats = {m: bootstrap_ci(pivot_dict['fixed_2'][m].values * (100 if is_p else 1), seed=0) for m, _, is_p in metrics}
        f3_stats = {m: bootstrap_ci(pivot_dict['fixed_3'][m].values * (100 if is_p else 1), seed=0) for m, _, is_p in metrics}

        latex_rows.append(f"\\textbf{{{ret}}} & Fixed $k=1$ & 1.00 & "
                          f"{f1_stats['recall'][0]:.3f} [{f1_stats['recall'][1]:.3f}, {f1_stats['recall'][2]:.3f}] & "
                          f"{f1_stats['full_coverage'][0]:.1f}\\% [{f1_stats['full_coverage'][1]:.1f}\\%, {f1_stats['full_coverage'][2]:.1f}\\%] & "
                          f"{f1_stats['precision'][0]:.3f} [{f1_stats['precision'][1]:.3f}, {f1_stats['precision'][2]:.3f}] & "
                          f"{f1_stats['tokens'][0]:.1f} [{f1_stats['tokens'][1]:.1f}, {f1_stats['tokens'][2]:.1f}] \\\\")

        latex_rows.append(f" & Fixed $k=2$ (Exploratory) & 2.00 & "
                          f"{f2_stats['recall'][0]:.3f} [{f2_stats['recall'][1]:.3f}, {f2_stats['recall'][2]:.3f}] & "
                          f"{f2_stats['full_coverage'][0]:.1f}\\% [{f2_stats['full_coverage'][1]:.1f}\\%, {f2_stats['full_coverage'][2]:.1f}\\%] & "
                          f"{f2_stats['precision'][0]:.3f} [{f2_stats['precision'][1]:.3f}, {f2_stats['precision'][2]:.3f}] & "
                          f"{f2_stats['tokens'][0]:.1f} [{f2_stats['tokens'][1]:.1f}, {f2_stats['tokens'][2]:.1f}] \\\\")

        latex_rows.append(f" & Fixed $k=3$ (Nearest Budget) & 3.00 & "
                          f"{f3_stats['recall'][0]:.3f} [{f3_stats['recall'][1]:.3f}, {f3_stats['recall'][2]:.3f}] & "
                          f"{f3_stats['full_coverage'][0]:.1f}\\% [{f3_stats['full_coverage'][1]:.1f}\\%, {f3_stats['full_coverage'][2]:.1f}\\%] & "
                          f"{f3_stats['precision'][0]:.3f} [{f3_stats['precision'][1]:.3f}, {f3_stats['precision'][2]:.3f}] & "
                          f"{f3_stats['tokens'][0]:.1f} [{f3_stats['tokens'][1]:.1f}, {f3_stats['tokens'][2]:.1f}] \\\\")

        latex_rows.append(f" & \\textbf{{Score-Gap Adaptive-$k$ Proxy}} & {k_proxy_mean:.2f} & "
                          f"{proxy_stats['recall'][0]:.3f} [{proxy_stats['recall'][1]:.3f}, {proxy_stats['recall'][2]:.3f}] & "
                          f"{proxy_stats['full_coverage'][0]:.1f}\\% [{proxy_stats['full_coverage'][1]:.1f}\\%, {proxy_stats['full_coverage'][2]:.1f}\\%] & "
                          f"{proxy_stats['precision'][0]:.3f} [{proxy_stats['precision'][1]:.3f}, {proxy_stats['precision'][2]:.3f}] & "
                          f"{proxy_stats['tokens'][0]:.1f} [{proxy_stats['tokens'][1]:.1f}, {proxy_stats['tokens'][2]:.1f}] \\\\")

        latex_rows.append("\\cmidrule(lr){2-7}")

        # Compute paired differences
        for f_id, f_label, f_k in fixed_configs:
            fix_sub = pivot_dict[f_id]
            diff_dict = {
                "Retriever": ret,
                "Row_Type": "Paired Difference (Proxy - Fixed)",
                "Label": f"Proxy vs {f_label}",
                "Mean_k": round(k_proxy_mean - f_k, 2),
            }
            
            diff_cells = []
            for m_key, m_name, is_pct in metrics:
                p_vals = proxy_sub[m_key].values
                f_vals = fix_sub[m_key].values
                if is_pct:
                    p_vals = p_vals * 100.0
                    f_vals = f_vals * 100.0
                
                diff_vals = p_vals - f_vals
                d_mean, d_low, d_upp = bootstrap_ci(diff_vals, seed=0)
                
                diff_dict[f"{m_key}_mean"] = round(d_mean, 4)
                diff_dict[f"{m_key}_ci_low"] = round(d_low, 4)
                diff_dict[f"{m_key}_ci_upp"] = round(d_upp, 4)

                sign_str = "+" if d_mean >= 0 else ""
                sign_low = "+" if d_low >= 0 else ""
                sign_upp = "+" if d_upp >= 0 else ""
                if is_pct:
                    diff_cells.append(f"{sign_str}{d_mean:.1f}\\% [{sign_low}{d_low:.1f}\\%, {sign_upp}{d_upp:.1f}\\%]")
                elif m_key == "tokens":
                    diff_cells.append(f"{sign_str}{d_mean:.1f} [{sign_low}{d_low:.1f}, {sign_upp}{d_upp:.1f}]")
                else:
                    diff_cells.append(f"{sign_str}{d_mean:.3f} [{sign_low}{d_low:.3f}, {sign_upp}{d_upp:.3f}]")

            csv_all_rows.append(diff_dict)
            delta_k_sign = "+" if (k_proxy_mean - f_k) >= 0 else ""
            latex_rows.append(f" & \\textit{{Paired Diff: Proxy $-$ {f_label.split(' (')[0]}}} & {delta_k_sign}{k_proxy_mean - f_k:.2f} & "
                              f"{diff_cells[0]} & {diff_cells[1]} & {diff_cells[2]} & {diff_cells[3]} \\\\")

        if ret == "BM25":
            latex_rows.append("\\midrule")

    # 4. Save CSV
    out_csv_path = os.path.join("results", "tables", "table3_matched_budget.csv")
    df_out = pd.DataFrame(csv_all_rows)
    df_out.to_csv(out_csv_path, index=False)
    print(f"\n[OUTPUT] Saved matched budget evaluation (baselines + paired diffs) to: {out_csv_path}")

    # 5. Build and Save LaTeX Table
    latex_table = "\\begin{table*}[t]\n" \
                  "\\centering\n" \
                  "\\caption{Matched-Budget Comparative Evaluation: Score-Gap Adaptive-$k$ Proxy versus Fixed-$k$ Baselines ($k \\in \\{1, 2, 3\\}$) on HotpotQA ($N=500$). Mean values with 95\\% Bootstrap Confidence Intervals and Paired Question-Level Differences ($\\Delta = \\text{Proxy} - \\text{Fixed}$, 1,000 resamples, seed 0). Coverage and Full Coverage are reported as percentages.}\n" \
                  "\\label{tab:matched_budget}\n" \
                  "\\begin{tabular}{llrcccc}\n" \
                  "\\toprule\n" \
                  "\\textbf{Retriever} & \\textbf{Configuration / Comparison} & \\textbf{Mean $k$} & \\textbf{Evidence Recall} & \\textbf{Full Coverage \\%} & \\textbf{Precision} & \\textbf{Selected Tokens} \\\\\n" \
                  "\\midrule\n" + \
                  "\n".join(latex_rows) + "\n" \
                  "\\bottomrule\n" \
                  "\\end{tabular}\n" \
                  "\\end{table*}\n"

    out_tex_path = os.path.join("paper", "table3_matched_budget.tex")
    with open(out_tex_path, "w", encoding="utf-8") as f:
        f.write(latex_table)
    print(f"[OUTPUT] Saved LaTeX table to: {out_tex_path}")

    print("\n" + "=" * 78)
    print("GENERATED LATEX TABLE (table*):")
    print("=" * 78)
    print(latex_table)
    print("=" * 78)


if __name__ == "__main__":
    main()
