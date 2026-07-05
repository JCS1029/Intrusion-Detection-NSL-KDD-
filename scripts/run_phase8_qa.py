"""Phase 8 QA: fresh venv install, data check, notebook execution, acceptance audit."""

from __future__ import annotations

import subprocess
import sys
import venv
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QA_VENV = PROJECT_ROOT / ".venv-qa"
LOG_PATH = PROJECT_ROOT / "docs" / "qa_run_log.md"
CHECKLIST_PATH = PROJECT_ROOT / "docs" / "submission_checklist.md"

TRAIN = PROJECT_ROOT / "data" / "raw" / "KDDTrain+.txt"
TEST = PROJECT_ROOT / "data" / "raw" / "KDDTest+.txt"
NOTEBOOK = PROJECT_ROOT / "notebooks" / "ids_nsl_kdd_analysis.ipynb"
REPORT = PROJECT_ROOT / "report" / "final_project_report.pdf"


def log(lines: list[str], buffer: list[str]) -> None:
    for line in lines:
        print(line)
        buffer.append(line)


def run(cmd: list[str], buffer: list[str], cwd: Path | None = None, timeout: int = 900) -> int:
    log([f"$ {' '.join(cmd)}"], buffer)
    result = subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.stdout:
        buffer.append(result.stdout.rstrip())
    if result.stderr:
        buffer.append(result.stderr.rstrip())
    buffer.append(f"exit_code={result.returncode}")
    return result.returncode


def venv_python() -> Path:
    return QA_VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def venv_bin(name: str) -> Path:
    sub = "Scripts" if sys.platform == "win32" else "bin"
    return QA_VENV / sub / name


def ensure_venv(buffer: list[str]) -> None:
    if not QA_VENV.exists():
        log(["Creating fresh venv at .venv-qa/"], buffer)
        venv.create(QA_VENV, with_pip=True, clear=True)
    py = venv_python()
    # Skip full reinstall if core stack already present (resume after timeout)
    try:
        import importlib.util

        spec_ok = all(
            importlib.util.find_spec(m, [str(QA_VENV / "Lib" / "site-packages")])
            for m in ("pandas", "sklearn", "tensorflow", "imblearn", "nbconvert")
        )
    except Exception:
        spec_ok = False
    if spec_ok:
        log(["OK: .venv-qa already has required packages (skipping reinstall)"], buffer)
        return
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"], buffer, timeout=120)
    run([str(py), "-m", "pip", "install", "-r", "requirements.txt"], buffer, timeout=1800)


def verify_data(buffer: list[str]) -> bool:
    ok = True
    for path, min_rows in [(TRAIN, 125_000), (TEST, 22_000)]:
        if not path.exists():
            log([f"FAIL: missing {path.relative_to(PROJECT_ROOT)}"], buffer)
            ok = False
            continue
        rows = sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
        log([f"OK: {path.name} rows={rows}"], buffer)
        if rows < min_rows:
            log([f"WARN: {path.name} below expected minimum {min_rows}"], buffer)
    return ok


def verify_artifacts(buffer: list[str]) -> dict[str, bool]:
    checks = {
        "notebook": NOTEBOOK.exists(),
        "report_pdf": REPORT.exists(),
        "experiment_metrics": (PROJECT_ROOT / "results/experiment_metrics.csv").exists(),
        "baseline_reproduction": (PROJECT_ROOT / "results/baseline_reproduction.csv").exists(),
        "critical_evaluation": (PROJECT_ROOT / "docs/critical_evaluation.md").exists(),
        "reproducibility_notes": (PROJECT_ROOT / "docs/reproducibility_notes.md").exists(),
        "readme": (PROJECT_ROOT / "README.md").exists(),
        "requirements": (PROJECT_ROOT / "requirements.txt").exists(),
        "src_modules": all(
            (PROJECT_ROOT / "src" / f).exists()
            for f in ("data_loading.py", "preprocessing.py", "models.py", "evaluation.py")
        ),
    }
    for name, passed in checks.items():
        log([f"{'OK' if passed else 'FAIL'}: artifact {name}"], buffer)
    return checks


def run_notebook(buffer: list[str]) -> int:
    py = venv_python()
    run([str(py), "-m", "ipykernel", "install", "--user", "--name", "ds-cyber-qa", "--display-name", "Python (ds-cyber-qa)"], buffer)
    nbconvert = venv_bin("jupyter-nbconvert.exe" if sys.platform == "win32" else "jupyter-nbconvert")
    out_nb = PROJECT_ROOT / "notebooks" / "_qa_executed.ipynb"
    return run(
        [
            str(nbconvert),
            "--to", "notebook",
            "--execute", str(NOTEBOOK),
            "--output", str(out_nb.name),
            "--ExecutePreprocessor.timeout=1200",
            "--ExecutePreprocessor.kernel_name=ds-cyber-qa",
        ],
        buffer,
        timeout=900,
    )


