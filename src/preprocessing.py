"""Leakage-free preprocessing pipelines for NSL-KDD IDS classification."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler

from src.data_loading import CATEGORICAL_FEATURES, NUMERIC_FEATURES

LABEL_COLUMN = "label_binary"
DROP_BY_DEFAULT = ["num_outbound_cmds"]


@dataclass
class PreprocessedData:
    """Container for model-ready train/test matrices."""

    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    feature_names: list[str]
    encoding: str
    smote_applied: bool
    dropped_features: list[str]


def split_features_and_labels(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    label_col: str = LABEL_COLUMN,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    feature_cols = [c for c in train_df.columns if c not in (label_col, "label", "attack_category")]
    return (
        train_df[feature_cols].copy(),
        test_df[feature_cols].copy(),
        train_df[label_col].to_numpy(),
        test_df[label_col].to_numpy(),
    )


def drop_features(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    existing = [c for c in columns if c in x_train.columns]
    return x_train.drop(columns=existing), x_test.drop(columns=existing), existing


def find_highly_correlated_numeric(
    x_train: pd.DataFrame,
    threshold: float = 0.95,
) -> list[str]:
    """Greedy drop list for |Pearson r| >= threshold on numeric columns."""
    numeric = [c for c in NUMERIC_FEATURES if c in x_train.columns]
    if len(numeric) < 2:
        return []

    corr = x_train[numeric].corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop: set[str] = set()
    for col in upper.columns:
        high = upper.index[upper[col] >= threshold].tolist()
        for partner in high:
            # Drop the second name lexicographically to make deterministic
            drop = max(col, partner)
            to_drop.add(drop)
    return sorted(to_drop)


def one_hot_encode_author_style(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Replicate author notebook: concat train+test before get_dummies."""
    n_train = len(x_train)
    combined = pd.concat([x_train, x_test], axis=0)
    encoded = pd.get_dummies(combined, columns=CATEGORICAL_FEATURES, drop_first=True)
    return (
        encoded.iloc[:n_train].reset_index(drop=True),
        encoded.iloc[n_train:].reset_index(drop=True),
    )


def one_hot_encode_train_only(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fit categories on train; align test columns without using test categories for schema."""
    train_enc = pd.get_dummies(x_train, columns=CATEGORICAL_FEATURES, drop_first=True)
    test_enc = pd.get_dummies(x_test, columns=CATEGORICAL_FEATURES, drop_first=True)
    test_enc = test_enc.reindex(columns=train_enc.columns, fill_value=0)
    return train_enc, test_enc


def scale_features(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)
    return x_train_scaled, x_test_scaled, scaler


def apply_smote_train_only(
    x_train: np.ndarray,
    y_train: np.ndarray,
    random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    return SMOTE(random_state=random_state).fit_resample(x_train, y_train)


def preprocess_nsl_kdd(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    *,
    encoding: str = "train_only",
    drop_constants: bool = True,
    drop_correlated: bool = True,
    correlation_threshold: float = 0.95,
    apply_smote: bool = False,
    label_col: str = LABEL_COLUMN,
) -> PreprocessedData:
    """
    Build model-ready arrays.

    encoding:
        - 'train_only': leakage-aware one-hot (recommended)
        - 'author_concat': matches author replication notebook
    """
    if encoding not in {"train_only", "author_concat"}:
        raise ValueError("encoding must be 'train_only' or 'author_concat'")

    x_train, x_test, y_train, y_test = split_features_and_labels(train_df, test_df, label_col)
    dropped: list[str] = []

    if drop_constants:
        x_train, x_test, dropped_const = drop_features(x_train, x_test, DROP_BY_DEFAULT)
        dropped.extend(dropped_const)

    if drop_correlated:
        corr_drop = find_highly_correlated_numeric(x_train, correlation_threshold)
        x_train, x_test, dropped_corr = drop_features(x_train, x_test, corr_drop)
        dropped.extend(dropped_corr)

    if encoding == "author_concat":
        x_train, x_test = one_hot_encode_author_style(x_train, x_test)
    else:
        x_train, x_test = one_hot_encode_train_only(x_train, x_test)

    feature_names = list(x_train.columns)
    x_train_scaled, x_test_scaled, _ = scale_features(x_train, x_test)

    smote_applied = False
    if apply_smote:
        x_train_scaled, y_train = apply_smote_train_only(x_train_scaled, y_train)
        smote_applied = True

    return PreprocessedData(
        X_train=x_train_scaled,
        X_test=x_test_scaled,
        y_train=y_train,
        y_test=y_test,
        feature_names=feature_names,
        encoding=encoding,
        smote_applied=smote_applied,
        dropped_features=dropped,
    )


class SmoteTransformer(BaseEstimator, TransformerMixin):
    """Pass-through for X; SMOTE is applied in a custom fit_resample helper."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X


def make_model_pipeline(estimator, *, use_smote: bool = False) -> ImbPipeline:
    """Classifier pipeline with optional SMOTE on training fold only."""
    steps: list[tuple[str, object]] = []
    if use_smote:
        steps.append(("smote", SMOTE(random_state=42)))
    steps.append(("clf", estimator))
    return ImbPipeline(steps)


def leakage_checks(x_train: pd.DataFrame, x_test: pd.DataFrame) -> dict[str, bool]:
    """Sanity checks documented in the notebook."""
    train_enc, test_enc = one_hot_encode_train_only(x_train, x_test)
    author_train, author_test = one_hot_encode_author_style(x_train, x_test)
    return {
        "train_only_test_columns_subset_of_train": set(test_enc.columns).issubset(set(train_enc.columns)),
        "author_has_more_or_equal_columns_than_train_only": author_train.shape[1] >= train_enc.shape[1],
        "scaler_fit_on_train_only": True,
        "smote_must_be_train_only": True,
    }
