"""Clean notebook: remove empty cells, verify structure."""
import json
from pathlib import Path

NOTEBOOK = Path("notebooks/ids_nsl_kdd_analysis.ipynb")


def is_empty(cell: dict) -> bool:
    src = "".join(cell.get("source", [])).strip()
    if cell["cell_type"] == "markdown":
        return not src
    if cell["cell_type"] == "code":
        return not src and not cell.get("outputs")
    return False


def main() -> None:
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    before = len(nb["cells"])
    nb["cells"] = [c for c in nb["cells"] if not is_empty(c)]
    removed = before - len(nb["cells"])

    NOTEBOOK.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Cleaned {NOTEBOOK}: removed {removed} empty cells ({len(nb['cells'])} cells remain)")


if __name__ == "__main__":
    main()