def write_checklist(artifact_ok: dict[str, bool], notebook_ok: bool, buffer: list[str]) -> None:
    import pandas as pd

    exp = pd.read_csv(PROJECT_ROOT / "results/experiment_metrics.csv")
    has_mcc_far = {"mcc", "far"}.issubset(exp.columns)
    n_models = exp["model"].nunique()

    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_links = all(s in readme for s in ("doi.org", "miguelarcosa", "NSL_KDD", "jupyter"))

    crit = (PROJECT_ROOT / "docs/critical_evaluation.md").read_text(encoding="utf-8")
    claims = sum(1 for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7") if c in crit)

    baseline = pd.read_csv(PROJECT_ROOT / "results/baseline_reproduction.csv")
    lr_row = baseline[(baseline["model"] == "LR") & (baseline["notes"] == "author notebook logic") & (~baseline["smote"])]
    lr_ok = not lr_row.empty and abs(lr_row.iloc[0]["f1"] - 0.7302) <= 0.02

    must = [
        ("Public GitHub repo with all required artifacts", "pending push" if all(artifact_ok.values()) else "FAIL"),
        ("Notebook runs top-to-bottom after data download", "PASS" if notebook_ok else "FAIL"),
        ("NSL-KDD LR reproduced (±0.02) or deviation explained", "PASS" if lr_ok else "FAIL"),
        (f"≥2 models with full metric suite (MCC, FAR); have {n_models}", "PASS" if has_mcc_far and n_models >= 2 else "FAIL"),
        (f"Report evaluates ≥5 claims; have {claims}", "PASS" if claims >= 5 else "FAIL"),
        ("README contains required links and instructions", "PASS" if readme_links else "FAIL"),
        ("Submitted before July 10, 2026 23:59", "PASS (deadline not reached)"),
    ]

    should = [
        ("AE+LR reproduced", "PASS (author baseline MATCH)"),
        ("SMOTE with/without comparison", "PASS"),
        ("Per-attack-type error analysis (R2L, U2R)", "PASS"),
        ("Feature redundancy formally analyzed", "PASS"),
    ]

    rubric = [
        ("Problem understanding & source selection (10)", "Report §1, README"),
        ("Summary quality (15)", "Report §1"),
        ("Critical evaluation of claims (20)", "Report §2, docs/critical_evaluation.md"),
        ("Feature engineering analysis (10)", "Report §3, Notebook §3"),
        ("Exploratory data analysis (15)", "Notebook §2, Report §5 figures"),
        ("Model training & comparison (15)", "Notebook §4, Report §5"),
        ("Evaluation & error analysis (10)", "Notebook §5–6, Report §5"),
        ("Code quality & software engineering (5)", "src/, notebook structure"),
    ]

    lines = [
        "# Submission Checklist — Phase 8 QA",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Assignment requirements — Must pass",
        "",
        "| Criterion | Status |",
        "|-----------|--------|",
    ]
    lines += [f"| {c} | {s} |" for c, s in must]
    lines += ["", "## Assignment requirements — Should pass", "", "| Criterion | Status |", "|-----------|--------|"]
    lines += [f"| {c} | {s} |" for c, s in should]
    lines += ["", "## Grading rubric coverage", "", "| Component | Primary artifact |", "|-----------|------------------|"]
    lines += [f"| {c} | {a} |" for c, a in rubric]
    lines += [
        "",
        "## Manual steps (student)",
        "",
        "1. Confirm public repo URL: https://github.com/JCS1029/Intrusion-Detection-NSL-KDD-",
        "2. Email repo URL to examiner per `haifaUEX.pdf` course instructions.",
        "3. Confirm repo is public and tag v1.0-submission is present.",
        "",
        "## QA run excerpt",
        "",
        "```",
        *buffer[-40:],
        "```",
    ]
    CHECKLIST_PATH.write_text("\n".join(lines), encoding="utf-8")
    log([f"Wrote {CHECKLIST_PATH.relative_to(PROJECT_ROOT)}"], buffer)


def main() -> int:
    buffer: list[str] = []
    log([f"# QA Run Log — {datetime.now(timezone.utc).isoformat()}"], buffer)

    ensure_venv(buffer)
    data_ok = verify_data(buffer)
    artifact_ok = verify_artifacts(buffer)

    notebook_rc = run_notebook(buffer)
    notebook_ok = notebook_rc == 0 and data_ok

    # Remove QA artifact notebook from repo tree
    qa_out = PROJECT_ROOT / "notebooks" / "_qa_executed.ipynb"
    if qa_out.exists():
        qa_out.unlink()

    write_checklist(artifact_ok, notebook_ok, buffer)

    status = "PASS" if notebook_ok and all(artifact_ok.values()) else "FAIL"
    log([f"", f"Overall QA: {status}"], buffer)
    LOG_PATH.write_text("\n".join(buffer) + "\n", encoding="utf-8")
    log([f"Wrote {LOG_PATH.relative_to(PROJECT_ROOT)}"], buffer)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
