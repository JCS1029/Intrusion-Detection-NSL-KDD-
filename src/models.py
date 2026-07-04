"""Model definitions and training utilities for NSL-KDD IDS."""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

from src.evaluation import compute_metrics
from src.preprocessing import PreprocessedData

RANDOM_STATE = 42
SKLEARN_MODEL_NAMES = ("NB", "LR", "LDA", "RF")
ALL_MODEL_NAMES = (*SKLEARN_MODEL_NAMES, "AE+LR")


@dataclass
class TrainResult:
    model: str
    smote: bool
    encoding: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    mcc: float
    far: float
    auc: float
    train_seconds: float
    infer_seconds: float
    tn: int
    fp: int
    fn: int
    tp: int
    model_path: str = ""
    notes: str = "our pipeline (train_only encoding)"

    def to_dict(self) -> dict:
        row = asdict(self)
        for key in ("accuracy", "precision", "recall", "f1", "mcc", "far", "auc"):
            row[key] = round(row[key], 4)
        row["train_seconds"] = round(row["train_seconds"], 3)
        row["infer_seconds"] = round(row["infer_seconds"], 3)
        return row


def set_sklearn_seed(seed: int = RANDOM_STATE) -> None:
    np.random.seed(seed)
    random.seed(seed)


def set_tensorflow_seed(seed: int = RANDOM_STATE) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    set_sklearn_seed(seed)
    import tensorflow as tf

    tf.random.set_seed(seed)
    try:
        tf.config.experimental.enable_op_determinism(True)
    except Exception:
        pass


