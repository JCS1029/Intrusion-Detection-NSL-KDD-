"""
Phase 1: Reproduce author NSL-KDD baseline metrics from vendor notebook logic.

Mirrors vendor/IDS-KDD-CICIDS2017/data/BACK-nsl-kdd-github.ipynb
using bundled KDDTrain_cleaned_binary.csv / KDDTest_cleaned_binary.csv.
"""

from __future__ import annotations

import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "_venv_bootstrap", Path(__file__).resolve().parent / "_venv_bootstrap.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import MinMaxScaler

# TensorFlow imported lazily in AE paths (after env seeds)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "vendor" / "IDS-KDD-CICIDS2017" / "data"
TRAIN_CSV = DATA_DIR / "KDDTrain_cleaned_binary.csv"
TEST_CSV = DATA_DIR / "KDDTest_cleaned_binary.csv"
OUTPUT_CSV = PROJECT_ROOT / "results" / "baseline_reproduction.csv"


@dataclass
class RunResult:
    dataset: str
    model: str
    smote: bool
    accuracy: float
    precision: float
    recall: float
    f1: float
    far: float
    auc: float
    train_seconds: float
    infer_seconds: float
    tn: int
    fp: int
    fn: int
    tp: int
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "dataset": self.dataset,
            "model": self.model,
            "smote": self.smote,
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "far": round(self.far, 4),
            "auc": round(self.auc, 4),
            "train_seconds": round(self.train_seconds, 3),
            "infer_seconds": round(self.infer_seconds, 3),
            "tn": self.tn,
            "fp": self.fp,
            "fn": self.fn,
            "tp": self.tp,
            "notes": self.notes,
        }


def set_sklearn_seed() -> None:
    np.random.seed(42)
    random.seed(42)


def set_tensorflow_seed() -> None:
    os.environ["PYTHONHASHSEED"] = "42"
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    set_sklearn_seed()
    import tensorflow as tf

    tf.random.set_seed(42)
    try:
        tf.config.experimental.enable_op_determinism(True)
    except Exception:
        pass


