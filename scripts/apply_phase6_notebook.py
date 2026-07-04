"""Apply Phase 6 notebook edits: executive summary, section 7, remove Phase labels."""
import json
from pathlib import Path

NOTEBOOK = Path("notebooks/ids_nsl_kdd_analysis.ipynb")

CELL0 = """# IDS NSL-KDD — Data Science in Cyber Final Project

Reproduction and critical evaluation of Arcos-Argudo et al. (2025) on the NSL-KDD intrusion detection benchmark.

Source paper: Arcos-Argudo et al. (2025), *Algorithms* 18, 749.

## Executive Summary

This notebook reproduces and critically evaluates Arcos-Argudo et al. (2025), who compare classical classifiers (Naïve Bayes, Logistic Regression, LDA) and a hybrid Autoencoder + Logistic Regression (AE+LR) pipeline for binary intrusion detection on NSL-KDD.

**Reproduction.** We ran the authors' replication notebook logic via `results/baseline_reproduction.csv` and independently rebuilt the pipeline from raw `KDDTrain+.txt` / `KDDTest+.txt` in `src/`. All eight author model/regime combinations match paper Tables 4–5 within ±0.02 (most exact). Our train-only preprocessing pipeline (106 features, correlated numerics dropped) diverges from the authors' bundled CSVs and joint one-hot encoding (119 features).

**Key results (our pipeline, no SMOTE).** LDA achieves the best F1 among paper models (0.752); Random Forest — added as an assignment extension — achieves the highest AUC (0.960). AE+LR underperforms LDA on both F1 (0.703) and AUC (0.856) in our setting, contradicting the paper's headline claim when preprocessing is strictly leakage-free. Naïve Bayes retains extreme precision (0.968) and minimal FAR (0.65%) but misses ~85% of attacks (recall 0.15).

**SMOTE.** Training-only SMOTE produces modest F1 gains (+0.003 LDA, +0.008 LR, +0.031 AE+LR) without resolving rare-attack failure: R2L family recall stays ~8% and U2R ~10% for the best models.

**Critical verdict on author claims (C1–C7).** SMOTE benefit (C2), LDA/LR competitiveness (C4), NB precision/recall trade-off (C5), and FAR necessity (C6) are **supported**. AE+LR superiority (C1) and byte-level reproducibility (C7) are **partially supported** — true in the author CSV pipeline, fragile otherwise. Leakage-free preprocessing (C3) is **rejected** for the author notebook (train+test concat before encoding) but **supported** for our implementation.

**Recommendation.** Use the paper as a reproducible classical-ML benchmark with good metric hygiene (FAR, fixed seeds), not as a deployment recipe. For similar IDS studies: audit encoding for leakage, report per-attack-family recall, and treat LDA/LR as mandatory baselines before investing in hybrid models.

Full claim matrix and methodology critique: `docs/critical_evaluation.md`.
"""

