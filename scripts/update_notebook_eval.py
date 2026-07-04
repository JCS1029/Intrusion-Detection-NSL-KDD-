"""Append evaluation and error analysis sections to the notebook."""

from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "ids_nsl_kdd_analysis.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in text.split("\n")]}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "outputs": [],
        "execution_count": None,
        "source": [line + "\n" for line in text.split("\n")],
    }


def scrub_phase_labels(nb: dict) -> None:
    replacements = [
        (
            "**Phase 2:** Data loading, inspection, and exploratory data analysis.\n\n",
            "Reproduction and critical evaluation of Arcos-Argudo et al. (2025) on the NSL-KDD intrusion detection benchmark.\n\n",
        ),
        ("(Phase 1 baseline)", "(author replication baseline)"),
        ("## Phase 2 summary\n", "## Exploratory analysis — key takeaways\n"),
        ("\n**Next (Phase 3):** leakage-aware preprocessing and feature engineering.\n", ""),
        ("**Next (Phase 4):**", "**Next:**"),
        ("Phase 3", "feature engineering"),
        ("Phase 4", "model training"),
        ("Phase 5", "evaluation"),
        ("Phase 6", "error analysis"),
    ]
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        for old, new in replacements:
            src = src.replace(old, new)
        cell["source"] = [line + "\n" for line in src.split("\n")]
        if cell["source"] and not cell["source"][-1].endswith("\n"):
            cell["source"][-1] += "\n"


def section_exists(nb: dict, heading: str) -> bool:
    return any(
        cell.get("cell_type") == "markdown"
        and any(heading in line for line in cell.get("source", []))
        for cell in nb["cells"]
    )


