# Reproducibility Notes

Log of environment setup, author baseline runs, and pipeline audits.

## Environment setup (2026-07-04)

### Host

| Item | Value |
|------|-------|
| OS | Windows 10 (build 19045) |
| Python | 3.12.10 |
| Project venv | `.venv/` |

### Key package versions (our environment)

| Package | Version |
|---------|---------|
| pandas | 2.3.3 |
| numpy | 2.5.0 |
| scikit-learn | 1.9.0 |
| imbalanced-learn | 0.14.2 |
| tensorflow | 2.21.0 |
| matplotlib | 3.11.0 |
| seaborn | 0.13.2 |

**Note:** Paper reports Python 3.12.11, TensorFlow 2.20.0, scikit-learn 1.7.2. Minor version drift may affect AE+LR metrics slightly — see author baseline comparison below.

### Author replication repo

| Item | Value |
|------|-------|
| URL | https://github.com/miguelarcosa/IDS-KDD-CICIDS2017 |
| Local path | `vendor/IDS-KDD-CICIDS2017/` |
| Commit | `dc8c7872f967bae031dddb747be425721d38c8a7` |
| NSL-KDD notebook | `vendor/IDS-KDD-CICIDS2017/data/BACK-nsl-kdd-github.ipynb` |
| Preprocessed CSVs (bundled) | `KDDTrain_cleaned_binary.csv`, `KDDTest_cleaned_binary.csv` |
| Author env file | `environment.yml` (Conda env `IDSTesis01`) |

**README discrepancy:** Author README references `notebooks/BACK-nsl-kdd-github.ipynb` but the file lives under `data/`.

### NSL-KDD raw data

| File | Rows | Size |
|------|------|------|
| `data/raw/KDDTrain+.txt` | 125,973 | ~18.2 MB |
| `data/raw/KDDTest+.txt` | 22,544 | ~3.3 MB |

Source: https://github.com/Jehuty4949/NSL_KDD

---

## Author baseline reproduction (2026-07-04)

### Execution approach

| Item | Value |
|------|-------|
| Implementation | Notebook §4 + logic mirrored from `vendor/.../data/BACK-nsl-kdd-github.ipynb` |
| Environment | Project `.venv/` (not author Conda env) |
| Data used | Author bundled CSVs (not raw `.txt`) |

### Preprocessing checklist (as implemented in author notebook)

1. Load `KDDTrain_cleaned_binary.csv` / `KDDTest_cleaned_binary.csv`
2. Split features (`iloc[:, :-1]`) and binary label (`iloc[:, -1]`)
3. **One-hot encode:** `pd.concat([X_train, X_test])` → `pd.get_dummies(drop_first=True)` → split back
4. **Min–max scale:** `MinMaxScaler.fit` on train, `transform` on test
5. **SMOTE (optional):** `SMOTE(random_state=42)` on train only (or on AE embeddings for AE+LR)
6. Train classifier; evaluate on held-out test; threshold 0.5

### Model hyperparameters (paper Table 3 / notebook)

| Model | Configuration |
|-------|---------------|
| NB | `GaussianNB()`, defaults |
| LR | `LogisticRegression(random_state=42, max_iter=1000)` |
| LDA | `LinearDiscriminantAnalysis()`, defaults |
| AE | Dense(64)→Dense(32)→Dense(64)→sigmoid; MSE; Adam 1e-3; 20 epochs; batch 256; shuffle=False |
| AE+LR | LR on 32-dim embeddings; SMOTE on embeddings when enabled |

### Data shape notes

| Source | Train rows | Test rows | Feature dim (after encoding) |
|--------|------------|-----------|------------------------------|
| Raw `.txt` | 125,973 | 22,544 | — |
| Author cleaned CSV | 125,972 | 22,542 | 119 |

One row dropped per split during author preprocessing (not documented in paper).

### Results vs paper

**Verdict: reproduction succeeded.** All models **MATCH** (max metric delta ≤ 0.02).

| Model | SMOTE | Max Δ vs paper | Status |
|-------|-------|----------------|--------|
| NB | No | 0.0000 | MATCH |
| LR | No | 0.0000 | MATCH |
| LDA | No | 0.0000 | MATCH |
| AE+LR | No | 0.0002 | MATCH |
| NB | Yes | 0.0000 | MATCH |
| LR | Yes | 0.0013 | MATCH |
| LDA | Yes | 0.0000 | MATCH |
| AE+LR | Yes | 0.0004 | MATCH |

Full metrics: `results/baseline_reproduction.csv`

#### No SMOTE — our run vs paper Table 4

| Model | Metric | Ours | Paper | Δ |
|-------|--------|------|-------|---|
| LR | F1 | 0.7302 | 0.7302 | 0.0000 |
| LR | AUC | 0.8276 | 0.8276 | 0.0000 |
| AE+LR | F1 | 0.7533 | 0.7534 | 0.0001 |
| AE+LR | AUC | 0.9040 | 0.9040 | 0.0000 |

