"""Load and validate NSL-KDD train/test splits."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "KDDTrain+.txt"
DEFAULT_TEST_PATH = PROJECT_ROOT / "data" / "raw" / "KDDTest+.txt"

NSL_KDD_COLUMNS: list[str] = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "label",
    "difficulty",
]

CATEGORICAL_FEATURES = ["protocol_type", "service", "flag"]
BINARY_FEATURES = [
    "land",
    "logged_in",
    "root_shell",
    "su_attempted",
    "is_host_login",
    "is_guest_login",
]
NUMERIC_FEATURES = [
    c
    for c in NSL_KDD_COLUMNS
    if c not in CATEGORICAL_FEATURES + ["label", "difficulty"]
]

ATTACK_LABELS = {"normal", "neptune", "satan", "ipsweep", "portsweep", "nmap", "warezclient",
                 "warezmaster", "apache2", "back", "land", "mailbomb", "pod", "processtable",
                 "smurf", "teardrop", "udpstorm", "buffer_overflow", "loadmodule", "perl",
                 "ps", "rootkit", "guess_passwd", "ftp_write", "imap", "multihop", "phf",
                 "spy", "warezmaster", "warezclient", "sendmail", "named", "snmpgetattack",
                 "snmpguess", "xlock", "xsnoop", "worm", "httptunnel"}


def load_nsl_kdd(
    train_path: Path | str = DEFAULT_TRAIN_PATH,
    test_path: Path | str = DEFAULT_TEST_PATH,
    drop_difficulty: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load official NSL-KDD train/test files with canonical column names."""
    train_df = pd.read_csv(train_path, header=None, names=NSL_KDD_COLUMNS)
    test_df = pd.read_csv(test_path, header=None, names=NSL_KDD_COLUMNS)

    if drop_difficulty:
        train_df = train_df.drop(columns=["difficulty"])
        test_df = test_df.drop(columns=["difficulty"])

    return train_df, test_df


def add_binary_label(df: pd.DataFrame, label_col: str = "label") -> pd.DataFrame:
    """Add binary target: 0=normal, 1=attack."""
    out = df.copy()
    out["label_binary"] = (out[label_col].str.lower() != "normal").astype(int)
    return out


def attack_category(label: str) -> str:
    """Map NSL-KDD attack name to DoS / Probe / R2L / U2R family."""
    label = label.lower()
    if label == "normal":
        return "normal"
    dos = {"neptune", "smurf", "back", "teardrop", "pod", "land", "apache2", "udpstorm", "mailbomb", "processtable"}
    probe = {"satan", "ipsweep", "nmap", "portsweep", "mscan", "saint"}
    r2l = {"guess_passwd", "ftp_write", "imap", "phf", "multihop", "warezmaster", "warezclient",
           "spy", "xlock", "xsnoop", "snmpguess", "snmpgetattack", "sendmail", "named", "worm", "httptunnel"}
    u2r = {"buffer_overflow", "loadmodule", "rootkit", "perl", "sqlattack", "xterm", "ps"}
    if label in dos:
        return "dos"
    if label in probe:
        return "probe"
    if label in r2l:
        return "r2l"
    if label in u2r:
        return "u2r"
    return "other"


def summarize_dataset(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Return a one-row summary for train or test."""
    return pd.DataFrame(
        [{
            "split": name,
            "rows": len(df),
            "columns": df.shape[1],
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 2),
            "missing_total": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        }]
    )


def find_constant_columns(df: pd.DataFrame) -> list[str]:
    """Columns with a single unique value."""
    return [c for c in df.columns if df[c].nunique(dropna=False) <= 1]


def find_duplicate_feature_columns(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Exact duplicate feature pairs (excluding label columns)."""
    feature_cols = [c for c in df.columns if c not in ("label", "label_binary", "attack_category")]
    pairs: list[tuple[str, str]] = []
    for i, a in enumerate(feature_cols):
        for b in feature_cols[i + 1 :]:
            if df[a].equals(df[b]):
                pairs.append((a, b))
    return pairs