def get_sklearn_models() -> dict[str, object]:
    """Return paper-aligned sklearn estimators plus Random Forest extension."""
    return {
        "NB": GaussianNB(),
        "LR": LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
        "LDA": LinearDiscriminantAnalysis(),
        "RF": RandomForestClassifier(
            n_estimators=100,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


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


def train_sklearn_model(
    model_name: str,
    estimator,
    data: PreprocessedData,
) -> tuple[TrainResult, object, np.ndarray, np.ndarray]:
    set_sklearn_seed()
    t0 = time.perf_counter()
    estimator.fit(data.X_train, data.y_train)
    train_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = estimator.predict(data.X_test)
    y_proba = estimator.predict_proba(data.X_test)[:, 1]
    infer_seconds = time.perf_counter() - t1

    metrics = compute_metrics(data.y_test, y_pred, y_proba)
    result = TrainResult(
        model=model_name,
        smote=data.smote_applied,
        encoding=data.encoding,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        **{k: metrics[k] for k in ("accuracy", "precision", "recall", "f1", "mcc", "far", "auc", "tn", "fp", "fn", "tp")},
    )
    return result, estimator, y_pred, y_proba


def train_ae_lr(data: PreprocessedData) -> tuple[TrainResult, dict, np.ndarray, np.ndarray]:
    set_tensorflow_seed()
    import tensorflow as tf

    tf.keras.backend.clear_session()

    autoencoder, encoder = build_autoencoder(data.X_train.shape[1])
    t0 = time.perf_counter()
    autoencoder.fit(
        data.X_train,
        data.X_train,
        epochs=20,
        batch_size=256,
        shuffle=False,
        validation_split=0.1,
        verbose=0,
    )
    x_train_emb = encoder.predict(data.X_train, verbose=0)
    x_test_emb = encoder.predict(data.X_test, verbose=0)

    clf = LogisticRegression(random_state=RANDOM_STATE, max_iter=1000)
    clf.fit(x_train_emb, data.y_train)
    train_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    y_pred = clf.predict(x_test_emb)
    y_proba = clf.predict_proba(x_test_emb)[:, 1]
    infer_seconds = time.perf_counter() - t1

    metrics = compute_metrics(data.y_test, y_pred, y_proba)
    artifact = {"autoencoder": autoencoder, "encoder": encoder, "classifier": clf}
    result = TrainResult(
        model="AE+LR",
        smote=data.smote_applied,
        encoding=data.encoding,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        **{k: metrics[k] for k in ("accuracy", "precision", "recall", "f1", "mcc", "far", "auc", "tn", "fp", "fn", "tp")},
    )
    return result, artifact, y_pred, y_proba


def _model_slug(model_name: str, smote: bool) -> str:
    smote_tag = "smote" if smote else "no_smote"
    return f"{model_name.replace('+', '_')}_{smote_tag}"


def save_sklearn_model(estimator, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimator, path)


def save_ae_lr_artifact(artifact: dict, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    artifact["autoencoder"].save(directory / "autoencoder.keras")
    artifact["encoder"].save(directory / "encoder.keras")
    joblib.dump(artifact["classifier"], directory / "classifier.joblib")


def save_predictions(
    path: Path,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, y_true=y_true, y_pred=y_pred, y_proba=y_proba)


def _relative_path(path: Path, prefix: Path | None) -> str:
    if prefix is None:
        return str(path)
    try:
        return str(path.relative_to(prefix))
    except ValueError:
        return str(path)


def train_all_models(
    data: PreprocessedData,
    *,
    save_dir: Path | None = None,
    predictions_dir: Path | None = None,
    include_rf: bool = True,
    path_prefix: Path | None = None,
) -> list[TrainResult]:
    """Train all required models on a preprocessed dataset."""
    results: list[TrainResult] = []
    sklearn_models = get_sklearn_models()
    model_names = list(SKLEARN_MODEL_NAMES) if include_rf else [n for n in SKLEARN_MODEL_NAMES if n != "RF"]

    for name in model_names:
        result, estimator, y_pred, y_proba = train_sklearn_model(name, sklearn_models[name], data)
        if save_dir is not None:
            model_path = save_dir / f"{_model_slug(name, data.smote_applied)}.joblib"
            save_sklearn_model(estimator, model_path)
            result.model_path = _relative_path(model_path, path_prefix)
        if predictions_dir is not None:
            pred_path = predictions_dir / f"{_model_slug(name, data.smote_applied)}.npz"
            save_predictions(pred_path, data.y_test, y_pred, y_proba)
        results.append(result)

    ae_result, ae_artifact, y_pred, y_proba = train_ae_lr(data)
    if save_dir is not None:
        ae_dir = save_dir / _model_slug("AE+LR", data.smote_applied)
        save_ae_lr_artifact(ae_artifact, ae_dir)
        ae_result.model_path = _relative_path(ae_dir, path_prefix)
    if predictions_dir is not None:
        pred_path = predictions_dir / f"{_model_slug('AE+LR', data.smote_applied)}.npz"
        save_predictions(pred_path, data.y_test, y_pred, y_proba)
    results.append(ae_result)

    return results


def compare_to_baseline(
    our_results: list[TrainResult],
    baseline_csv: Path,
    *,
    tolerance: float = 0.02,
) -> list[dict]:
    """Compare our metrics to author replication baseline (same model/SMOTE rows)."""
    import pandas as pd

    baseline = pd.read_csv(baseline_csv)
    author = baseline[baseline["notes"] == "author notebook logic"].copy()
    comparisons: list[dict] = []

    for result in our_results:
        row = author[(author["model"] == result.model) & (author["smote"] == result.smote)]
        if row.empty:
            continue
        ref = row.iloc[0]
        deltas = {
            metric: abs(getattr(result, metric) - ref[metric])
            for metric in ("accuracy", "precision", "recall", "f1", "far", "auc")
        }
        max_delta = max(deltas.values())
        comparisons.append(
            {
                "model": result.model,
                "smote": result.smote,
                "max_delta_vs_author": round(max_delta, 4),
                "status": "close" if max_delta <= tolerance else "diverged",
                "note": (
                    "Expected: our pipeline uses train-only encoding and drops correlated features"
                    if max_delta > tolerance
                    else "Within tolerance of author baseline"
                ),
                **{f"delta_{k}": round(v, 4) for k, v in deltas.items()},
            }
        )
    return comparisons


def save_training_log(results: list[TrainResult], path: Path):
    import pandas as pd

    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([r.to_dict() for r in results])
    df.to_csv(path, index=False)
    return df


def save_comparison(comparisons: list[dict], path: Path):
    import pandas as pd

    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(comparisons)
    df.to_csv(path, index=False)
    return df


def save_run_metadata(path: Path, metadata: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
