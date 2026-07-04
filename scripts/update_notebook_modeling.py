"""Scrub phase labels from notebook and append model training section."""

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


def section_exists(nb: dict) -> bool:
    return any(
        cell.get("cell_type") == "markdown"
        and any("## 4. Model training" in line for line in cell.get("source", []))
        for cell in nb["cells"]
    )


def main() -> None:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    scrub_phase_labels(nb)

    if section_exists(nb):
        NOTEBOOK.write_text(json.dumps(nb, indent=1), encoding="utf-8")
        print(f"Notebook already has section 4; scrubbed phase labels in {NOTEBOOK}")
        return

    modeling_cells = [
        md(
            """## 4. Model training

We train five classifiers on the **train-only** preprocessing pipeline (`default_prep` without SMOTE, and a SMOTE-resampled training set):

| Model | Role |
|-------|------|
| Naïve Bayes (NB) | Paper baseline — fast generative model |
| Logistic Regression (LR) | Paper baseline — linear decision boundary |
| Linear Discriminant Analysis (LDA) | Paper baseline — class-separating projection |
| Random Forest (RF) | Assignment extension beyond the paper |
| Autoencoder + LR (AE+LR) | Paper hybrid — nonlinear embeddings + linear classifier |

Hyperparameters follow Arcos-Argudo et al. (2025) where applicable (`random_state=42`, LR `max_iter=1000`, AE 20 epochs). SMOTE is applied to **training data only** when enabled."""
        ),
        code(
            """from src.models import (
    compare_to_baseline,
    save_comparison,
    save_training_log,
    train_all_models,
)

MODELS_DIR = PROJECT_ROOT / 'results' / 'models'
PREDICTIONS_DIR = PROJECT_ROOT / 'results' / 'predictions'
BASELINE_CSV = PROJECT_ROOT / 'results' / 'baseline_reproduction.csv'

training_results = []
baseline_checks = []

for smote in [False, True]:
    prep = variants[f'train_only_smote={smote}']
    print(f\"\\nTraining suite — SMOTE={smote}, features={prep.X_train.shape[1]}\")
    batch = train_all_models(
        prep,
        save_dir=MODELS_DIR,
        predictions_dir=PREDICTIONS_DIR,
        include_rf=True,
    )
    training_results.extend(batch)
    baseline_checks.extend(compare_to_baseline(batch, BASELINE_CSV))

training_df = save_training_log(training_results, PROJECT_ROOT / 'results' / 'model_training.csv')
comparison_df = save_comparison(baseline_checks, PROJECT_ROOT / 'results' / 'baseline_comparison.csv')

display(training_df[['model', 'smote', 'accuracy', 'precision', 'recall', 'f1', 'auc', 'far', 'train_seconds']])"""
        ),
        md(
            """### 4.1 Training times and saved artifacts

Models are persisted under `results/models/`; test-set predictions (`y_pred`, `y_proba`) are saved to `results/predictions/` for downstream error analysis."""
        ),
        code(
            """timing = training_df.pivot_table(
    index='model',
    columns='smote',
    values='train_seconds',
    aggfunc='first',
)
timing.columns = ['no_smote_sec', 'smote_sec']
display(timing.sort_index())

print('Saved models:', len(list(MODELS_DIR.glob('*'))), 'entries under', MODELS_DIR)"""
        ),
        md(
            """### 4.2 Comparison with author replication baseline

The author baseline (`results/baseline_reproduction.csv`) uses **pre-cleaned CSVs** and **concat(train, test)** one-hot encoding. Our pipeline uses raw NSL-KDD, drops redundant features, and encodes categories on train only — so some divergence is expected and methodologically justified."""
        ),
        code(
            """display(comparison_df[['model', 'smote', 'max_delta_vs_author', 'status', 'note']])

import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
for ax, smote_flag, title in zip(
    axes,
    [False, True],
    ['Without SMOTE', 'With SMOTE (train only)'],
):
    subset = training_df[training_df['smote'] == smote_flag]
    ax.bar(subset['model'], subset['f1'], color='#4c78a8')
    ax.set_title(f'F1 by model — {title}')
    ax.set_ylabel('F1 score')
    ax.tick_params(axis='x', rotation=20)
plt.tight_layout()
plt.savefig(PROJECT_ROOT / 'results' / 'figures' / 'model_training_f1.png', dpi=120)
plt.show()"""
        ),
        md(
            """### 4.3 Modeling conclusions

- **RF** adds a nonlinear ensemble benchmark not evaluated in the paper; compare its recall/FAR trade-off in the evaluation section.
- **SMOTE** generally lifts recall on attacks at the cost of more false alarms — inspect per-model shifts above.
- Divergence from the author baseline reflects preprocessing differences (encoding + redundancy removal), not necessarily model bugs.
- Full metric interpretation, ROC curves, and attack-subtype error analysis follow in the next section."""
        ),
    ]

    nb["cells"].extend(modeling_cells)
    NOTEBOOK.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"Updated {NOTEBOOK} ({len(nb['cells'])} cells)")


if __name__ == "__main__":
    main()
