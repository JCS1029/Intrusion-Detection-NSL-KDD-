# PRD — Data Science in Cyber Final Project

**Project:** Critical Reproduction & Evaluation of IDS on NSL-KDD  
**Course:** Data Science in Cyber — Dr. Uri Itai  
**Source (Option A):** Arcos-Argudo et al. (2025), *Algorithms* 18, 749  
**Deadline:** Friday, July 10, 2026, 23:59  
**Primary dataset:** NSL-KDD  
**Repository:** Public GitHub (submission artifact)

---

## 1. Problem statement

The assignment requires selecting a published cybersecurity data-science article with an accompanying implementation, reproducing its experiments, and **critically evaluating** whether the authors' claims are supported by evidence. The deliverable is not a passive rerun of code — it must demonstrate methodological rigor, objective critique, and clear communication.

This project uses the Applied Sciences 2025 paper comparing classical ML classifiers (NB, LR, LDA) and a hybrid Autoencoder + Logistic Regression (AE+LR) pipeline on intrusion detection benchmarks. We focus on **NSL-KDD** for speed and reproducibility; CICIDS2017 is out of scope unless explicitly added later.

---

## 2. Goals

| ID | Goal |
|----|------|
| G1 | Faithfully reproduce the paper's NSL-KDD binary IDS results within documented tolerance |
| G2 | Critically assess whether the authors' claims hold under independent replication |
| G3 | Produce an assignment-compliant Jupyter notebook with full EDA, feature engineering, modeling, and error analysis |
| G4 | Produce an assignment-compliant PDF report centered on critique of the original work |
| G5 | Publish a public GitHub repository with README, dependencies, and execution instructions |

---

## 3. Non-goals

- Full CICIDS2017 reproduction (2M+ rows) unless scope is explicitly expanded
- Beating state-of-the-art IDS benchmarks or deploying a production system
- Multiclass attack-family classification as the primary task (binary Normal vs Attack matches the paper)
- Student-written code (agent implements; student owns submission and oral defense)

---

## 4. Source of truth

