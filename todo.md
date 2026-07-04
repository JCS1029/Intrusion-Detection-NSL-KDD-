# TODO — IDS NSL-KDD Reproduction Project

**Companion docs:** [`prd.md`](./prd.md) · [`plan.md`](./plan.md)  
**Deadline:** Friday, July 10, 2026, 23:59  
**Legend:** `[ ]` pending · `[x]` done · `[-]` skipped/blocked

---

## Progress summary

| Phase | Name | Status |
|-------|------|--------|
| 0 | Foundation & Environment | `[x]` |
| 1 | Author Baseline Reproduction | `[x]` |
| 2 | Data Loading & EDA | `[x]` |
| 3 | Feature Engineering | `[x]` |
| 4 | Model Training | `[x]` |
| 5 | Evaluation & Error Analysis | `[x]` |
| 6 | Critical Evaluation Synthesis | `[x]` |
| 7 | Report & Documentation | `[x]` |
| 8 | Final QA & Submission | `[x]` |

---

## Phase 0 — Foundation & Environment

**Target:** Jul 4 · **Exit:** Environment installs; data verified; repo tree matches PRD

- [x] Initialize Git repository in project root
- [x] Create directory structure (`data/raw/`, `notebooks/`, `src/`, `results/figures/`, `report/`, `docs/`, `vendor/`)
- [x] Write `requirements.txt` with pinned dependencies
- [x] Write `.gitignore` (data, venv, checkpoints, large model artifacts)
- [x] Clone author repo to `vendor/IDS-KDD-CICIDS2017/`
- [x] Download NSL-KDD `KDDTrain+.txt` and `KDDTest+.txt` into `data/raw/`
- [x] Verify train row count (~125,973) and test row count (~22,544 — +1 vs paper, likely blank line)
- [x] Scaffold empty `src/` modules (`data_loading.py`, `preprocessing.py`, `models.py`, `evaluation.py`)
- [x] Draft initial `README.md` skeleton
- [x] Create virtual environment and confirm dependencies install (core + TensorFlow separately)

---

## Phase 1 — Author Baseline Reproduction

**Target:** Jul 4 · **Exit:** LR within ±0.02 of paper Table 4 (or deviation documented); ≥1 additional model attempted

> Phase 1 is intentionally granular. Complete tasks in order unless a blocker forces a documented workaround.

### 1.1 Repository orientation

- [x] Open `vendor/IDS-KDD-CICIDS2017/` and list top-level files and folders
- [x] Read author `README.md` (or equivalent) end-to-end
- [x] Identify whether project uses scripts, notebooks, Makefile, or config-driven runner
- [x] Locate dependency file (`requirements.txt`, `environment.yml`, `pyproject.toml`)
- [x] Locate config files (`configs/`, `*.yaml`, `*.json`, `.env` examples) — none; notebook-only
- [x] Locate NSL-KDD-specific code paths (grep/search: `NSL`, `KDD`, `nsl_kdd`)
- [x] Locate CICIDS2017-specific code paths (confirm we will **not** run these in this phase)
- [x] Identify where final metrics are printed or saved (CSV, JSON, logs, tables) — stdout in notebook cells
- [x] Identify where trained models / `predict_proba` scores are stored (if pre-computed) — not stored; retrained each cell
- [x] Record repo commit hash in `docs/reproducibility_notes.md`

### 1.2 Paper-to-code mapping

- [x] Open paper Section 3 (Methodology) alongside the repo
- [x] Confirm binary task definition: Normal vs Attack (not multiclass)
- [x] Confirm split policy: official `KDDTrain+` / `KDDTest+` (no random reshuffle)
- [x] Locate code that loads `KDDTrain+.txt` and `KDDTest+.txt` — **not used**; uses cleaned CSVs instead
- [x] Locate code for one-hot encoding of `protocol_type`, `service`, `flag`
- [x] Locate code for min–max scaling to [0, 1]
- [x] Locate code for median imputation (expected for CICIDS2017; note if used on NSL-KDD) — not on NSL-KDD
- [x] Locate SMOTE usage and verify it is **train-only** (not applied to test)
- [x] Locate model definitions for NB, LR, LDA, AE+LR
- [x] Locate fixed seed / deterministic TensorFlow settings (`random_state=42`, TF seeds)
- [x] Write a preprocessing checklist in `docs/reproducibility_notes.md` (ordered steps)
- [x] Write a model hyperparameter checklist matching paper Table 3

### 1.3 Environment setup (author pipeline)

- [x] Check Python version required by author repo — Python 3.12.11 in environment.yml
- [x] Decide execution context: project venv vs author-repo venv (document choice) — **project `.venv`**
- [x] Install author repo dependencies (or map overlap with our `requirements.txt`)
- [x] Install TensorFlow if required for AE+LR
- [x] Install `imbalanced-learn` if SMOTE is used
- [x] Run a minimal import test (`sklearn`, `tensorflow`, `imblearn`, `pandas`, `numpy`)
- [x] Record exact package versions (`pip freeze`) in `docs/reproducibility_notes.md`
- [x] Record OS, Python version, and CPU/GPU context in `docs/reproducibility_notes.md`

