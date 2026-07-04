"""Evaluation metrics, plots, and error analysis for IDS binary classification."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

METRIC_COLUMNS = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "mcc",
    "far",
    "auc",
    "tn",
    "fp",
    "fn",
    "tp",
]

METRIC_INTERPRETATIONS = {
    "accuracy": "Overall correct decisions; can be misleading when attacks are rare or uneven across types.",
    "precision": "Of flagged alerts, how many are real attacks — high precision reduces analyst fatigue (false alarms).",
    "recall": "Of true attacks, how many are detected — low recall means missed intrusions (false negatives).",
    "f1": "Harmonic mean of precision and recall; balances alert quality and detection coverage.",
    "mcc": "Correlation between predictions and truth; robust to class imbalance (range −1 to +1).",
    "far": "False Alarm Rate = FP/(FP+TN): fraction of benign traffic incorrectly flagged — operational cost in SOCs.",
    "auc": "Ranking quality across thresholds; insensitive to class balance but hides per-threshold FAR/recall trade-offs.",
}


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> dict[str, float | int]:
    """Return standard classification metrics including FAR and MCC."""
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    far = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    metrics: dict[str, float | int] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "far": float(far),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }
    if y_proba is not None:
        metrics["auc"] = float(roc_auc_score(y_true, y_proba))
    return metrics


def prediction_slug(model_name: str, smote: bool) -> str:
    smote_tag = "smote" if smote else "no_smote"
    return f"{model_name.replace('+', '_')}_{smote_tag}"


def load_predictions(path: Path | str) -> dict[str, np.ndarray]:
    data = np.load(path)
    return {
        "y_true": data["y_true"],
        "y_pred": data["y_pred"],
        "y_proba": data["y_proba"],
    }


def load_all_predictions(
    predictions_dir: Path,
    models: list[str],
    smote_flags: list[bool] | None = None,
) -> dict[tuple[str, bool], dict[str, np.ndarray]]:
    if smote_flags is None:
        smote_flags = [False, True]
    out: dict[tuple[str, bool], dict[str, np.ndarray]] = {}
    for model in models:
        for smote in smote_flags:
            path = predictions_dir / f"{prediction_slug(model, smote)}.npz"
            if path.exists():
                out[(model, smote)] = load_predictions(path)
    return out


def build_experiment_metrics(training_csv: Path | str) -> pd.DataFrame:
    """Normalize training results into the experiment metrics table."""
    df = pd.read_csv(training_csv)
    cols = [c for c in ["model", "smote", "encoding"] + METRIC_COLUMNS if c in df.columns]
    return df[cols].sort_values(["smote", "model"]).reset_index(drop=True)


def smote_delta_table(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """F1/recall/FAR change when SMOTE is enabled."""
    rows = []
    for model in sorted(metrics_df["model"].unique()):
        base = metrics_df[(metrics_df["model"] == model) & (~metrics_df["smote"])]
        smote = metrics_df[(metrics_df["model"] == model) & (metrics_df["smote"])]
        if base.empty or smote.empty:
            continue
        b, s = base.iloc[0], smote.iloc[0]
        rows.append(
            {
                "model": model,
                "delta_f1": round(s["f1"] - b["f1"], 4),
                "delta_recall": round(s["recall"] - b["recall"], 4),
                "delta_far": round(s["far"] - b["far"], 4),
                "delta_auc": round(s["auc"] - b["auc"], 4),
            }
        )
    return pd.DataFrame(rows)


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    title: str,
    output_path: Path | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=["Normal", "Attack"])
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title)
    if output_path is not None:
        if fig is None:
            fig = ax.figure
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(output_path, dpi=120)
        if fig is not None:
            plt.close(fig)
    return ax


def plot_roc_curves(
    predictions: dict[tuple[str, bool], dict[str, np.ndarray]],
    *,
    smote: bool = False,
    output_path: Path | None = None,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 6))
    for (model, smote_flag), preds in sorted(predictions.items()):
        if smote_flag != smote:
            continue
        fpr, tpr, _ = roc_curve(preds["y_true"], preds["y_proba"])
        auc = roc_auc_score(preds["y_true"], preds["y_proba"])
        ax.plot(fpr, tpr, label=f"{model} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("False Positive Rate (1 − specificity)")
    ax.set_ylabel("True Positive Rate (recall)")
    ax.set_title(f"ROC curves — {'with SMOTE' if smote else 'without SMOTE'}")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=120)
    return fig


def plot_metric_comparison(
    metrics_df: pd.DataFrame,
    metric: str,
    *,
    output_path: Path | None = None,
) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for ax, smote_flag, title in zip(axes, [False, True], ["Without SMOTE", "With SMOTE"]):
        subset = metrics_df[metrics_df["smote"] == smote_flag]
        ax.bar(subset["model"], subset[metric], color="#4c78a8")
        ax.set_title(title)
        ax.set_ylabel(metric.upper())
        ax.tick_params(axis="x", rotation=20)
    fig.suptitle(f"{metric.upper()} by model")
    fig.tight_layout()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=120)
    return fig


def threshold_sweep(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    """Precision/recall/FAR at multiple decision thresholds."""
    if thresholds is None:
        thresholds = np.linspace(0.05, 0.95, 19)
    rows = []
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        m = compute_metrics(y_true, y_pred)
        rows.append(
            {
                "threshold": round(float(t), 3),
                "precision": m["precision"],
                "recall": m["recall"],
                "f1": m["f1"],
                "far": m["far"],
            }
        )
    return pd.DataFrame(rows)


def plot_threshold_tradeoff(
    sweep_df: pd.DataFrame,
    *,
    title: str,
    output_path: Path | None = None,
) -> plt.Figure:
    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(sweep_df["threshold"], sweep_df["recall"], "o-", label="Recall (attack detection)")
    ax1.plot(sweep_df["threshold"], sweep_df["far"], "s-", label="FAR (false alarms)")
    ax1.set_xlabel("Decision threshold")
    ax1.set_ylabel("Rate")
    ax1.set_title(title)
    ax1.legend(loc="center right")
    ax1.grid(True, alpha=0.3)
    fig.tight_layout()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=120)
    return fig


def _attach_attack_metadata(test_df: pd.DataFrame) -> pd.DataFrame:
    from src.data_loading import attack_category

    meta = test_df[["label"]].copy()
    meta["label_binary"] = (meta["label"].str.lower() != "normal").astype(int)
    meta["attack_category"] = meta["label"].str.lower().map(attack_category)
    return meta


def error_by_attack_family(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
) -> pd.DataFrame:
    """Recall and miss rate per attack family (DoS, Probe, R2L, U2R)."""
    meta = _attach_attack_metadata(test_df)
    meta["y_pred"] = y_pred
    attack_rows = meta[meta["label_binary"] == 1].copy()
    rows = []
    for family in ["dos", "probe", "r2l", "u2r", "other"]:
        subset = attack_rows[attack_rows["attack_category"] == family]
        if subset.empty:
            continue
        detected = int((subset["y_pred"] == 1).sum())
        total = len(subset)
        rows.append(
            {
                "attack_family": family.upper(),
                "attacks_in_test": total,
                "detected": detected,
                "missed_fn": total - detected,
                "recall": round(detected / total, 4),
            }
        )
    return pd.DataFrame(rows)


def error_by_attack_label(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
    *,
    focus_families: tuple[str, ...] = ("r2l", "u2r"),
) -> pd.DataFrame:
    """Per-label detection for rare families (R2L/U2R emphasis)."""
    meta = _attach_attack_metadata(test_df)
    meta["y_pred"] = y_pred
    attack_rows = meta[meta["label_binary"] == 1].copy()
    attack_rows = attack_rows[attack_rows["attack_category"].isin(focus_families)]
    rows = []
    for label, group in attack_rows.groupby("label"):
        detected = int((group["y_pred"] == 1).sum())
        total = len(group)
        rows.append(
            {
                "label": label,
                "family": group["attack_category"].iloc[0].upper(),
                "count": total,
                "detected": detected,
                "missed": total - detected,
                "recall": round(detected / total, 4),
            }
        )
    return pd.DataFrame(rows).sort_values(["family", "recall"])


def false_positive_summary(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
) -> dict[str, int | float]:
    """Summarize benign traffic misclassified as attacks."""
    y_true = (test_df["label"].str.lower() != "normal").astype(int).to_numpy()
    fp_mask = (y_true == 0) & (y_pred == 1)
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(fp_mask.sum())
    return {
        "false_positives": fp,
        "true_negatives": tn,
        "far": round(fp / (fp + tn), 4) if (fp + tn) else 0.0,
    }


def compare_model_errors(
    test_df: pd.DataFrame,
    predictions: dict[tuple[str, bool], dict[str, np.ndarray]],
    *,
    smote: bool = False,
) -> pd.DataFrame:
    """Aggregate FN count and FP count per model."""
    rows = []
    for (model, smote_flag), preds in sorted(predictions.items()):
        if smote_flag != smote:
            continue
        y_true = preds["y_true"]
        y_pred = preds["y_pred"]
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        rows.append({"model": model, "false_positives": fp, "false_negatives": fn})
    return pd.DataFrame(rows)


def save_evaluation_artifacts(
    test_df: pd.DataFrame,
    predictions: dict[tuple[str, bool], dict[str, np.ndarray]],
    metrics_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Generate all evaluation CSVs and figures."""
    fig_dir = output_dir / "figures" / "eval"
    fig_dir.mkdir(parents=True, exist_ok=True)

    metrics_df.to_csv(output_dir / "experiment_metrics.csv", index=False)
    smote_delta_table(metrics_df).to_csv(output_dir / "smote_delta.csv", index=False)

    for metric in ("f1", "recall", "far", "auc"):
        plot_metric_comparison(
            metrics_df,
            metric,
            output_path=fig_dir / f"metric_{metric}.png",
        )
        plt.close()

    for smote in (False, True):
        plot_roc_curves(
            predictions,
            smote=smote,
            output_path=fig_dir / f"roc_{'smote' if smote else 'no_smote'}.png",
        )
        plt.close()

    focus_models = ["NB", "LR", "RF", "AE+LR"]
    for model in focus_models:
        key = (model, False)
        if key not in predictions:
            continue
        preds = predictions[key]
        plot_confusion_matrix(
            preds["y_true"],
            preds["y_pred"],
            title=f"{model} — no SMOTE",
            output_path=fig_dir / f"cm_{prediction_slug(model, False)}.png",
        )

        family_df = error_by_attack_family(test_df, preds["y_pred"])
        family_df.to_csv(output_dir / f"errors_by_family_{prediction_slug(model, False)}.csv", index=False)

        rare_df = error_by_attack_label(test_df, preds["y_pred"])
        rare_df.to_csv(output_dir / f"errors_rare_attacks_{prediction_slug(model, False)}.csv", index=False)

    lr_preds = predictions.get(("LR", False))
    if lr_preds is not None:
        sweep = threshold_sweep(lr_preds["y_true"], lr_preds["y_proba"])
        sweep.to_csv(output_dir / "threshold_sweep_LR_no_smote.csv", index=False)
        plot_threshold_tradeoff(
            sweep,
            title="LR threshold trade-off (no SMOTE)",
            output_path=fig_dir / "threshold_tradeoff_LR.png",
        )
        plt.close()

    compare_model_errors(test_df, predictions, smote=False).to_csv(
        output_dir / "model_error_counts_no_smote.csv",
        index=False,
    )
