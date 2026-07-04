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

Deliverables: Jupyter notebook (`notebooks/ids_nsl_kdd_analysis.ipynb`), PDF report (`report/final_project_report.pdf`), and this public repository.

## Repository layout

```
data-science-in-cyber/
├── README.md
├── prd.md / plan.md / todo.md
├── requirements.txt
├── data/raw/                     # NSL-KDD files (not committed)
├── notebooks/                    # primary analysis notebook
├── src/                          # reusable Python modules
├── results/                      # metrics, figures (generated)
├── report/                       # final PDF report
├── docs/                         # reproducibility & critical eval notes
└── vendor/                       # upstream author repo (reference only)
```

## Submission

| Item | Value |
|------|-------|
| **Repository** | https://github.com/JCS1029/Intrusion-Detection-NSL-KDD- |
| **Release tag** | `v1.0-submission` |
| **QA checklist** | [`docs/submission_checklist.md`](docs/submission_checklist.md) |
| **Deadline** | Friday, July 10, 2026, 23:59 |

Email the repository URL to the examiner per course instructions in `haifaUEX.pdf`.

## Quick start

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd "data science in cyber"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

Scripts under `scripts/` auto-switch to `.venv` when present.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the dataset

Place in `data/raw/`:

- `KDDTrain+.txt` (~125,973 records)
- `KDDTest+.txt` (~22,543 records)

Source: [NSL-KDD GitHub mirror](https://github.com/Jehuty4949/NSL_KDD). See `data/raw/README.md`.

### 5. Run the notebook (recommended)

```bash
.venv\Scripts\jupyter.exe notebook notebooks/ids_nsl_kdd_analysis.ipynb
```

**End-to-end execution** (~6–8 min CPU, includes AE+LR training):

```bash
.venv\Scripts\jupyter-nbconvert.exe --to notebook --execute notebooks/ids_nsl_kdd_analysis.ipynb --output ids_nsl_kdd_analysis.ipynb --ExecutePreprocessor.timeout=1200 --ExecutePreprocessor.kernel_name=ds-cyber
```

In Cursor/VS Code: open the notebook and select kernel **Python (ds-cyber)**.

### 6. Standalone scripts (optional)

| Script | Output | Runtime (CPU) |
|--------|--------|---------------|
| `python scripts/run_phase1_baseline.py` | `results/baseline_reproduction.csv` | ~6 min |
| `python scripts/run_phase2_eda.py` | `results/figures/eda/` | ~2 min |
| `python scripts/run_phase4_training.py` | `results/models/`, `results/model_training.csv` | ~5 min |
| `python scripts/run_phase5_eval.py` | `results/experiment_metrics.csv`, eval figures | ~1 min |
| `python scripts/run_phase7_report.py` | `report/final_project_report.pdf` | ~30 s |

## Report and documentation

| Artifact | Description |
|----------|-------------|
| [`report/final_project_report.pdf`](report/final_project_report.pdf) | Assignment PDF — executive summary, source summary, critical evaluation, feature engineering, reproducibility, results, conclusions |
| [`docs/critical_evaluation.md`](docs/critical_evaluation.md) | Claim matrix C1–C7 with verdicts and evidence |
| [`docs/reproducibility_notes.md`](docs/reproducibility_notes.md) | Environment, author baseline comparison, pipeline audits |

## Models evaluated

| Model | Source |
|-------|--------|
| Naïve Bayes | Paper reproduction |
| Logistic Regression | Paper + assignment |
| Linear Discriminant Analysis | Paper reproduction |
| Autoencoder + LR | Paper reproduction |
| Random Forest | Assignment extension |

## Oral defense cheat sheet

**One-liner:** We reproduced all author NSL-KDD metrics, then showed several headline claims fail under strict preprocessing or rare-attack scrutiny.

### Key numbers (our pipeline, no SMOTE)

| Model | F1 | AUC | FAR | Recall |
|-------|-----|-----|-----|--------|
| LDA | **0.752** | 0.860 | 6.9% | 0.63 |
| RF | 0.749 | **0.960** | 2.8% | 0.61 |
| AE+LR | 0.703 | 0.856 | 8.4% | 0.58 |
| LR | 0.716 | 0.843 | 7.5% | 0.59 |
| NB | 0.257 | 0.794 | **0.65%** | **0.15** |

### Claim verdicts (C1–C7)

| Claim | Verdict |
|-------|---------|
| C1 — AE+LR best AUC/F1 | **Partial** — true in author CSV pipeline (AUC 0.904); not in our train-only pipeline |
| C2 — SMOTE modest F1 gains | **Supported** — ΔF1 +0.003 to +0.031 |
| C3 — Leakage-free preprocessing | **Rejected (author)** — concat before one-hot; **Supported (ours)** |
| C4 — LR/LDA strong baselines | **Supported** — LDA within 0.002 F1 of AE+LR |
| C5 — NB high Prec, low Rec | **Supported** — Prec ~0.97, Rec ~0.15 |
| C6 — FAR essential | **Supported** — NB Acc 0.51 vs FAR 0.65% |
| C7 — Byte-level reproducibility | **Partial** — Table 4/5 matched; hidden CSV ETL |

### Likely examiner questions

1. **Why do your AE+LR numbers differ from the paper?** Different encoding (train-only 106 vs author concat 119 features), raw `.txt` vs bundled CSVs, seven correlated features dropped.
2. **Did you reproduce the authors?** Yes — all eight model/regime rows match Tables 4–5 within ±0.02 via `scripts/run_phase1_baseline.py`.
3. **Biggest weakness of the paper?** Binary collapse hides R2L/U2R failure (recall ~8–10%); legacy dataset; encoding leakage in author code.
4. **Would you deploy this?** No — use as benchmark only; report per-attack-family recall and tune thresholds operationally.

## Author replication (reference)

Upstream NSL-KDD notebook: `vendor/IDS-KDD-CICIDS2017/data/BACK-nsl-kdd-github.ipynb`  
(Author README incorrectly lists `notebooks/`.)

Bundled preprocessed CSVs: `vendor/IDS-KDD-CICIDS2017/data/KDDTrain_cleaned_binary.csv`.

## Project status

| Component | Status |
|-----------|--------|
| Environment & data | Complete |
| Author baseline reproduction | Complete |
| Notebook (EDA → critical eval) | Complete |
| PDF report | Complete |
| QA & submission | Complete |

Track tasks in [`todo.md`](./todo.md). Planning docs: [`prd.md`](./prd.md), [`plan.md`](./plan.md).

## References

- Arcos-Argudo, M., Bojorque, R., & Torres, A. (2025). A Deterministic Comparison of Classical Machine Learning and Hybrid Deep Representation Models for Intrusion Detection on NSL-KDD and CICIDS2017. *Algorithms*, 18(12), 749. https://doi.org/10.3390/a18120749
- NSL-KDD Dataset. https://github.com/Jehuty4949/NSL_KDD

## License

Course assignment submission. Upstream datasets and author replication code retain their original licenses.
