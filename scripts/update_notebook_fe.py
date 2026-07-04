"""Update notebook: remove phase labels and append feature engineering section."""

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


def main() -> None:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        src = src.replace(
            "**Phase 2:** Data loading, inspection, and exploratory data analysis.\n\n",
            "Reproduction and critical evaluation of Arcos-Argudo et al. (2025) on the NSL-KDD intrusion detection benchmark.\n\n",
        )
        src = src.replace(
            "(Phase 1 baseline)",
            "(author replication baseline)",
        )
        if src.startswith("## Phase 2 summary"):
            src = src.replace("## Phase 2 summary\n", "## Exploratory analysis — key takeaways\n")
            src = src.replace(
                "\n**Next (Phase 3):** leakage-aware preprocessing and feature engineering.\n",
                "",
            )
        cell["source"] = [line + "\n" for line in src.split("\n") if line or src.endswith("\n")]
        # fix trailing newline handling
        if cell["source"] and not cell["source"][-1].endswith("\n"):
            cell["source"][-1] += "\n"

    # Remove empty summary cell if it's redundant - keep key takeaways

    fe_cells = [
        md(
            """## 3. Feature engineering

We build two preprocessing variants:

1. **`train_only`** (recommended): one-hot categories and min–max scaling are fit on **training data only**; test rows are aligned to the train schema.
2. **`author_concat`**: matches the replication notebook (`concat(train, test)` before `get_dummies`) for metric comparison.

Additional steps informed by EDA:

- Drop `num_outbound_cmds` (constant zero).
- Drop one feature from each highly correlated numeric pair (|r| ≥ 0.95).
- Optional **SMOTE** on the training matrix only when training models."""
        ),
        code(
            """from src.preprocessing import (
    find_highly_correlated_numeric,
    leakage_checks,
    preprocess_nsl_kdd,
    split_features_and_labels,
)

FE_FIG_DIR = PROJECT_ROOT / 'results' / 'figures' / 'feature_engineering'
FE_FIG_DIR.mkdir(parents=True, exist_ok=True)

x_train_raw, x_test_raw, _, _ = split_features_and_labels(train_df, test_df)
corr_drop = find_highly_correlated_numeric(x_train_raw, threshold=0.95)
print('Features dropped for redundancy (|r|>=0.95):', corr_drop)
print('Leakage checks:', leakage_checks(x_train_raw, x_test_raw))"""
        ),
        md(
            """### 3.1 Encoding and scaling

| Step | Method | Rationale (cybersecurity) |
|------|--------|---------------------------|
| Constant drop | Remove `num_outbound_cmds` | Zero variance — no discriminative signal for attacks |
| Redundancy drop | Pearson |r| >= 0.95 on train | Error-rate features measure overlapping connection anomalies |
| Categorical encoding | One-hot (`protocol_type`, `service`, `flag`) | Attack patterns differ by protocol/service (DoS on HTTP, probe on TCP) |
| Scaling | Min–max to [0, 1], fit on train | Keeps comparable weight across byte counts and rates |
| Imbalance | SMOTE (optional, train only) | Increases minority attack exposure without contaminating test distribution |"""
        ),
        code(
            """variants = {}
for enc in ['train_only', 'author_concat']:
    for smote in [False, True]:
        key = f'{enc}_smote={smote}'
        variants[key] = preprocess_nsl_kdd(
            train_df,
            test_df,
            encoding=enc,
            drop_constants=True,
            drop_correlated=True,
            apply_smote=smote,
        )

summary_rows = []
for name, data in variants.items():
    summary_rows.append({
        'variant': name,
        'encoding': data.encoding,
        'smote': data.smote_applied,
        'n_features': len(data.feature_names),
        'train_shape': data.X_train.shape,
        'test_shape': data.X_test.shape,
        'dropped': data.dropped_features,
    })

fe_summary = pd.DataFrame(summary_rows)
display(fe_summary[['variant', 'n_features', 'train_shape', 'test_shape']])

# Default pipeline for downstream modeling
default_prep = variants['train_only_smote=False']
print('Default feature matrix:', default_prep.X_train.shape, default_prep.X_test.shape)"""
        ),
        md(
            """### 3.2 Author vs train-only encoding

The replication notebook encodes categories using **both** splits. That can introduce **schema leakage** (test-only categorical levels inform column space). Our `train_only` encoder prevents that; any unseen test category is ignored rather than expanding the feature space."""
        ),
        code(
            """compare = fe_summary[fe_summary['smote'] == False][['variant', 'n_features']]
display(compare)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(compare['variant'], compare['n_features'], color=['#4c78a8', '#f58518'])
ax.set_ylabel('Number of features after encoding')
ax.set_title('Feature dimensionality by encoding strategy')
plt.xticks(rotation=15, ha='right')
plt.tight_layout()
plt.savefig(FE_FIG_DIR / 'encoding_feature_counts.png', dpi=120)
plt.show()"""
        ),
        md(
            """### 3.3 Feature engineering conclusions

- Dropping correlated error-rate and host statistics reduces redundancy without removing protocol/service indicators.
- **Train-only encoding** is methodologically safer than concat-encoding for held-out evaluation.
- SMOTE resamples **only** `X_train` (125,973 → balanced majority/minority) and never touches `X_test`.
- These choices will be compared against the published results in the modeling section."""
        ),
    ]

    nb["cells"].extend(fe_cells)

    NOTEBOOK.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"Updated {NOTEBOOK} ({len(nb['cells'])} cells)")


if __name__ == "__main__":
    main()