| Artifact | Reference | Purpose |
|----------|-----------|---------|
| Primary article | [DOI 10.3390/a18120749](https://doi.org/10.3390/a18120749) | Problem definition, methodology, claims, target metrics |
| Local article copy | `algorithms-18-00749.pdf` | Offline reference |
| Author replication repo | [github.com/miguelarcosa/IDS-KDD-CICIDS2017](https://github.com/miguelarcosa/IDS-KDD-CICIDS2017) | Reference implementation, configs, seeds |
| Dataset | NSL-KDD `KDDTrain+.txt`, `KDDTest+.txt` | Official train/test split (~148K records total) |
| Assignment brief | `haifaUEX.pdf` | Submission format, rubric, grading criteria |

---

## 5. Author claims to evaluate

These are the hypotheses our reproduction and report must test:

| ID | Claim | Source |
|----|-------|--------|
| C1 | AE+LR achieves the highest AUC on NSL-KDD (~0.904) and the strongest F1 among the four evaluated models | Abstract, Tables 4–5 |
| C2 | SMOTE applied only on training data yields modest F1 gains on NSL-KDD | Section 4.1, Table 5 |
| C3 | All preprocessing (encoding, scaling, imputation) is leakage-free — fit on train only | Section 3.2 |
| C4 | LR and LDA are strong, interpretable baselines competitive with hybrid approaches | Sections 4.3, 5 |
| C5 | Naïve Bayes attains very high Precision (~0.98) but very low Recall (~0.24), making it a poor standalone detector | Tables 4–5 |
| C6 | Reporting FAR alongside Recall is essential for operational IDS deployment | Sections 3.4, 4.3 |
| C7 | The replication package enables byte-level reproducibility of reported metrics | Section 3.4, Data Availability |

---

## 6. Deliverables

### 6.1 GitHub repository (public)

```
data-science-in-cyber/
├── README.md
├── requirements.txt
├── .gitignore
├── prd.md
├── plan.md
├── data/
│   └── raw/                         # gitignored; download via instructions
├── notebooks/
│   └── ids_nsl_kdd_analysis.ipynb   # primary executable notebook
├── src/
│   ├── data_loading.py
│   ├── preprocessing.py
│   ├── models.py
│   └── evaluation.py
├── results/
│   ├── baseline_reproduction.csv
│   ├── experiment_metrics.csv
│   └── figures/
├── report/
│   └── final_project_report.pdf
└── docs/
    └── reproducibility_notes.md
```

### 6.2 Jupyter notebook

Single primary notebook (`notebooks/ids_nsl_kdd_analysis.ipynb`), executable end-to-end after data download. Supporting logic may live in `src/` and be imported by the notebook.

### 6.3 PDF report

English-language report covering all assignment sections (see Section 8).

### 6.4 README

Must include: project description, link to article, link to original repo, dataset source, execution instructions, expected runtime.

---

## 7. Functional requirements

### 7.1 Data loading & inspection

- [ ] Load NSL-KDD train and test files with correct column names
- [ ] Report data size, feature types, and memory usage
- [ ] Missing value analysis
- [ ] Analyze column and index naming — document whether structure makes sense
- [ ] Handle irrelevant columns (e.g., drop `difficulty`)
- [ ] Detect and document duplicated or single-value features
- [ ] Temporal analysis: document that NSL-KDD has no timestamps and state the limitation
- [ ] Label distribution for binary and multi-class views

### 7.2 Exploratory data analysis

- [ ] Feature distributions (numeric and categorical)
- [ ] Outlier analysis
- [ ] Correlation analysis with **justified method** (Pearson, Spearman, and/or Kendall)
- [ ] Crosstab / group-by analysis (e.g., `protocol_type`, `service`, `flag` vs label)
- [ ] Class imbalance analysis with real-world cybersecurity meaning
- [ ] Assess whether authors addressed imbalance (SMOTE on train)
- [ ] Relevant visualizations saved to `results/figures/`

### 7.3 Feature engineering

- [ ] Binary label mapping: `normal` → 0, all attacks → 1
- [ ] One-hot encoding for categorical features (`protocol_type`, `service`, `flag`)
- [ ] Min–max scaling to [0, 1] fit on train, applied to test
- [ ] Optional SMOTE branch — train only, never on test
- [ ] Feature redundancy analysis (correlation clusters, duplicate detection)
- [ ] Feature selection or dimensionality discussion where appropriate
- [ ] Document why each transformation was applied and its effect

### 7.4 Model training

Minimum models:

| Model | Role |
|-------|------|
| Logistic Regression | Assignment minimum + paper baseline |
| Random Forest | Assignment minimum + extension beyond paper |
| Naïve Bayes | Paper reproduction |
| LDA | Paper reproduction |
| AE+LR | Paper reproduction (hybrid) |

Optional: XGBoost if time permits.

All models must use:
- Preprocessing fit on training data only
- `random_state=42` where applicable
- Train/test split matching paper (official KDDTrain+ / KDDTest+)

### 7.5 Evaluation

Required metrics (with cybersecurity interpretation in notebook and report):

| Metric | Required |
|--------|----------|
| Accuracy | Yes |
| Precision | Yes |
| Recall | Yes |
| F1 | Yes |
| ROC-AUC | Yes |
| MCC | Yes |
| Confusion matrix | Yes |
| FAR (False Alarm Rate) | Yes — paper-specific, IDS-relevant |
| Fβ | Optional, justified if used |

Each metric must include: mathematical meaning, why it matters for IDS, and FP vs FN implications.

### 7.6 Error analysis

- [ ] Examples or patterns of model failures
- [ ] Analysis by attack subtype where feasible (DoS, Probe, R2L, U2R)
- [ ] Cybersecurity implications of false positives and false negatives
- [ ] Trade-off discussion between FP and FN for SOC deployment

### 7.7 Notebook executive summary

- [ ] ~1 page markdown cell summarizing the full project

---

## 8. PDF report structure

| Section | Content | Rubric weight |
|---------|---------|---------------|
| Executive Summary | ~1 page overview | — |
| 1. Summary of the Source | Problem, importance, solution, dataset, methodology | 15 pts |
| 2. Critical Evaluation | Claims vs evidence, methodology appropriateness, limitations, justified conclusions | 20 pts |
| 3. Feature Engineering Analysis | Transformations, redundancy, meaningfulness, suggested improvements | 10 pts |
| 4. Reproducibility Analysis | Code execution, dependencies, hidden steps, overall reproducibility | — |
| 5. Experimental Results | Our experiments, modifications, models, metrics, results | 30 pts (EDA + models) |
| 6. Conclusions | Key findings, lessons, strengths/weaknesses, future work | — |
| 7. Summing It Up | Concise reader-facing summary with claim verdict and recommendation | — |

**Emphasis:** The report critiques the **authors' work**, not only our implementation.

---

## 9. Technical specifications

### 9.1 Data

| Field | Specification |
|-------|---------------|
| Train | `KDDTrain+.txt` — 125,973 records |
| Test | `KDDTest+.txt` — 22,543 records |
| Features | 41 input features + `label` + `difficulty` |
| Task | Binary: Normal vs Attack |
| Split | Official NSL-KDD train/test — do not reshuffle |

### 9.2 Preprocessing pipeline (match paper Section 3.2)

```
Training:
  categorical → one-hot encode (fit on train)
  numeric     → min-max scale [0,1] (fit on train)
  optional    → SMOTE (fit/resample train only)
  model.fit(X_train, y_train)

Testing:
  transform with fitted encoders/scalers
  no SMOTE
  model.predict / predict_proba
```

### 9.3 Model hyperparameters (paper defaults)

| Model | Configuration |
|-------|---------------|
| Naïve Bayes | `GaussianNB`, defaults |
| Logistic Regression | L2, `max_iter=1000` |
| LDA | default (NSL-KDD) |
| Random Forest (ours) | `n_estimators=100`, `random_state=42` |
| AE+LR | AE: Dense(64)→Dense(32)→Dense(64), ReLU, sigmoid output; MSE loss; Adam 1e-3; batch 256; 20 epochs; LR on embeddings, `max_iter=1000` |
| SMOTE | `random_state=42`, `k_neighbors=5`, train only |

### 9.4 Target reproduction metrics (NSL-KDD, no SMOTE — paper Table 4)

| Model | Accuracy | Precision | Recall | F1 | FAR | AUC |
|-------|----------|-----------|--------|-----|-----|-----|
| NB | 0.5649 | 0.9800 | 0.2406 | 0.3864 | 0.0065 | 0.7987 |
| LR | 0.7443 | 0.9142 | 0.6079 | 0.7302 | 0.0754 | 0.8276 |
| LDA | 0.7616 | 0.9249 | 0.6326 | 0.7514 | 0.0679 | 0.8484 |
| AE+LR | 0.7616 | 0.9165 | 0.6397 | 0.7534 | 0.0770 | 0.9040 |

**Tolerance:** ±0.02 per metric acceptable if cause is documented (library versions, environment).

### 9.5 Environment

| Dependency | Target |
|------------|--------|
| Python | 3.12.x |
| scikit-learn | pinned in `requirements.txt` |
| TensorFlow | 2.x (for AE+LR) |
| imbalanced-learn | for SMOTE |
| pandas, numpy, matplotlib, seaborn | standard analysis stack |

---

## 10. Code quality requirements

- Short, focused functions in `src/`
- Meaningful variable names
- No unnecessary loops; use pandas/numpy/sklearn idioms
- Clear separation: load → preprocess → train → evaluate
- English comments for non-obvious logic
- No duplicated code between notebook and `src/`
- Fixed random seeds
- Proper train/test protocol — no test leakage

---

## 11. Grading rubric mapping

| Component | Points | Primary artifact |
|-----------|--------|----------------|
| Problem understanding & source selection | 10 | Report §1, README |
| Summary quality | 15 | Report §1 |
| Critical evaluation of author's claims | 20 | Report §2 |
| Feature engineering analysis | 10 | Report §3, Notebook §FE |
| Exploratory data analysis | 15 | Notebook §EDA, Report §5 |
| Model training & comparison | 15 | Notebook §Models, Report §5 |
| Evaluation & error analysis | 10 | Notebook §Eval, Report §5 |
| Code quality & software engineering | 5 | `src/`, notebook structure |
| **Total** | **100** | |

---

## 12. Acceptance criteria

### Must pass (blocking)

- [ ] Public GitHub repo with all required artifacts
- [ ] Notebook runs top-to-bottom after documented data download
- [ ] NSL-KDD results reproduced for LR; deviations for other models explained
- [ ] ≥2 models trained with full metric suite including MCC and FAR
- [ ] Report critically evaluates ≥5 author claims with evidence
- [ ] README contains all required links and instructions
- [ ] Submitted before July 10, 2026, 23:59

### Should pass

- [ ] AE+LR reproduced
- [ ] SMOTE with/without comparison completed
- [ ] Per-attack-type error analysis (R2L, U2R emphasis)
- [ ] Feature redundancy formally analyzed

### Nice to have

- [ ] XGBoost comparison
- [ ] SHAP / feature importance for interpretability
- [ ] CICIDS2017 subset experiment

---

## 13. Stakeholders & responsibilities

| Role | Responsibility |
|------|----------------|
| Student | Source approval, submission, oral defense if invited |
| Agent | All implementation, analysis, report drafting, repo setup |
| Lecturer (Uri Itai) | Grading, optional oral review |

---

## 14. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Author repo fails on Windows | High | WSL fallback; reimplement pipeline from paper |
| Metric mismatch vs paper | Medium | Pin versions; document in reproducibility section |
| TensorFlow / AE+LR issues | Medium | Version pin; sklearn MLP fallback with disclosure |
| NSL-KDD column naming variants | Medium | Use column list from author repo |
| Time overrun | Medium | NSL-KDD only; defer optional models |
| Oral defense | Medium | README defense summary with key claims and numbers |
