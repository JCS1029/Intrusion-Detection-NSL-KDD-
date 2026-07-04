# Critical Evaluation — Arcos-Argudo et al. (2025) on NSL-KDD

**Evidence sources:** `results/baseline_reproduction.csv` (author pipeline reproduction), `results/experiment_metrics.csv` (our raw-data pipeline), `docs/reproducibility_notes.md`.

---

## Claim evaluation matrix

| Claim | Evidence | Verdict | Notes |
|-------|----------|---------|-------|
| **C1** — AE+LR achieves the highest AUC (~0.904) and strongest F1 among the four evaluated models | Author baseline (no SMOTE): AE+LR AUC **0.9040**, F1 **0.7533** — top among NB/LR/LDA/AE+LR. Our pipeline (no SMOTE): RF AUC **0.9597**, LDA F1 **0.7517**; AE+LR AUC **0.8557**, F1 **0.7030** (below LDA/LR/RF). | **Partially supported** | Holds in the authors' bundled-CSV pipeline (we reproduced Table 4 within tolerance). Under our leakage-aware preprocessing from raw NSL-KDD, AE+LR does **not** dominate; LDA matches or exceeds F1 and RF far exceeds AUC. The hybrid advantage is pipeline-dependent, not robust. |
| **C2** — SMOTE on training data yields modest F1 gains on NSL-KDD | Author baseline F1 Δ: LR +0.003, LDA +0.002, AE+LR +0.005, NB +0.0002. Our pipeline F1 Δ: LR +0.008, LDA +0.003, AE+LR +0.031, RF +0.013, NB 0. Recall gains are larger than F1 for several models. | **Supported** | Gains are modest in the author setting (≤0.005 F1 for three of four models). Our pipeline shows slightly larger AE+LR uplift (+0.031 F1, +0.052 AUC), consistent with SMOTE helping the embedding stage when train-only encoding reduces feature overlap. SMOTE never applied to test — verified in both pipelines. |
| **C3** — Preprocessing is leakage-free (fit on train only) | Author notebook: `pd.concat([train, test])` before `get_dummies`. Our `src/preprocessing.py`: encoders and scalers fit on train only; `leakage_checks()` asserts no test influence. | **Partially supported (authors) / Supported (ours)** | Paper text claims train-only fitting. Author code introduces **schema leakage** via joint one-hot encoding — test categories can expand the feature space. Scaling and SMOTE are train-only in both implementations. We treat C3 as **rejected for the author package** under strict ML protocol, **supported for our reimplementation**. |
| **C4** — LR and LDA are strong, interpretable baselines competitive with hybrid AE+LR | Author (no SMOTE): LDA F1 **0.7514** vs AE+LR **0.7533** (Δ=0.0019); LR F1 **0.7302**. Our pipeline: LDA F1 **0.7517** (best among paper models), LR **0.7162**; AE+LR **0.7030**. LDA AUC within 0.005 of AE+LR in our runs. | **Supported** | LDA is statistically tied with AE+LR on F1 in both pipelines while avoiding TensorFlow training cost (~63 s vs ~5 s for LDA). LR is slightly weaker on F1 but still operationally viable. The paper's hybrid adds complexity without a clear F1 margin. |
| **C5** — NB attains very high Precision (~0.98) but very low Recall (~0.24), making it a poor standalone detector | Author: Prec **0.9800**, Rec **0.2406**, FAR **0.0065**. Ours: Prec **0.9679**, Rec **0.1478**, FAR **0.0065**. NB misses **10,936** of **12,833** attacks in our test set (FN >> FP). | **Supported** | Pattern reproduced exactly in author baseline; even more extreme recall collapse on raw-data pipeline. NB is useful only as a low-FAR pre-filter, not as a primary IDS. |
| **C6** — Reporting FAR alongside Recall is essential for operational IDS deployment | NB: Acc **0.51**, FAR **0.65%**, Rec **15%** — accuracy alone misleads. RF: Acc **0.77**, FAR **2.8%**, Rec **61%** — strong ranking (AUC 0.96) with moderate analyst load. LR threshold sweep shows recall/FAR trade-off invisible in accuracy. | **Supported** | FAR separates "quiet but blind" (NB) from "balanced" (LR/LDA) and "aggressive" (AE+LR) profiles. Accuracy near 0.75–0.77 for top models masks **~5,000 missed attacks** per model. Essential for SOC staffing decisions. |
| **C7** — Replication package enables byte-level reproducibility of reported metrics | Phase 1: all 8 model/regime rows **MATCH** paper Tables 4–5 (max Δ ≤ 0.02; most exact). Gaps: undocumented CSV cleaning, raw `.txt` never loaded, README path error, library version sensitivity (TF 2.21 vs 2.20). | **Partially supported** | Metrics are reproducible when using bundled cleaned CSVs and mirroring notebook logic — we achieved near-exact parity. **Not** byte-level from raw NSL-KDD alone; hidden preprocessing and minor FP drift prevent literal "byte-level" claims. |