#### With SMOTE — our run vs paper Table 5

| Model | Metric | Ours | Paper | Δ |
|-------|--------|------|-------|---|
| LR | Accuracy | 0.7465 | 0.7458 | 0.0007 |
| LR | F1 | 0.7333 | 0.7324 | 0.0009 |
| AE+LR | F1 | 0.7586 | 0.7583 | 0.0003 |

### Training times (our run, seconds)

| Model | No SMOTE (train) | With SMOTE (train) |
|-------|------------------|---------------------|
| NB | 0.47 | 0.43 |
| LR | 4.17 | 3.57 |
| LDA | 5.57 | 5.28 |
| AE+LR | 63.1 | 81.9 |

### Reproducibility audit — findings for critical evaluation

1. **Hidden preprocessing:** Notebook uses pre-cleaned binary CSVs. Raw `KDDTrain+.txt` / `KDDTest+.txt` are never loaded. The cleaning script is not in the repo — full reproduction from raw data is not possible without reverse-engineering.

2. **One-hot encoding leakage risk:** `pd.concat([train, test])` before `get_dummies` means test-set categorical levels inform the encoding schema. Paper claims leakage-free preprocessing fit on train only; this step is a methodological tension worth discussing.

3. **No saved `predict_proba` artifacts:** Models are retrained in notebook cells; metrics are computed live (supports claim C7 partially — code reproduces, but not byte-identical without same library versions).

4. **SMOTE parameters:** Notebook uses `SMOTE(random_state=42)` defaults (`k_neighbors=5`, `sampling_strategy='auto'`) — consistent with paper.

5. **No median imputation on NSL-KDD:** Paper Section 3.2 imputation applies to CICIDS2017 only; correctly absent here.

6. **Windows / TensorFlow:** Ran on CPU (Windows native TF ≥2.11). Minor AE+LR floating-point differences vs paper (F1 ±0.0003) likely from TF 2.21 vs 2.20 and oneDNN ops.

7. **Author README error:** Notebook path documented incorrectly (`notebooks/` vs `data/`).

### Our preprocessing pipeline (`src/preprocessing.py`)

| Step | `train_only` (default) | `author_concat` |
|------|------------------------|-------------------|
| Constant drop | `num_outbound_cmds` | same |
| Correlation drop | \|r\| ≥ 0.95 pairs on train numerics | same |
| One-hot | Fit schema on train; align test | Concat train+test (author style) |
| Scaling | MinMaxScaler fit on train | same |
| SMOTE | Optional, train only | same |

**Feature counts after encoding (no SMOTE):**

| Variant | Features |
|---------|----------|
| `train_only` | 106 |
| `author_concat` | 119 |

Redundant numeric features removed (train-only Pearson):  
`dst_host_rerror_rate`, `dst_host_srv_rerror_rate`, `dst_host_srv_serror_rate`, `num_root`, `rerror_rate`, `srv_rerror_rate`, `srv_serror_rate`

### Author baseline conclusion

**Reproduction succeeded.** All eight model/regime combinations match paper Tables 4–5 within tolerance. The replication package is functional when using bundled CSVs and mirroring notebook logic. The main reproducibility gaps are undocumented CSV preprocessing and the train+test concat before one-hot encoding.

### Our model training (`src/models.py`)

| Setting | Value |
|---------|-------|
| Encoding | `train_only` (default) |
| Models | NB, LR, LDA, RF (`n_estimators=100`), AE+LR |
| SMOTE | Optional on train matrix only |
| `random_state` | 42 |
| Outputs | `results/model_training.csv`, `results/baseline_comparison.csv`, `results/models/`, `results/predictions/` |

**Best F1 (no SMOTE):** LDA 0.7517, RF 0.7491. **Best AUC:** RF 0.9597.

**Vs author baseline:** LR and LDA within ±0.02; NB and AE+LR diverge (expected — different encoding/feature set and raw vs cleaned CSVs). RF has no author baseline (our extension).

### Evaluation summary

| Finding | Detail |
|---------|--------|
| Best AUC (no SMOTE) | RF 0.9597 |
| Best F1 (no SMOTE) | LDA 0.7517 |
| SMOTE effect | Modest F1/recall gains; largest on RF (+0.013 F1) and AE+LR (+0.031 F1) |
| Hardest families | R2L recall ~8% (RF), U2R ~10% — rare-class problem persists |
| NB trade-off | FAR 0.65% but recall 15% — extreme precision-over-recall bias |

Artifacts: `results/experiment_metrics.csv`, `results/figures/eval/`, per-family error CSVs.

### Critical evaluation

Claim verdicts C1–C7 documented in `docs/critical_evaluation.md`. Notebook §7 and executive summary synthesize findings for the report.
