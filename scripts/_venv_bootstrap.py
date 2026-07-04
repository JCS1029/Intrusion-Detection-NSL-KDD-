"""Re-launch the current script with the project virtualenv when available."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def ensure_project_venv() -> None:
    """If `.venv` exists and we're not already using it, re-run with venv Python."""
    project_root = Path(__file__).resolve().parents[1]
    if os.name == "nt":
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_root / ".venv" / "bin" / "python"

    if not venv_python.exists():
        return

    try:
        same = Path(sys.executable).resolve() == venv_python.resolve()
    except OSError:
        same = False

    if same:
        return

    print(f"Using project venv: {venv_python}", flush=True)
    result = subprocess.run([str(venv_python), *sys.argv])
    raise SystemExit(result.returncode)


ensure_project_venv()
