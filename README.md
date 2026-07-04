# Data Science in Cyber — Final Project

Critical reproduction and evaluation of an intrusion detection study on **NSL-KDD**.

| | |
|---|---|
| **Course** | Data Science in Cyber — Dr. Uri Itai |
| **Source paper** | [Arcos-Argudo et al. (2025), *Algorithms* 18, 749](https://doi.org/10.3390/a18120749) |
| **Original repo** | [miguelarcosa/IDS-KDD-CICIDS2017](https://github.com/miguelarcosa/IDS-KDD-CICIDS2017) |
| **Dataset** | [NSL-KDD](https://github.com/Jehuty4949/NSL_KDD) |
| **Deadline** | Friday, July 10, 2026, 23:59 |

## Project goal

Reproduce the authors' NSL-KDD binary intrusion detection pipeline, then **critically evaluate** whether their claims (AE+LR superiority, SMOTE effect, leakage-free preprocessing) are supported by independent evidence.

This is not a code-only rerun — deliverables include a Jupyter notebook, PDF report, and public GitHub repository per the course assignment.

## Repository layout

```
data-science-in-cyber/
├── README.md
├── prd.md / plan.md / todo.md    # project docs
├── requirements.txt
├── data/raw/                     # NSL-KDD files (not committed)
├── notebooks/                    # primary analysis notebook
├── src/                          # reusable Python modules
├── results/                      # metrics, figures (generated)
├── report/                       # final PDF report
├── docs/                         # reproducibility & critical eval notes
└── vendor/                       # upstream author repo (reference only)
```

## Quick start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd "data science in cyber"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows — activate before running scripts/notebooks:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

Scripts under `scripts/` will **auto-switch** to `.venv` if it exists, even when you run `python scripts/...` without activating.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the dataset

Place these files in `data/raw/`:

- `KDDTrain+.txt` (~125,973 records)
- `KDDTest+.txt` (~22,543 records)

Download from the [NSL-KDD GitHub mirror](https://github.com/Jehuty4949/NSL_KDD) or Kaggle. See `data/raw/README.md` for details.

### 5. Run the notebook

```bash
jupyter notebook notebooks/ids_nsl_kdd_analysis.ipynb
```

### 6. Reproduce author baseline (Phase 1)

```bash
python scripts/run_phase1_baseline.py
```

Outputs metrics to `results/baseline_reproduction.csv` (~6 min on CPU).

### 7. Run EDA (Phase 2) or open notebook

```bash
python scripts/run_phase2_eda.py
```

**Open the notebook** (must use project `.venv` — system `jupyter` often lacks Notebook):

```bash
.venv\Scripts\jupyter.exe notebook notebooks/ids_nsl_kdd_analysis.ipynb
```

Or double-click `scripts/run_notebook.bat`.

**Execute notebook end-to-end** (uses `ds-cyber` kernel; ~5 min on CPU plus AE training):

```bash
.venv\Scripts\jupyter-nbconvert.exe --to notebook --execute notebooks/ids_nsl_kdd_analysis.ipynb --output ids_nsl_kdd_analysis.ipynb --ExecutePreprocessor.timeout=1200 --ExecutePreprocessor.kernel_name=ds-cyber
```

### 8. Train models (standalone)

```bash
python scripts/run_phase4_training.py
```

Saves metrics to `results/model_training.csv`, baseline comparison to `results/baseline_comparison.csv`, and artifacts under `results/models/` (~5 min on CPU).

### 9. Evaluation and error analysis (standalone)

```bash
python scripts/run_phase5_eval.py
```

Writes `results/experiment_metrics.csv` and figures to `results/figures/eval/`.

In **Cursor/VS Code**: open `notebooks/ids_nsl_kdd_analysis.ipynb` and select kernel **Python (ds-cyber)**.

## Author replication (reference)

The upstream notebook for NSL-KDD is at:

`vendor/IDS-KDD-CICIDS2017/data/BACK-nsl-kdd-github.ipynb`

(The author README lists `notebooks/` but the file is under `data/`.)

Bundled preprocessed CSVs are also available in `vendor/IDS-KDD-CICIDS2017/data/`.

## Execution status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Foundation & environment | **Complete** |
| 1 | Author baseline reproduction | **Complete** |
| 2 | Data loading & EDA | **Complete** |
| 3 | Feature engineering | **Complete** |
| 4 | Model training | **Complete** |
| 5 | Evaluation & error analysis | **Complete** |
| 6 | Critical evaluation | Pending |
| 7 | Report & documentation | Pending |
| 8 | QA & submission | Pending |

Track granular tasks in [`todo.md`](./todo.md).

## Models evaluated

| Model | Source |
|-------|--------|
| Naïve Bayes | Paper reproduction |
| Logistic Regression | Paper + assignment |
| Linear Discriminant Analysis | Paper reproduction |
| Autoencoder + LR | Paper reproduction |
| Random Forest | Assignment extension |

## Key paper claims under test

1. AE+LR achieves highest AUC on NSL-KDD (~0.904)
2. SMOTE on train only yields modest F1 gains on NSL-KDD
3. Preprocessing is leakage-free (fit on train only)
4. NB has high precision but very low recall (~0.98 / ~0.24)
5. FAR must be reported alongside recall for operational IDS

## References

- Arcos-Argudo, M., Bojorque, R., & Torres, A. (2025). A Deterministic Comparison of Classical Machine Learning and Hybrid Deep Representation Models for Intrusion Detection on NSL-KDD and CICIDS2017. *Algorithms*, 18(12), 749. https://doi.org/10.3390/a18120749
- Canadian Institute for Cybersecurity. NSL-KDD Dataset. https://github.com/Jehuty4949/NSL_KDD

## License

Course assignment submission. Upstream datasets and author replication code retain their original licenses.