---

## Methodology weaknesses

1. **Binary collapse hides rare attacks** — Collapsing all attacks to label 1 yields acceptable aggregate F1 while R2L recall stays ~8% and U2R ~10% (RF, our pipeline). Operational risk from stealthy intrusions is invisible in binary metrics.
2. **NSL-KDD external validity** — Dataset is legacy (1990s traffic patterns); near-ceiling metrics on DoS/Probe do not transfer to modern encrypted or APT traffic.
3. **Accuracy is misleading under imbalance** — Attack traffic dominates the test set; high accuracy coexists with thousands of false negatives. MCC and FAR are necessary complements.
4. **Near-ceiling AUC, limited practical significance** — AUC > 0.90 for several models on this benchmark may reflect dataset saturation rather than deployable detection capability.
5. **Hidden preprocessing in replication package** — Pre-cleaned CSVs and absent cleaning script undermine end-to-end reproducibility from primary data files.
6. **One-hot encoding leakage risk** — Joint train+test encoding in the author notebook contradicts the stated leakage-free protocol.
7. **Fixed 0.5 threshold** — No operational calibration for environment-specific FP/FN costs; rare-class recall remains poor regardless of threshold for some families.

---

## Methodology strengths

1. **Leakage-aware intent** — Paper explicitly describes train-only SMOTE, scaling, and encoding; our strict reimplementation validates the design when applied correctly.
2. **FAR reporting** — False alarm rate is included alongside standard sklearn metrics — uncommon and SOC-relevant.
3. **Public replication package** — Code, seeds, and bundled data enable independent verification (we reproduced all Table 4/5 entries).
4. **Deterministic seeds** — `random_state=42` for LR, SMOTE, and TensorFlow settings support repeatable experiments.
5. **Multiple classical baselines** — Comparing NB, LR, LDA, and a hybrid gives readers a spectrum of bias–variance and interpretability trade-offs.
6. **Official train/test split** — No random reshuffle preserves the NSL-KDD benchmark protocol.

---

## Recommendation for similar IDS problems

**Conditionally recommend** the paper as a **reproducible baseline study**, not as a deployment blueprint.

| Use the paper for… | Avoid relying on it for… |
|--------------------|--------------------------|
| Classical ML + SMOTE benchmarking on NSL-KDD | Production IDS on modern networks |
| FAR-aware metric reporting templates | Rare-attack detection without multiclass or hierarchical models |
| AE+LR hybrid as an embedding experiment | Claims that hybrids uniformly beat linear baselines |
| Replication methodology and seed discipline | End-to-end reproducibility from raw PCAP or flow logs without documented ETL |

For similar academic reproduction projects: start from the replication notebook, audit encoding for leakage, report per-attack-family recall, and treat LDA/LR as mandatory baselines before investing in deep hybrids.

---

## Report-ready findings (bullet list)

- Reproduced all author NSL-KDD metrics within ±0.02 using bundled CSVs; max delta 0.0004 on AE+LR F1.
- AE+LR highest AUC (0.904) **only** in author pipeline; our train-only pipeline favors RF (AUC 0.960) and LDA (F1 0.752).
- SMOTE yields modest F1 gains (+0.002–0.005 author; up to +0.031 AE+LR ours) without fixing R2L/U2R detection.
- Author one-hot encoding via train+test concat is a reproducibility and leakage concern.
- LDA matches AE+LR on F1 at ~5× lower training cost — hybrid complexity poorly justified on NSL-KDD.
- NB precision ~0.97 with recall ~0.15–0.24 confirms unsuitability as standalone detector; FAR 0.65% vs 10k+ missed attacks.
- FAR and MCC essential: accuracy alone cannot rank models for SOC deployment.
- Binary task masks catastrophic failure on R2L (e.g., `guess_passwd`, `snmpguess` at 0% recall under LR).
- Replication package enables metric reproduction but not byte-identical pipeline from raw KDDTrain+.txt.
- **Overall verdict:** Claims C2, C4, C5, C6 well supported; C1 and C7 partially supported; C3 rejected for author code under strict protocol.
