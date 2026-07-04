"""
Phase 2: Generate EDA figures and summary tables for NSL-KDD.

Used by notebooks/ids_nsl_kdd_analysis.ipynb and run standalone.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Re-launch with project .venv if user runs system `python`
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "_venv_bootstrap", Path(__file__).resolve().parent / "_venv_bootstrap.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loading import (  # noqa: E402
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    add_binary_label,
    attack_category,
    find_constant_columns,
    find_duplicate_feature_columns,
    load_nsl_kdd,
    summarize_dataset,
)

FIG_DIR = PROJECT_ROOT / "results" / "figures" / "eda"
SUMMARY_DIR = PROJECT_ROOT / "results"


def _savefig(name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, dpi=120, bbox_inches="tight")
    plt.close()


def run_eda() -> dict:
    sns.set_theme(style="whitegrid")
    train_df, test_df = load_nsl_kdd()
    train_df = add_binary_label(train_df)
    test_df = add_binary_label(test_df)
    train_df["attack_category"] = train_df["label"].map(attack_category)
    test_df["attack_category"] = test_df["label"].map(attack_category)
    full_df = pd.concat([train_df.assign(split="train"), test_df.assign(split="test")], ignore_index=True)

    # --- Label distributions ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    binary_counts = full_df["label_binary"].value_counts().sort_index()
    axes[0].bar(["Normal (0)", "Attack (1)"], binary_counts.values, color=["#4c78a8", "#e45756"])
    axes[0].set_title("Binary label distribution (full dataset)")
    axes[0].set_ylabel("Count")

    cat_counts = full_df["attack_category"].value_counts()
    axes[1].barh(cat_counts.index, cat_counts.values, color="#72b7b2")
    axes[1].set_title("Attack category distribution")
    axes[1].set_xlabel("Count")
    _savefig("01_label_distribution.png")

    # --- Missing values ---
    missing = full_df.isna().sum()
    missing = missing[missing > 0]
    if len(missing):
        missing.plot(kind="barh", title="Missing values per column")
        _savefig("02_missing_values.png")
    else:
        pd.DataFrame({"note": ["No missing values detected"]}).to_csv(SUMMARY_DIR / "eda_missing.csv", index=False)

    # --- Numeric distributions (sample key features) ---
    key_numeric = ["duration", "src_bytes", "dst_bytes", "count", "srv_count", "serror_rate", "dst_host_count"]
    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    axes = axes.ravel()
    for ax, col in zip(axes, key_numeric):
        sns.histplot(data=full_df, x=col, hue="label_binary", bins=40, ax=ax, stat="density", common_norm=False)
        ax.set_title(col)
    for ax in axes[len(key_numeric) :]:
        ax.axis("off")
    _savefig("03_numeric_distributions.png")

    # --- Outliers (IQR) on train ---
    outlier_rows = []
    for col in NUMERIC_FEATURES:
        q1, q3 = train_df[col].quantile(0.25), train_df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n_out = int(((train_df[col] < lower) | (train_df[col] > upper)).sum())
        outlier_rows.append({"feature": col, "outliers_iqr": n_out, "pct": round(100 * n_out / len(train_df), 2)})
    outlier_df = pd.DataFrame(outlier_rows).sort_values("outliers_iqr", ascending=False)
    outlier_df.to_csv(SUMMARY_DIR / "eda_outliers_train.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    top = outlier_df.head(15)
    ax.barh(top["feature"], top["pct"], color="#f58518")
    ax.set_xlabel("% rows flagged as outliers (IQR rule)")
    ax.set_title("Top 15 features by outlier rate (train)")
    ax.invert_yaxis()
    _savefig("04_outlier_rates.png")

    # --- Crosstabs ---
    for cat in CATEGORICAL_FEATURES:
        ct = pd.crosstab(train_df[cat], train_df["label_binary"], normalize="index")
        ct.plot(kind="bar", stacked=True, figsize=(10, 4), colormap="coolwarm")
        plt.title(f"Attack rate by {cat} (train, row-normalized)")
        plt.ylabel("Proportion")
        plt.xlabel(cat)
        plt.legend(["Normal", "Attack"])
        _savefig(f"05_crosstab_{cat}_vs_binary.png")

    # --- Correlation (numeric only, train) ---
    num_train = train_df[NUMERIC_FEATURES + ["label_binary"]]
    pearson = num_train.corr(method="pearson")
    spearman = num_train.corr(method="spearman")

    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(pearson, cmap="RdBu_r", center=0, ax=ax, square=False)
    ax.set_title("Pearson correlation (numeric features + binary label, train)")
    _savefig("06_correlation_pearson.png")

    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(spearman, cmap="RdBu_r", center=0, ax=ax, square=False)
    ax.set_title("Spearman correlation (numeric features + binary label, train)")
    _savefig("07_correlation_spearman.png")

    # High Pearson pairs (redundancy)
    redundant = []
    cols = pearson.columns
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            r = pearson.loc[a, b]
            if abs(r) >= 0.9 and a != b:
                redundant.append({"feature_a": a, "feature_b": b, "pearson_r": round(r, 4)})
    pd.DataFrame(redundant).sort_values("pearson_r", key=abs, ascending=False).to_csv(
        SUMMARY_DIR / "eda_high_correlation_pairs.csv", index=False
    )

    # --- Class imbalance tables ---
    imb_train = train_df["label_binary"].value_counts(normalize=True).rename("proportion")
    imb_test = test_df["label_binary"].value_counts(normalize=True).rename("proportion")
    imb = pd.concat([imb_train, imb_test], axis=1, keys=["train", "test"])
    imb.to_csv(SUMMARY_DIR / "eda_class_balance.csv")

    subtype = train_df["attack_category"].value_counts(normalize=True).rename("train_proportion")
    subtype.to_csv(SUMMARY_DIR / "eda_attack_category_train.csv")

    fig, ax = plt.subplots(figsize=(8, 4))
    imb.plot(kind="bar", ax=ax, color=["#4c78a8", "#e45756"])
    ax.set_title("Class balance: Normal vs Attack")
    ax.set_ylabel("Proportion")
    ax.set_xticklabels(["Normal (0)", "Attack (1)"], rotation=0)
    _savefig("08_class_balance.png")

    # --- Constant / duplicate features ---
    constants = find_constant_columns(train_df.drop(columns=["label", "label_binary", "attack_category"], errors="ignore"))
    dup_pairs = find_duplicate_feature_columns(train_df)
    pd.DataFrame({"constant_columns": constants}).to_csv(SUMMARY_DIR / "eda_constant_columns.csv", index=False)
    pd.DataFrame(dup_pairs, columns=["col_a", "col_b"]).to_csv(SUMMARY_DIR / "eda_duplicate_columns.csv", index=False)

    summary = {
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "features": train_df.shape[1] - 3,  # exclude label, label_binary, attack_category
        "constant_columns": constants,
        "duplicate_pairs": len(dup_pairs),
        "attack_rate_train": float(train_df["label_binary"].mean()),
        "attack_rate_test": float(test_df["label_binary"].mean()),
    }
    pd.DataFrame([summary]).to_csv(SUMMARY_DIR / "eda_summary.csv", index=False)
    summarize_dataset(train_df, "train").to_csv(SUMMARY_DIR / "eda_split_summary.csv", index=False)
    pd.concat([summarize_dataset(train_df, "train"), summarize_dataset(test_df, "test")]).to_csv(
        SUMMARY_DIR / "eda_split_summary.csv", index=False
    )

    return summary


if __name__ == "__main__":
    s = run_eda()
    print("Phase 2 EDA complete.")
    for k, v in s.items():
        print(f"  {k}: {v}")
    print(f"Figures saved to {FIG_DIR}")