def load_preprocessed_splits() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Match author notebook: concat train+test for one-hot, scale on train."""
    train_df = pd.read_csv(TRAIN_CSV)
    test_df = pd.read_csv(TEST_CSV)

    x_train = train_df.iloc[:, :-1]
    y_train = train_df.iloc[:, -1].to_numpy()
    x_test = test_df.iloc[:, :-1]
    y_test = test_df.iloc[:, -1].to_numpy()

    x_all = pd.concat([x_train, x_test], axis=0)
    x_all_encoded = pd.get_dummies(x_all, drop_first=True)
    x_train_encoded = x_all_encoded.iloc[: len(x_train), :].to_numpy()
    x_test_encoded = x_all_encoded.iloc[len(x_train) :, :].to_numpy()

    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train_encoded)
    x_test_scaled = scaler.transform(x_test_encoded)
    return x_train_scaled, y_train, x_test_scaled, y_test


def compute_metrics(y_test: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> dict:
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    far = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "auc": roc_auc_score(y_test, y_proba),
        "far": far,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def run_sklearn_model(
    model_name: str,
    estimator,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    smote: bool,
) -> RunResult:
    set_sklearn_seed()
    x_tr, y_tr = x_train, y_train
    if smote:
        x_tr, y_tr = SMOTE(random_state=42).fit_resample(x_train, y_train)

    t0 = time.perf_counter()
    estimator.fit(x_tr, y_tr)
    train_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = estimator.predict(x_test)
    y_proba = estimator.predict_proba(x_test)[:, 1]
    infer_seconds = time.perf_counter() - t1

    m = compute_metrics(y_test, y_pred, y_proba)
    return RunResult(
        dataset="NSL-KDD",
        model=model_name,
        smote=smote,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        notes="author notebook logic",
        **m,
    )


def build_autoencoder(input_dim: int):
    from tensorflow.keras.layers import Dense, Input
    from tensorflow.keras.models import Model
    from tensorflow.keras.optimizers import Adam

    encoding_dim = 32
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(64, activation="relu")(input_layer)
    encoded = Dense(encoding_dim, activation="relu")(encoded)
    decoded = Dense(64, activation="relu")(encoded)
    output_layer = Dense(input_dim, activation="sigmoid")(decoded)

    autoencoder = Model(inputs=input_layer, outputs=output_layer)
    encoder = Model(inputs=input_layer, outputs=encoded)
    autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
    return autoencoder, encoder


def run_ae_lr(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    smote: bool,
) -> RunResult:
    set_tensorflow_seed()
    import tensorflow as tf

    tf.keras.backend.clear_session()

    autoencoder, encoder = build_autoencoder(x_train.shape[1])
    t0 = time.perf_counter()
    autoencoder.fit(
        x_train,
        x_train,
        epochs=20,
        batch_size=256,
        shuffle=False,
        validation_split=0.1,
        verbose=0,
    )
    x_train_emb = encoder.predict(x_train, verbose=0)
    x_test_emb = encoder.predict(x_test, verbose=0)

    x_tr, y_tr = x_train_emb, y_train
    if smote:
        x_tr, y_tr = SMOTE(random_state=42).fit_resample(x_train_emb, y_train)

    clf = LogisticRegression(random_state=42, max_iter=1000)
    clf.fit(x_tr, y_tr)
    train_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = clf.predict(x_test_emb)
    y_proba = clf.predict_proba(x_test_emb)[:, 1]
    infer_seconds = time.perf_counter() - t1

    m = compute_metrics(y_test, y_pred, y_proba)
    return RunResult(
        dataset="NSL-KDD",
        model="AE+LR",
        smote=smote,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        notes="author notebook logic",
        **m,
    )


PAPER_TABLE4 = [
    RunResult("NSL-KDD", "NB", False, 0.5649, 0.9800, 0.2406, 0.3864, 0.0065, 0.7987, 0, 0, 0, 0, 0, 0, "paper Table 4"),
    RunResult("NSL-KDD", "LR", False, 0.7443, 0.9142, 0.6079, 0.7302, 0.0754, 0.8276, 0, 0, 0, 0, 0, 0, "paper Table 4"),
    RunResult("NSL-KDD", "LDA", False, 0.7616, 0.9249, 0.6326, 0.7514, 0.0679, 0.8484, 0, 0, 0, 0, 0, 0, "paper Table 4"),
    RunResult("NSL-KDD", "AE+LR", False, 0.7616, 0.9165, 0.6397, 0.7534, 0.0770, 0.9040, 0, 0, 0, 0, 0, 0, "paper Table 4"),
]

PAPER_TABLE5 = [
    RunResult("NSL-KDD", "NB", True, 0.5650, 0.9800, 0.2408, 0.3866, 0.0065, 0.7978, 0, 0, 0, 0, 0, 0, "paper Table 5"),
    RunResult("NSL-KDD", "LR", True, 0.7458, 0.9137, 0.6112, 0.7324, 0.0763, 0.8227, 0, 0, 0, 0, 0, 0, "paper Table 5"),
    RunResult("NSL-KDD", "LDA", True, 0.7632, 0.9238, 0.6365, 0.7537, 0.0694, 0.8525, 0, 0, 0, 0, 0, 0, "paper Table 5"),
    RunResult("NSL-KDD", "AE+LR", True, 0.7654, 0.9166, 0.6467, 0.7583, 0.0778, 0.9043, 0, 0, 0, 0, 0, 0, "paper Table 5"),
]


def main() -> int:
    if not TRAIN_CSV.exists() or not TEST_CSV.exists():
        print(f"Missing data in {DATA_DIR}", file=sys.stderr)
        return 1

    print("Loading preprocessed NSL-KDD CSVs from author repo...")
    x_train, y_train, x_test, y_test = load_preprocessed_splits()
    print(f"Train shape: {x_train.shape}, Test shape: {x_test.shape}")

    results: list[RunResult] = []

    print("\n--- Without SMOTE ---")
    for name, est in [
        ("NB", GaussianNB()),
        ("LR", LogisticRegression(random_state=42, max_iter=1000)),
        ("LDA", LinearDiscriminantAnalysis()),
    ]:
        print(f"Running {name}...")
        r = run_sklearn_model(name, est, x_train, y_train, x_test, y_test, smote=False)
        results.append(r)
        print(f"  Acc={r.accuracy:.4f} F1={r.f1:.4f} AUC={r.auc:.4f}")

    print("Running AE+LR...")
    r_ae = run_ae_lr(x_train, y_train, x_test, y_test, smote=False)
    results.append(r_ae)
    print(f"  Acc={r_ae.accuracy:.4f} F1={r_ae.f1:.4f} AUC={r_ae.auc:.4f}")

    print("\n--- With SMOTE (train only) ---")
    for name, est in [
        ("NB", GaussianNB()),
        ("LR", LogisticRegression(random_state=42, max_iter=1000)),
        ("LDA", LinearDiscriminantAnalysis()),
    ]:
        print(f"Running {name} + SMOTE...")
        r = run_sklearn_model(name, est, x_train, y_train, x_test, y_test, smote=True)
        results.append(r)
        print(f"  Acc={r.accuracy:.4f} F1={r.f1:.4f} AUC={r.auc:.4f}")

    print("Running AE+LR + SMOTE...")
    r_ae_s = run_ae_lr(x_train, y_train, x_test, y_test, smote=True)
    results.append(r_ae_s)
    print(f"  Acc={r_ae_s.accuracy:.4f} F1={r_ae_s.f1:.4f} AUC={r_ae_s.auc:.4f}")

    rows = [r.to_dict() for r in results]
    rows.extend([r.to_dict() for r in PAPER_TABLE4])
    rows.extend([r.to_dict() for r in PAPER_TABLE5])

    df = pd.DataFrame(rows)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {OUTPUT_CSV}")

    # Comparison summary
    ours = df[df["notes"] == "author notebook logic"].copy()
    paper = df[df["notes"].str.startswith("paper")].copy()
    print("\n=== Delta vs paper (|ours - paper|) ===")
    for smote_flag in [False, True]:
        label = "with SMOTE" if smote_flag else "no SMOTE"
        print(f"\n{label}:")
        o = ours[ours["smote"] == smote_flag]
        p = paper[paper["smote"] == smote_flag]
        for model in ["NB", "LR", "LDA", "AE+LR"]:
            o_row = o[o["model"] == model].iloc[0]
            p_row = p[p["model"] == model].iloc[0]
            deltas = {
                m: abs(o_row[m] - p_row[m])
                for m in ["accuracy", "precision", "recall", "f1", "far", "auc"]
            }
            max_d = max(deltas.values())
            status = "MATCH" if max_d <= 0.02 else ("CLOSE" if max_d <= 0.05 else "DRIFT")
            print(f"  {model}: max_delta={max_d:.4f} -> {status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