### 1.4 Data path configuration

- [x] Determine expected path/filename for NSL-KDD train file in author repo — `KDDTrain_cleaned_binary.csv`
- [x] Determine expected path/filename for NSL-KDD test file in author repo — `KDDTest_cleaned_binary.csv`
- [x] Copy or symlink `data/raw/KDDTrain+.txt` to author-expected location (or update config) — N/A; author uses CSVs
- [x] Copy or symlink `data/raw/KDDTest+.txt` to author-expected location (or update config) — N/A
- [x] Confirm author loader reads correct number of columns (41 features + label + difficulty) — 119 encoded features after cleaning
- [x] Confirm how author handles `difficulty` column (drop vs keep) — dropped in cleaned CSV
- [x] Confirm how author maps labels to binary (0/1) for Normal vs Attack — pre-mapped in CSV
- [x] Run data-load-only step (if available) and verify train/test shapes match paper — 125,972 / 22,542

### 1.5 Run — NSL-KDD without SMOTE

- [x] Identify exact command/notebook/cell to run NSL-KDD **without SMOTE** — `scripts/run_phase1_baseline.py`
- [x] Set dataset flag to NSL-KDD only (disable CICIDS2017 if config exists)
- [x] Set SMOTE flag to **off** / `use_smote=False` (or equivalent)
- [x] Confirm `random_state=42` (or paper seed) in config before running
- [x] Run pipeline for **Naïve Bayes** — capture stdout/logs
- [x] Record NB metrics: Accuracy, Precision, Recall, F1, FAR, AUC
- [x] Run pipeline for **Logistic Regression** — capture stdout/logs
- [x] Record LR metrics: Accuracy, Precision, Recall, F1, FAR, AUC
- [x] Run pipeline for **LDA** — capture stdout/logs
- [x] Record LDA metrics: Accuracy, Precision, Recall, F1, FAR, AUC
- [x] Run pipeline for **AE+LR** — capture stdout/logs
- [x] Record AE+LR metrics: Accuracy, Precision, Recall, F1, FAR, AUC
- [ ] Save confusion matrices (if emitted) to `results/figures/baseline/no_smote/` — deferred (metrics in CSV)
- [ ] Save ROC data or plots (if emitted) to `results/figures/baseline/no_smote/` — deferred to Phase 5
- [x] Record wall-clock training and inference times per model (if available)

### 1.6 Run — NSL-KDD with SMOTE (train only)

- [x] Identify exact command/notebook/cell to run NSL-KDD **with SMOTE**
- [x] Set SMOTE flag to **on** / `use_smote=True`
- [x] Verify in code/logs that SMOTE applies to **training data only**
- [x] Confirm SMOTE params: `random_state=42`, `k_neighbors=5`, `sampling_strategy='auto'`
- [x] Run pipeline for **Naïve Bayes** (with SMOTE) — record all metrics
- [x] Run pipeline for **Logistic Regression** (with SMOTE) — record all metrics
- [x] Run pipeline for **LDA** (with SMOTE) — record all metrics
- [x] Run pipeline for **AE+LR** (with SMOTE) — record all metrics
- [ ] Save confusion matrices to `results/figures/baseline/with_smote/` — deferred
- [x] Record wall-clock training times (expect increase vs no-SMOTE)

### 1.7 Aggregate and compare results

- [x] Create `results/baseline_reproduction.csv` with columns: `dataset`, `model`, `smote`, `accuracy`, `precision`, `recall`, `f1`, `far`, `auc`, `notes`
- [x] Add paper Table 4 targets as reference rows (no SMOTE)
- [x] Add paper Table 5 targets as reference rows (with SMOTE)
- [x] Compute absolute delta per metric: `|ours - paper|`
- [x] Flag any metric with delta > 0.02 for investigation — none flagged
- [x] Build side-by-side comparison table in `docs/reproducibility_notes.md`
- [x] Mark each model/regime as: **MATCH** (≤0.02), **CLOSE** (0.02–0.05), or **DRIFT** (>0.05) — all MATCH

### 1.8 Reproducibility audit

- [x] Note any preprocessing step present in paper but absent in repo (or vice versa)
- [x] Note any default threshold other than 0.5 for probabilistic classifiers
- [x] Note whether author uses pre-saved `predict_proba` artifacts instead of retraining
- [x] Note any non-deterministic behavior observed across repeated runs
- [x] Document all workarounds (path fixes, dependency pins, manual edits) with file/line refs
- [x] Document Windows-specific issues and fixes (if any)
- [x] Add **Phase 1 conclusion** paragraph: reproduction succeeded / partial / failed (and why)

