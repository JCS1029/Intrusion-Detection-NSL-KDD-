"""Generate report/final_project_report.pdf per PRD Section 8."""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "report" / "final_project_report.pdf"
FIGURES = PROJECT_ROOT / "results" / "figures"


def wrap(text: str, width: int = 95) -> str:
    return "\n".join(textwrap.fill(p, width=width) for p in text.strip().split("\n\n"))


def text_page(pdf: PdfPages, title: str, body: str, subtitle: str = "") -> None:
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    y = 0.94
    fig.text(0.5, y, title, ha="center", va="top", fontsize=14, fontweight="bold")
    y -= 0.04
    if subtitle:
        fig.text(0.5, y, subtitle, ha="center", va="top", fontsize=10, style="italic")
        y -= 0.05
    fig.text(0.08, y, wrap(body), ha="left", va="top", fontsize=9, family="sans-serif")
    plt.axis("off")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def figure_page(pdf: PdfPages, title: str, image_path: Path, caption: str = "") -> None:
    if not image_path.exists():
        text_page(pdf, title, f"[Figure not found: {image_path.name}]")
        return
    img = mpimg.imread(image_path)
    fig, ax = plt.subplots(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    ax.imshow(img)
    ax.axis("off")
    fig.suptitle(title, fontsize=12, fontweight="bold", y=0.98)
    if caption:
        fig.text(0.5, 0.02, wrap(caption, 110), ha="center", va="bottom", fontsize=8)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def metrics_table(df: pd.DataFrame) -> str:
    cols = ["model", "smote", "accuracy", "precision", "recall", "f1", "far", "auc"]
    sub = df[cols].copy()
    sub["smote"] = sub["smote"].map({True: "yes", False: "no"})
    for c in ["accuracy", "precision", "recall", "f1", "far", "auc"]:
        sub[c] = sub[c].map(lambda x: f"{x:.4f}")
    return sub.to_string(index=False)


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    exp = pd.read_csv(PROJECT_ROOT / "results" / "experiment_metrics.csv")
    baseline = pd.read_csv(PROJECT_ROOT / "results" / "baseline_reproduction.csv")
    baseline_ours = baseline[baseline["notes"] == "author notebook logic"]
    smote_delta = pd.read_csv(PROJECT_ROOT / "results" / "smote_delta.csv")

    no_smote_exp = exp[exp["smote"] == False]  # noqa: E712
    metrics_no_smote = metrics_table(no_smote_exp)

    exec_summary = """
This report presents an independent reproduction and critical evaluation of Arcos-Argudo et al. (2025),
who compare classical machine learning classifiers and an Autoencoder + Logistic Regression (AE+LR) hybrid
for binary intrusion detection on NSL-KDD.

We reproduced all author NSL-KDD metrics within ±0.02 using their replication package, then rebuilt the
pipeline from raw KDDTrain+.txt / KDDTest+.txt with leakage-aware preprocessing. Key findings: LDA matches
AE+LR on F1 at far lower training cost; Random Forest (our extension) achieves the highest AUC (0.960);
SMOTE yields modest aggregate gains but does not fix rare-attack detection (R2L recall ~8%); Naïve Bayes
confirms extreme precision/recall asymmetry; and the author notebook's train+test concat encoding contradicts
a strict leakage-free claim.

Recommendation: adopt the paper's metric framework (especially FAR) for tabular IDS benchmarks, but do not
treat AE+LR superiority or high AUC as evidence of deployable detection without per-family evaluation.
"""

    section1 = """
Problem. Intrusion detection systems (IDS) must distinguish malicious from benign network traffic under
class imbalance and asymmetric error costs — false negatives miss breaches; false positives burden analysts.

Source. Arcos-Argudo et al. (2025), Algorithms 18(12), 749, compare Naïve Bayes, Logistic Regression,
Linear Discriminant Analysis, and AE+LR on NSL-KDD (binary Normal vs Attack) and CICIDS2017. We focus on
NSL-KDD per assignment scope.

Dataset. Official split: KDDTrain+.txt (125,973 records) and KDDTest+.txt (22,544 records); 41 features
plus label and difficulty (dropped). No timestamps — connection-level features only.

Methodology. One-hot encoding of protocol_type, service, flag; min-max scaling fit on train; optional SMOTE
on train only; fixed random_state=42. AE: Dense(64)→32→64, 20 epochs; LR on 32-dim embeddings. Metrics:
Accuracy, Precision, Recall, F1, FAR, ROC-AUC.

Importance. The paper claims AE+LR achieves the highest AUC (~0.904), SMOTE helps modestly, preprocessing
is leakage-free, and the replication package enables byte-level reproducibility — claims we test with
independent evidence.
"""

    section2 = """
We evaluate seven author claims (C1–C7) using results/baseline_reproduction.csv (author pipeline) and
results/experiment_metrics.csv (our train-only pipeline from raw data).

C1 (AE+LR best AUC/F1): PARTIALLY SUPPORTED. Author baseline: AE+LR AUC 0.904, F1 0.753 (top among four).
Our pipeline: RF AUC 0.960, LDA F1 0.752; AE+LR below both. Hybrid advantage is pipeline-dependent.

C2 (SMOTE modest F1 gains): SUPPORTED. Author ΔF1 +0.002–0.005; ours up to +0.031 (AE+LR). Always train-only.

C3 (Leakage-free preprocessing): REJECTED for author code / SUPPORTED for ours. Author concat train+test
before get_dummies introduces schema leakage. Our src/preprocessing.py fits encoders on train only.

C4 (LR/LDA strong baselines): SUPPORTED. LDA F1 within 0.002 of AE+LR in both pipelines.

C5 (NB high Prec, low Rec): SUPPORTED. Prec ~0.97–0.98, Rec ~0.15–0.24, FAR 0.65%.

C6 (FAR essential): SUPPORTED. NB accuracy 0.51 with minimal FAR but ~85% missed attacks; accuracy alone misleads.

C7 (Byte-level reproducibility): PARTIALLY SUPPORTED. All Table 4/5 metrics matched with bundled CSVs; hidden
CSV ETL and library drift prevent reproduction from raw .txt alone.

Limitations. Binary collapse hides R2L/U2R failure; NSL-KDD is legacy; near-ceiling DoS/Probe metrics lack
modern external validity; fixed 0.5 threshold ignores operational calibration.
"""

    section3 = """
Transformations applied (our pipeline, src/preprocessing.py):

1. Binary label: normal→0, all attacks→1 (matches paper task definition).
2. Drop constant feature num_outbound_cmds (zero variance in train).
3. Drop highly correlated numerics (|Pearson r| ≥ 0.95 on train): seven error-rate/host statistics removed.
4. One-hot encode categoricals — train-only schema (106 features) vs author concat style (119 features).
5. MinMaxScaler fit on train, applied to test.
6. SMOTE optional on train only (random_state=42, k_neighbors=5).

Redundancy. EDA and correlation analysis show clusters among dst_host_* error rates and serror/rerror features.
Removing them reduces multicollinearity without large metric loss for LR/LDA.

Cybersecurity rationale. Protocol/service/flag encode attack vectors; byte and connection counts capture volume
anomalies; scaling puts heterogeneous counts on comparable ranges for linear models.

Feature creation (exploratory). We evaluated derived candidates such as bytes_ratio = src_bytes /
(dst_bytes + 1) for asymmetric traffic patterns; they show class separation in EDA but were not added to
final models to preserve comparability with the authors' feature space.

Suggested improvements. Per-family or hierarchical labels for R2L/U2R; log-scaled byte counts; threshold
tuning on validation data; audit encoding for leakage; report MCC and per-family recall alongside binary F1.
"""

    section4 = """
Execution. Author baseline via scripts/run_phase1_baseline.py mirroring vendor/.../BACK-nsl-kdd-github.ipynb.
Our pipeline via src/ modules and notebooks/ids_nsl_kdd_analysis.ipynb from raw NSL-KDD files.

Environment. Python 3.12.10, scikit-learn 1.9.0, TensorFlow 2.21.0, imbalanced-learn 0.14.2 (Windows 10 CPU).
Paper reports TF 2.20 / sklearn 1.7.2 — minor AE+LR floating-point drift observed (F1 Δ ≤ 0.0004).

Reproduction outcome. All eight author model/regime combinations MATCH paper Tables 4–5 (max Δ ≤ 0.02).

Hidden steps. Author notebook uses pre-cleaned binary CSVs; raw KDDTrain+.txt never loaded; cleaning script
absent. One row dropped per split (125,972 / 22,542 vs 125,973 / 22,544). README lists wrong notebook path.

Overall reproducibility. Functional for metric verification with bundled artifacts; not end-to-end from primary
data files without reverse-engineering. Our reimplementation documents the gap and applies strict train-only
encoding.
"""

    section5_intro = f"""
Our experiments extend the paper with Random Forest (n_estimators=100) and train-only preprocessing from raw
NSL-KDD. Below: test-set metrics without SMOTE (our pipeline).

{metrics_no_smote}

SMOTE impact (ΔF1): {', '.join(f"{r.model} {r.delta_f1:+.4f}" for r in smote_delta.itertuples())}.

Error analysis (RF, no SMOTE): DoS recall 0.80, Probe 0.69, R2L 0.08, U2R 0.10. Rare subclasses such as
guess_passwd and snmpguess show 0% recall under LR.

Author baseline comparison: LR and LDA within ±0.02 of author metrics; NB and AE+LR diverge due to encoding
and feature-set differences (documented in results/baseline_comparison.csv).

Metric selection. We report Accuracy, Precision, Recall, F1, MCC, FAR, and AUC. Fβ is omitted by design:
FAR quantifies false alarms on normal traffic, recall covers missed attacks, and LR threshold sweeps expose
the operational FP/FN trade-off without fixing β. MCC summarizes performance under class skew.
"""

    section6 = """
Key findings.
• Reproduced all author NSL-KDD metrics within tolerance using replication package.
• AE+LR leads only in author CSV pipeline; LDA/RF competitive or superior under strict preprocessing.
• SMOTE: modest aggregate F1 gains; does not fix rare-attack detection.
• NB confirms precision-first profile unsuitable as standalone detector.
• FAR and MCC required alongside accuracy for SOC-relevant comparison.

Strengths of source work. Public code, fixed seeds, FAR reporting, multiple baselines, official train/test split.

Weaknesses. Binary evaluation masks R2L/U2R failure; legacy dataset; hidden CSV ETL; encoding leakage risk;
hybrid complexity poorly justified on F1.

Future work. Multiclass or hierarchical evaluation; contemporary datasets (CICIDS2017 subset); operational
threshold calibration; SHAP/feature importance for interpretability.
"""

    section7 = """
Arcos-Argudo et al. deliver a reproducible classical-ML benchmark with thoughtful metric reporting, but
headline claims require qualification. AE+LR superiority (C1) holds only in their bundled preprocessing
pipeline. SMOTE (C2), LDA/LR competitiveness (C4), NB behavior (C5), and FAR necessity (C6) are well
supported. Leakage-free preprocessing (C3) fails under strict audit of author code. Byte-level
reproducibility (C7) is partial — metrics yes, raw-data pipeline no.

Verdict: Conditionally recommend as a benchmarking reference for NSL-KDD tabular IDS studies. Do not deploy
or cite near-0.90 AUC as operational readiness without per-attack-family evidence on modern traffic.

Repository: notebooks/ids_nsl_kdd_analysis.ipynb, docs/critical_evaluation.md, results/experiment_metrics.csv.
"""

    key_figures = [
        ("Figure 1 — Class balance", FIGURES / "eda" / "08_class_balance.png",
         "Train vs test label distribution; imbalance motivates train-only SMOTE."),
        ("Figure 2 — Feature correlation (Pearson)", FIGURES / "eda" / "06_correlation_pearson.png",
         "Redundant error-rate clusters motivate correlation-based feature drops."),
        ("Figure 3 — Encoding feature counts", FIGURES / "feature_engineering" / "encoding_feature_counts.png",
         "Train-only (106) vs author concat encoding (119 features)."),
        ("Figure 4 — ROC curves (no SMOTE)", FIGURES / "eval" / "roc_no_smote.png",
         "RF dominates AUC; AE+LR below RF and comparable to LDA."),
        ("Figure 5 — F1 by model", FIGURES / "eval" / "metric_f1.png",
         "LDA best F1 among paper models; NB lowest."),
        ("Figure 6 — FAR by model", FIGURES / "eval" / "metric_far.png",
         "NB minimal FAR vs higher FAR for LR/AE+LR."),
        ("Figure 7 — RF recall by attack family", FIGURES / "eval" / "rf_recall_by_family.png",
         "R2L and U2R remain poorly detected despite strong binary metrics."),
        ("Figure 8 — Confusion matrix (RF)", FIGURES / "eval" / "cm_RF_no_smote.png",
         "High TN/TP with substantial FN on minority attack patterns."),
        ("Figure 9 — FP/FN trade-off", FIGURES / "eval" / "fp_fn_tradeoff.png",
         "Model profiles for SOC deployment: NB conservative, RF balanced."),
    ]

    with PdfPages(REPORT_PATH) as pdf:
        text_page(
            pdf,
            "Data Science in Cyber — Final Project Report",
            exec_summary,
            subtitle="Critical Reproduction & Evaluation: Arcos-Argudo et al. (2025) on NSL-KDD",
        )
        text_page(pdf, "1. Summary of the Source", section1)
        text_page(pdf, "2. Critical Evaluation", section2)
        text_page(pdf, "3. Feature Engineering Analysis", section3)
        text_page(pdf, "4. Reproducibility Analysis", section4)
        text_page(pdf, "5. Experimental Results", section5_intro)
        for title, path, caption in key_figures:
            figure_page(pdf, title, path, caption)
        text_page(pdf, "6. Conclusions", section6)
        text_page(pdf, "7. Summing It Up", section7)

        d = pdf.infodict()
        d["Title"] = "IDS NSL-KDD Critical Reproduction Report"
        d["Author"] = "Data Science in Cyber Final Project"
        d["Subject"] = "Critical evaluation of Arcos-Argudo et al. (2025)"

    print(f"Wrote {REPORT_PATH} ({REPORT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