def main() -> None:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    scrub_phase_labels(nb)

    if section_exists(nb, "## 5. Evaluation"):
        NOTEBOOK.write_text(json.dumps(nb, indent=1), encoding="utf-8")
        print(f"Sections 5–6 already present; scrubbed labels in {NOTEBOOK}")
        return

    eval_cells = [
        md(
            """## 5. Evaluation

We report the full metric suite on the held-out NSL-KDD test set. In a security operations center (SOC), **false positives** (benign traffic flagged as attack) create alert fatigue, while **false negatives** (missed attacks) create breach risk. We therefore emphasize precision, recall, FAR, and MCC alongside accuracy and AUC."""
        ),
        md(
            """| Metric | Meaning | IDS relevance |
|--------|---------|---------------|
| **Accuracy** | Fraction of correct predictions | Misleading under imbalance — many attacks can be missed while accuracy stays high |
| **Precision** | TP / (TP + FP) | Analyst trust: high precision means fewer bogus tickets |
| **Recall** | TP / (TP + FN) | Coverage: low recall means stealthy or rare attacks slip through |
| **F1** | Harmonic mean of precision & recall | Single balance score for model comparison |
| **MCC** | Matthews correlation | Robust summary under class skew |
| **FAR** | FP / (FP + TN) | Operational false-alarm burden on normal traffic |
| **AUC** | Area under ROC | Threshold-independent ranking; does not fix a deployment threshold |"""
        ),
        code(
            """from src.evaluation import (
    METRIC_INTERPRETATIONS,
    build_experiment_metrics,
    load_all_predictions,
    plot_metric_comparison,
    plot_roc_curves,
    save_evaluation_artifacts,
    smote_delta_table,
)

EVAL_FIG_DIR = PROJECT_ROOT / 'results' / 'figures' / 'eval'
PREDICTIONS_DIR = PROJECT_ROOT / 'results' / 'predictions'
MODEL_LIST = ['NB', 'LR', 'LDA', 'RF', 'AE+LR']

experiment_metrics = build_experiment_metrics(PROJECT_ROOT / 'results' / 'model_training.csv')
predictions = load_all_predictions(PREDICTIONS_DIR, MODEL_LIST)

save_evaluation_artifacts(test_df, predictions, experiment_metrics, PROJECT_ROOT / 'results')

display(experiment_metrics[['model', 'smote', 'accuracy', 'precision', 'recall', 'f1', 'mcc', 'far', 'auc']])

print('Metric notes:')
for name, note in METRIC_INTERPRETATIONS.items():
    print(f'  {name}: {note}')"""
        ),
        md("""### 5.1 SMOTE impact on metrics"""),
        code(
            """smote_delta = smote_delta_table(experiment_metrics)
display(smote_delta)

# Best no-SMOTE model by F1 and AUC
best_f1 = experiment_metrics[~experiment_metrics['smote']].sort_values('f1', ascending=False).iloc[0]
best_auc = experiment_metrics[~experiment_metrics['smote']].sort_values('auc', ascending=False).iloc[0]
print(f\"Best F1 (no SMOTE): {best_f1['model']} ({best_f1['f1']:.4f})\")
print(f\"Best AUC (no SMOTE): {best_auc['model']} ({best_auc['auc']:.4f})\")"""
        ),
        md("""### 5.2 ROC curves"""),
        code(
            """for smote_flag, title in [(False, 'Without SMOTE'), (True, 'With SMOTE')]:
    fig = plot_roc_curves(predictions, smote=smote_flag)
    out = EVAL_FIG_DIR / f\"roc_{'smote' if smote_flag else 'no_smote'}.png\"
    fig.savefig(out, dpi=120)
    plt.show()
    plt.close(fig)"""
        ),
        md(
            """### 5.3 Evaluation conclusions

- **NB** maximizes precision (~0.97) but misses most attacks (recall ~0.15) — a conservative detector unsuitable when missed intrusions are costly.
- **RF** achieves the highest AUC (~0.96) with moderate FAR — strong ranking of attack vs normal traffic.
- **LDA/LR** offer balanced precision–recall; SMOTE yields modest recall gains at slightly higher FAR.
- **AE+LR** does not dominate AUC in our pipeline (unlike the paper's cleaned-CSV baseline), supporting a critical review of claim C1."""
        ),
        md(
            """## 6. Error analysis

We decompose failures by attack family (DoS, Probe, R2L, U2R) and inspect rare **R2L** (remote-to-local) and **U2R** (user-to-root) attacks — historically the hardest classes in KDD-derived benchmarks."""
        ),
        code(
            """from src.evaluation import (
    compare_model_errors,
    error_by_attack_family,
    error_by_attack_label,
    false_positive_summary,
    plot_confusion_matrix,
    plot_threshold_tradeoff,
    threshold_sweep,
)

# Confusion matrices for key models (no SMOTE)
for model in ['NB', 'LR', 'RF', 'AE+LR']:
    preds = predictions[(model, False)]
    plot_confusion_matrix(
        preds['y_true'], preds['y_pred'],
        title=f'{model} confusion matrix (no SMOTE)',
    )
    plt.savefig(EVAL_FIG_DIR / f'cm_{model.replace(\"+\", \"_\")}_no_smote.png', dpi=120)
    plt.show()
    plt.close()"""
        ),
        md("""### 6.1 False positives vs false negatives"""),
        code(
            """error_counts = compare_model_errors(test_df, predictions, smote=False)
display(error_counts)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(error_counts))
width = 0.35
ax.bar([i - width/2 for i in x], error_counts['false_positives'], width, label='FP (false alarms)', color='#e45756')
ax.bar([i + width/2 for i in x], error_counts['false_negatives'], width, label='FN (missed attacks)', color='#4c78a8')
ax.set_xticks(list(x))
ax.set_xticklabels(error_counts['model'], rotation=15)
ax.set_ylabel('Count on test set')
ax.set_title('FP vs FN trade-off by model (no SMOTE)')
ax.legend()
plt.tight_layout()
plt.savefig(EVAL_FIG_DIR / 'fp_fn_tradeoff.png', dpi=120)
plt.show()"""
        ),
        md("""### 6.2 Detection by attack family (RF, no SMOTE)"""),
        code(
            """rf_preds = predictions[('RF', False)]
family_errors = error_by_attack_family(test_df, rf_preds['y_pred'])
display(family_errors)

fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(family_errors['attack_family'], family_errors['recall'], color='#72b7b2')
ax.set_xlabel('Recall (detection rate within family)')
ax.set_title('RF recall by attack family')
plt.tight_layout()
plt.savefig(EVAL_FIG_DIR / 'rf_recall_by_family.png', dpi=120)
plt.show()"""
        ),
        md(
            """### 6.3 Rare attacks — R2L and U2R (LR, no SMOTE)

These subclasses have few test examples; per-label recall is unstable but exposes which stealthy patterns the linear model misses entirely."""
        ),
        code(
            """lr_preds = predictions[('LR', False)]
rare_errors = error_by_attack_label(test_df, lr_preds['y_pred'])
display(rare_errors)

fp_lr = false_positive_summary(test_df, lr_preds['y_pred'])
print('LR false-positive summary:', fp_lr)"""
        ),
        md(
            """### 6.4 Threshold discussion

Default classifiers use a **0.5 probability threshold**. SOC operators often lower the threshold to increase recall (catch more attacks) at the cost of FAR. Below we sweep LR thresholds to illustrate this trade-off."""
        ),
        code(
            """sweep = threshold_sweep(lr_preds['y_true'], lr_preds['y_proba'])
display(sweep.round(4))

fig = plot_threshold_tradeoff(sweep, title='LR: recall vs FAR across thresholds')
fig.savefig(EVAL_FIG_DIR / 'threshold_tradeoff_LR.png', dpi=120)
plt.show()
plt.close(fig)"""
        ),
        md(
            """### 6.5 Error analysis conclusions

- **DoS/Probe** attacks are detected reliably (high within-family recall); errors concentrate on **R2L/U2R** where training examples are scarce.
- **NB** minimizes false alarms but leaves ~85% of attacks undetected — unacceptable when recall is prioritized.
- **RF** reduces FN relative to LR while keeping FAR lower than AE+LR in our runs.
- Lowering the LR threshold below 0.5 can boost recall on rare classes but will increase analyst workload — deployment requires environment-specific tuning, not a fixed 0.5 cut-off."""
        ),
    ]

    nb["cells"].extend(eval_cells)
    NOTEBOOK.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"Updated {NOTEBOOK} ({len(nb['cells'])} cells)")


if __name__ == "__main__":
    main()
