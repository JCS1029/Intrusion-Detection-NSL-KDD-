# Submission Checklist

Use this before the deadline (Friday, July 10, 2026, 23:59).

## Required deliverables

| Item | Location | Done? |
|------|----------|-------|
| Public GitHub repository | https://github.com/JCS1029/Intrusion-Detection-NSL-KDD- | ☐ |
| Jupyter notebook (runs top-to-bottom) | `notebooks/ids_nsl_kdd_analysis.ipynb` | ☐ |
| PDF report | `report/final_project_report.pdf` | ☐ |
| README with setup instructions | `README.md` | ☐ |
| Raw data instructions | `data/raw/README.md` | ☐ |

## Assignment criteria

| Criterion | Where to verify |
|-----------|-----------------|
| NSL-KDD LR reproduced (±0.02) or deviation explained | `results/baseline_reproduction.csv`, notebook §4 |
| ≥2 models with MCC and FAR | `results/experiment_metrics.csv` (5 models) |
| Report evaluates ≥5 author claims | Report §2, `docs/critical_evaluation.md` (7 claims) |
| SMOTE with/without comparison | Notebook §4–5 |
| Per-attack-type error analysis (R2L, U2R) | Notebook §6, `results/errors_rare_attacks_*.csv` |
| Feature redundancy analysis | Notebook §3, Report §3 |

## Before you submit

1. Download `KDDTrain+.txt` and `KDDTest+.txt` into `data/raw/` and run the notebook once from a clean kernel.
2. Confirm the repo is **public** and tag `v1.0-submission` exists.
3. Email the repository URL to the examiner per `haifaUEX.pdf`.
