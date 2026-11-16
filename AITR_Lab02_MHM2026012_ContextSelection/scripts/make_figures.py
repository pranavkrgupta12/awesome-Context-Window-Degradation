"""
scripts/make_figures.py - Generates publication-ready figures strictly from results.csv.
Now updated with method label "Score-Gap Adaptive-k Proxy".
Outputs:
  - results/figures/figure1_coverage_vs_tokens.png & .pdf
  - results/figures/figure2_question_types.png & .pdf
  - results/figures/figure3_failure_distribution.png & .pdf
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def setup_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--"
    })


def make_figure1_pareto():
    """
    Figure 1: Trade-off between Selected Tokens and Full-Coverage Rate / Evidence Recall.
    """
    df_t1 = pd.read_csv("results/tables/table1_main_results.csv")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0))
    
    colors = {"BM25": "#1f77b4", "TF-IDF": "#ff7f0e"}
    markers = {
        "fixed_1": "o",
        "fixed_3": "s",
        "fixed_5": "^",
        "fixed_10": "D",
        "Score-Gap Adaptive-k Proxy": "*"
    }

    for ret in ["BM25", "TF-IDF"]:
        sub = df_t1[df_t1["retriever"] == ret].copy()
        sub = sub.sort_values(by="tokens_mean")
        
        # Plot 1: Evidence Recall vs Tokens
        ax1.plot(sub["tokens_mean"], sub["recall_mean"], color=colors[ret], linestyle="-", alpha=0.6, label=f"{ret} Frontier")
        for _, row in sub.iterrows():
            m = row["method"]
            is_adapt = (m == "Score-Gap Adaptive-k Proxy")
            size = 150 if is_adapt else 70
            marker = markers.get(m, "o")
            ax1.scatter(row["tokens_mean"], row["recall_mean"], color=colors[ret], marker=marker, s=size, edgecolors="black", zorder=4)
            
            # Label point
            lbl = "Score-Gap\nAdaptive-k Proxy" if is_adapt else f"k={m.split('_')[1]}"
            offset_y = 0.025 if ret == "BM25" else -0.04
            ax1.annotate(lbl, (row["tokens_mean"], row["recall_mean"] + offset_y), fontsize=7.5, ha="center")
            
        # Plot 2: Full Coverage Rate vs Tokens
        ax2.plot(sub["tokens_mean"], sub["full_coverage_mean"] * 100, color=colors[ret], linestyle="-", alpha=0.6, label=f"{ret} Frontier")
        for _, row in sub.iterrows():
            m = row["method"]
            is_adapt = (m == "Score-Gap Adaptive-k Proxy")
            size = 150 if is_adapt else 70
            marker = markers.get(m, "o")
            ax2.scatter(row["tokens_mean"], row["full_coverage_mean"] * 100, color=colors[ret], marker=marker, s=size, edgecolors="black", zorder=4)
            lbl = "Score-Gap\nAdaptive-k Proxy" if is_adapt else f"k={m.split('_')[1]}"
            offset_y = 2.5 if ret == "BM25" else -4.5
            ax2.annotate(lbl, (row["tokens_mean"], row["full_coverage_mean"] * 100 + offset_y), fontsize=7.5, ha="center")

    ax1.set_xlabel("Mean Selected Tokens")
    ax1.set_ylabel("Mean Evidence Recall")
    ax1.set_title("(a) Evidence Recall vs. Context Budget")
    ax1.set_ylim(0.28, 1.05)
    ax1.legend(loc="lower right")

    ax2.set_xlabel("Mean Selected Tokens")
    ax2.set_ylabel("Full Coverage Rate (%)")
    ax2.set_title("(b) Multi-Hop Full Coverage vs. Context Budget")
    ax2.set_ylim(-6, 108)
    ax2.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig("results/figures/figure1_coverage_vs_tokens.png")
    plt.savefig("results/figures/figure1_coverage_vs_tokens.pdf")
    plt.close()
    print("Saved Figure 1 (PNG and PDF).")


def make_figure2_question_types():
    """
    Figure 2: Performance comparison stratified by Question Type (Bridge vs Comparison).
    """
    df_t2 = pd.read_csv("results/tables/table2_question_types.csv")
    df_t2["cov_val"] = df_t2["Full Coverage %"].apply(lambda s: float(s.split("%")[0]))
    
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    
    methods = ["fixed_3", "fixed_5", "Score-Gap Adaptive-k Proxy"]
    labels = ["Fixed k=3", "Fixed k=5", "Score-Gap Adaptive-k Proxy"]
    x = np.arange(len(methods))
    width = 0.2
    
    bm25_bridge = df_t2[(df_t2["Retriever"] == "BM25") & (df_t2["Question Type"] == "bridge") & (df_t2["Method"].isin(methods))]["cov_val"].values
    bm25_comp = df_t2[(df_t2["Retriever"] == "BM25") & (df_t2["Question Type"] == "comparison") & (df_t2["Method"].isin(methods))]["cov_val"].values
    tfidf_bridge = df_t2[(df_t2["Retriever"] == "TF-IDF") & (df_t2["Question Type"] == "bridge") & (df_t2["Method"].isin(methods))]["cov_val"].values
    tfidf_comp = df_t2[(df_t2["Retriever"] == "TF-IDF") & (df_t2["Question Type"] == "comparison") & (df_t2["Method"].isin(methods))]["cov_val"].values
    
    ax.bar(x - 1.5*width, bm25_bridge, width, label="BM25 (Bridge)", color="#1f77b4", edgecolor="black")
    ax.bar(x - 0.5*width, bm25_comp, width, label="BM25 (Comparison)", color="#aec7e8", edgecolor="black")
    ax.bar(x + 0.5*width, tfidf_bridge, width, label="TF-IDF (Bridge)", color="#ff7f0e", edgecolor="black")
    ax.bar(x + 1.5*width, tfidf_comp, width, label="TF-IDF (Comparison)", color="#ffbb78", edgecolor="black")
    
    ax.set_ylabel("Full Coverage Rate (%)")
    ax.set_title("Full Evidence Coverage by Reasoning Type (Bridge vs. Comparison)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 85)
    ax.legend(loc="upper left", ncol=2)
    
    plt.tight_layout()
    plt.savefig("results/figures/figure2_question_types.png")
    plt.savefig("results/figures/figure2_question_types.pdf")
    plt.close()
    print("Saved Figure 2 (PNG and PDF).")


def make_figure3_failure_distribution():
    """
    Figure 3: Failure Mode Category Counts from the 40-case sample.
    """
    df_fail = pd.read_csv("results/tables/failure_sample.csv")
    counts = df_fail["predicted_category"].value_counts()
    
    pretty_names = {
        "bridge_entity_absent_from_query": "Bridge Entity Absent\nfrom Question",
        "flat_score_distribution_tie": "Flat Score Slope /\nRanking Tie",
        "distractor_lexical_overlap": "Topical Distractor\nLexical Overlap",
        "lexical_mismatch_synonymy": "Lexical Mismatch /\nSynonymy"
    }
    
    labels = [pretty_names.get(k, k) for k in counts.index]
    values = counts.values
    
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    bars = ax.barh(labels, values, color="#2ca02c", edgecolor="black", alpha=0.85)
    
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{int(w)} ({w/len(df_fail)*100:.1f}%)",
                    (w + 0.5, bar.get_y() + bar.get_height()/2),
                    va="center", fontsize=10)
        
    ax.set_xlabel("Number of Cases (N=40 Sample)")
    ax.set_title("Failure Mode Distribution in Missed Evidence\n(Score-Gap Adaptive-k Proxy / BM25)")
    ax.set_xlim(0, max(values) + 5)
    ax.invert_yaxis()  # Highest count on top
    
    plt.tight_layout()
    plt.savefig("results/figures/figure3_failure_distribution.png")
    plt.savefig("results/figures/figure3_failure_distribution.pdf")
    plt.close()
    print("Saved Figure 3 (PNG and PDF).")


def main():
    setup_style()
    os.makedirs(os.path.join("results", "figures"), exist_ok=True)
    make_figure1_pareto()
    make_figure2_question_types()
    make_figure3_failure_distribution()


if __name__ == "__main__":
    main()