SECTION7 = """## 7. Critical evaluation

We synthesize reproduction evidence against the seven author claims (C1–C7) defined in `prd.md`, using `results/baseline_reproduction.csv` (author pipeline), `results/experiment_metrics.csv` (our pipeline), and audits in `docs/reproducibility_notes.md`. The full matrix lives in `docs/critical_evaluation.md`.

### 7.1 Claim verdicts

| Claim | Summary | Verdict |
|-------|---------|---------|
| **C1** — AE+LR best AUC (~0.904) and F1 | Author baseline: AE+LR AUC 0.904, F1 0.753 (top among four). Our pipeline: RF AUC 0.960, LDA F1 0.752; AE+LR below both. | **Partially supported** |
| **C2** — SMOTE modest F1 gains | Author ΔF1: +0.003 LR, +0.002 LDA, +0.005 AE+LR. Ours: up to +0.031 AE+LR; always train-only. | **Supported** |
| **C3** — Leakage-free preprocessing | Author: concat train+test before one-hot. Ours: fit encoders/scalers on train only. | **Rejected (author) / Supported (ours)** |
| **C4** — LR/LDA strong baselines | LDA F1 within 0.002 of AE+LR in author runs; same in ours. LR slightly lower but competitive. | **Supported** |
| **C5** — NB high Prec, low Rec | Prec ~0.97–0.98, Rec ~0.15–0.24, FAR 0.65%; 10,936 FN vs 63 FP (our NB). | **Supported** |
| **C6** — FAR essential for IDS | NB accuracy 0.51 with low FAR but blind to attacks; threshold sweeps show hidden recall/FAR trade-offs. | **Supported** |
| **C7** — Byte-level reproducibility | All Table 4/5 metrics matched; hidden CSV ETL and library drift prevent raw-data byte identity. | **Partially supported** |

### 7.2 Methodology critique

**Weaknesses**

- Binary labels hide catastrophic R2L/U2R failure (e.g., `guess_passwd`, `snmpguess` at 0% recall under LR).
- NSL-KDD is legacy; near-ceiling DoS/Probe metrics lack external validity for modern networks.
- Accuracy (~0.75–0.77 for top models) masks ~5,000 missed attacks per model on the test set.
- Author replication depends on undocumented cleaned CSVs and joint encoding that risks schema leakage.

**Strengths**

- FAR included alongside standard metrics — operationally meaningful for SOC staffing.
- Fixed seeds and public code enabled independent verification (we matched all reported NSL-KDD numbers).
- Train-only SMOTE and official KDDTrain+/KDDTest+ split follow sound experimental protocol when implemented correctly.

### 7.3 Conclusions and recommendation

The authors deliver a **reproducible classical-ML benchmark** with thoughtful metric reporting, but several headline claims **do not survive strict preprocessing** or **multiclass scrutiny**. LDA provides equivalent F1 to AE+LR at a fraction of training cost; Random Forest (our extension) dominates AUC. SMOTE helps modestly but does not fix rare-attack detection.

**Recommendation:** Adopt the paper's metric framework (especially FAR and fixed seeds) for similar tabular IDS benchmarks. Do **not** treat AE+LR superiority or near-0.90 AUC as evidence of deployable detection without per-family evaluation on contemporary data.

### 7.4 Report-ready findings

- Reproduced all author NSL-KDD metrics within tolerance; replication package works with bundled CSVs.
- AE+LR leads only in author pipeline; LDA/RF competitive or superior under train-only encoding.
- SMOTE: modest aggregate F1 gains; R2L recall remains ~8%, U2R ~10%.
- NB: precision-first profile unsuitable as standalone detector (FAR 0.65%, recall ~15%).
- Author train+test concat encoding contradicts leakage-free claim — audit before trusting results.
- FAR and MCC required alongside accuracy for meaningful SOC comparison.
"""


def main() -> None:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    cells = nb["cells"]

    # Cell 0: executive summary
    cells[0]["source"] = [line + "\n" for line in CELL0.split("\n")]
    if cells[0]["source"]:
        cells[0]["source"][-1] = cells[0]["source"][-1].rstrip("\n")

    # Remove Phase labels in existing cells
    for cell in cells:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell.get("source", []))
        src = src.replace("(Phase 1 baseline)", "(author baseline)")
        src = src.replace("## Phase 2 summary", "## Exploratory analysis — key takeaways")
        src = src.replace("**Next (Phase 3):** leakage-aware preprocessing and feature engineering.", "")
        src = src.replace("\num_outbound_cmds", "`num_outbound_cmds`")
        cell["source"] = [line + "\n" for line in src.split("\n")]
        if cell["source"]:
            cell["source"][-1] = cell["source"][-1].rstrip("\n")

    # Append section 7 if not present
    if not any("## 7. Critical evaluation" in "".join(c.get("source", [])) for c in cells):
        cells.append(
            {
                "cell_type": "markdown",
                "id": "critical-eval-section7",
                "metadata": {},
                "source": [line + "\n" for line in SECTION7.split("\n")],
            }
        )
        if cells[-1]["source"]:
            cells[-1]["source"][-1] = cells[-1]["source"][-1].rstrip("\n")

    NOTEBOOK.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {NOTEBOOK} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
