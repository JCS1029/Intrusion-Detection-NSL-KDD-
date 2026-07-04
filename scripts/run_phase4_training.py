"""Train all IDS models on our preprocessing pipeline and compare to author baseline."""

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
from src.models import (
    compare_to_baseline,
    save_comparison,
    save_run_metadata,
    save_training_log,
    train_all_models,
)
from src.preprocessing import preprocess_nsl_kdd

RESULTS_DIR = PROJECT_ROOT / "results"
MODELS_DIR = RESULTS_DIR / "models"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
BASELINE_CSV = RESULTS_DIR / "baseline_reproduction.csv"


def main() -> int:
    print("Loading raw NSL-KDD...")
    train_df, test_df = load_nsl_kdd()
    train_df = add_binary_label(train_df)
    test_df = add_binary_label(test_df)

    all_results = []
    comparisons = []

    for smote in (False, True):
        label = "with SMOTE" if smote else "without SMOTE"
        print(f"\n=== Training {label} (train_only encoding) ===")
        data = preprocess_nsl_kdd(
            train_df,
            test_df,
            encoding="train_only",
            apply_smote=smote,
        )
        print(f"  Features: {len(data.feature_names)}, train shape: {data.X_train.shape}")

        results = train_all_models(
            data,
            save_dir=MODELS_DIR,
            predictions_dir=PREDICTIONS_DIR,
            include_rf=True,
            path_prefix=PROJECT_ROOT,
        )
        for r in results:
            print(
                f"  {r.model}: Acc={r.accuracy:.4f} F1={r.f1:.4f} "
                f"AUC={r.auc:.4f} train={r.train_seconds:.1f}s"
            )
        all_results.extend(results)
        comparisons.extend(compare_to_baseline(results, BASELINE_CSV))

    training_csv = RESULTS_DIR / "model_training.csv"
    comparison_csv = RESULTS_DIR / "baseline_comparison.csv"
    save_training_log(all_results, training_csv)
    save_comparison(comparisons, comparison_csv)
    save_run_metadata(
        RESULTS_DIR / "model_training_metadata.json",
        {
            "encoding": "train_only",
            "models": ["NB", "LR", "LDA", "RF", "AE+LR"],
            "smote_regimes": [False, True],
            "random_state": 42,
            "models_dir": str(MODELS_DIR),
            "predictions_dir": str(PREDICTIONS_DIR),
        },
    )

    print(f"\nSaved {training_csv}")
    print(f"Saved {comparison_csv}")
    print(f"Models saved under {MODELS_DIR}")

    print("\n=== Divergence vs author baseline ===")
    for row in comparisons:
        print(
            f"  {row['model']} (smote={row['smote']}): "
            f"max_delta={row['max_delta_vs_author']:.4f} -> {row['status']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
