from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


@lru_cache(maxsize=None)
def load_data(name: str) -> Any:
    """Load JSON or CSV data from the assets directory.

    Parameters
    ----------
    name: str
        Filename within the assets directory. The extension is optional; if
        omitted, ``.json`` is tried first, then ``.csv``.
    Returns
    -------
    Any
        Parsed data structure. JSON files return ``dict`` or ``list`` objects
        depending on their content, while CSV files return a list of rows.
    """
    path = ASSETS_DIR / name
    if path.suffix == "":
        json_path = path.with_suffix(".json")
        csv_path = path.with_suffix(".csv")
        if json_path.exists():
            path = json_path
        elif csv_path.exists():
            path = csv_path
        else:
            raise FileNotFoundError(f"Asset file '{name}' not found")

    if path.suffix == ".json":
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            return [row for row in csv.reader(f)]
    raise ValueError(f"Unsupported file type: {path.suffix}")