### 1.9 Phase 1 exit gate

- [x] LR no-SMOTE metrics captured
- [x] LR no-SMOTE within ±0.02 of paper **OR** deviation explained in `docs/reproducibility_notes.md`
- [x] At least one of LDA or AE+LR attempted — both completed
- [x] `results/baseline_reproduction.csv` committed (metrics only — no raw data)
- [x] Phase 1 marked complete in progress summary above

**Paper reference targets (NSL-KDD, no SMOTE — Table 4):**

| Model | Acc | Prec | Rec | F1 | FAR | AUC |
|-------|-----|------|-----|-----|-----|-----|
| NB | 0.5649 | 0.9800 | 0.2406 | 0.3864 | 0.0065 | 0.7987 |
| LR | 0.7443 | 0.9142 | 0.6079 | 0.7302 | 0.0754 | 0.8276 |
| LDA | 0.7616 | 0.9249 | 0.6326 | 0.7514 | 0.0679 | 0.8484 |
| AE+LR | 0.7616 | 0.9165 | 0.6397 | 0.7534 | 0.0770 | 0.9040 |

---

## Phase 2 — Data Loading & EDA

**Target:** Jul 5 · **Exit:** Notebook runs through EDA; imbalance and correlation findings documented

- [x] Implement `src/data_loading.py` (load, dtypes, column names, drop `difficulty`)
- [x] Notebook §1: Data loading & inspection (shape, missing values, duplicates, temporal note)
- [x] Notebook §2: EDA (distributions, outliers, correlations, crosstabs, imbalance)
- [x] Save EDA figures to `results/figures/eda/`

---

## Phase 3 — Feature Engineering

**Target:** Jul 6 (AM) · **Exit:** Leakage-free preprocessing pipeline; redundancy analysis complete

- [x] Implement `src/preprocessing.py` (encode, scale, optional SMOTE, sklearn Pipeline)
- [x] Notebook §3: Feature engineering with cybersecurity rationale per transform
- [x] Redundancy analysis and improvement recommendations
- [x] Update `docs/reproducibility_notes.md` with our preprocessing metadata

---

## Phase 4 — Model Training

**Target:** Jul 6 (PM) · **Exit:** NB, LR, LDA, RF, AE+LR trained; test predictions saved

- [x] Implement `src/models.py` (all models + AE+LR hybrid + SMOTE branch)
- [x] Notebook §4: Train all models (with/without SMOTE); log training times
- [x] Compare our training output against Phase 1 baseline — flag divergences

---

## Phase 5 — Evaluation & Error Analysis

**Target:** Jul 7 (AM) · **Exit:** Full metric suite; FP/FN analysis with attack-subtype breakdown

- [x] Implement `src/evaluation.py` (Acc, Prec, Rec, F1, MCC, AUC, FAR, confusion matrix)
- [x] Notebook §5: Evaluation with per-metric IDS interpretation
- [x] Notebook §6: Error analysis (R2L/U2R focus, FP vs FN trade-off, threshold discussion)
- [x] Save `results/experiment_metrics.csv` and eval figures to `results/figures/eval/`

---

## Phase 6 — Critical Evaluation Synthesis

**Target:** Jul 7 (PM) · **Exit:** Claims C1–C7 verdicts documented; notebook executive summary written

- [x] Build claim evaluation matrix in `docs/critical_evaluation.md` (C1–C7)
- [x] Document methodology strengths and weaknesses
- [x] Draft recommend / not-recommend conclusion for similar IDS problems
- [x] Write notebook executive summary markdown cell (~1 page)

---

## Phase 7 — Report & Documentation

**Target:** Jul 8–9 · **Exit:** PDF report complete; README finalized; notebook clean

- [x] Write `report/final_project_report.pdf` (all 7 assignment sections + executive summary)
- [x] Embed key figures from `results/figures/`
- [x] Finalize `README.md` (links, setup, run instructions, defense cheat sheet)
- [x] Clean notebook — full top-to-bottom run passes

---

## Phase 8 — Final QA & Submission

**Target:** Jul 9–10 · **Exit:** Fresh-env run passes; public repo live; submitted before 23:59

- [x] Fresh venv test: install → download data → run notebook end-to-end
- [x] Verify all PRD acceptance criteria (`prd.md` §12 Must pass)
- [x] Verify rubric coverage (`prd.md` §11)
- [ ] Push to public GitHub; tag `v1.0-submission`
- [ ] Email repo URL to examiner

---

## Blockers log

| Date | Phase | Blocker | Resolution |
|------|-------|---------|------------|
| | | | |

---

## Notes

- Expand Phase 2+ into granular tasks when each phase begins (keeps this file accurate).
- Do not commit raw dataset files or large model binaries to Git.
- Phase 1 results are the evidentiary baseline for claims C1, C2, C5, and C7 in the critical evaluation.
