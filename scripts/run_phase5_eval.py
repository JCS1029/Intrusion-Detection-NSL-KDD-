"""Run evaluation and error analysis on saved model predictions."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "_venv_bootstrap", Path(__file__).resolve().parent / "_venv_bootstrap.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loading import add_binary_label, load_nsl_kdd
from src.evaluation import (
    build_experiment_metrics,
    compare_model_errors,
    error_by_attack_family,
    error_by_attack_label,
    load_all_predictions,
    save_evaluation_artifacts,
    smote_delta_table,
)

RESULTS_DIR = PROJECT_ROOT / "results"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
TRAINING_CSV = RESULTS_DIR / "model_training.csv"
MODELS = ["NB", "LR", "LDA", "RF", "AE+LR"]


def main() -> int:
    if not TRAINING_CSV.exists():
        print(f"Missing {TRAINING_CSV} — run training first.", file=sys.stderr)
        return 1

    print("Loading test labels for error analysis...")
    _, test_df = load_nsl_kdd()
    test_df = add_binary_label(test_df)

    print("Loading saved predictions...")
    predictions = load_all_predictions(PREDICTIONS_DIR, MODELS)
    if not predictions:
        print(f"No predictions in {PREDICTIONS_DIR}", file=sys.stderr)
        return 1

    metrics_df = build_experiment_metrics(TRAINING_CSV)
    save_evaluation_artifacts(test_df, predictions, metrics_df, RESULTS_DIR)

    print(f"\nSaved {RESULTS_DIR / 'experiment_metrics.csv'}")
    print(f"Figures under {RESULTS_DIR / 'figures' / 'eval'}")

    print("\n=== SMOTE delta (F1) ===")
    print(smote_delta_table(metrics_df).to_string(index=False))

    print("\n=== Error counts (no SMOTE) ===")
    print(compare_model_errors(test_df, predictions, smote=False).to_string(index=False))

    print("\n=== RF recall by attack family (no SMOTE) ===")
    rf = predictions.get(("RF", False))
    if rf is not None:
        print(error_by_attack_family(test_df, rf["y_pred"]).to_string(index=False))

    print("\n=== R2L/U2R per-label recall — LR (no SMOTE) ===")
    lr = predictions.get(("LR", False))
    if lr is not None:
        rare = error_by_attack_label(test_df, lr["y_pred"])
        print(rare.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
