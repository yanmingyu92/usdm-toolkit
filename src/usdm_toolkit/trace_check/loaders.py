"""Read SDTM datasets: Dataset-JSON (v1.0 / v1.1), CSV, and XPT (optional).

Every loader returns ``(DATASET_NAME, rows)`` where rows is a tuple of dicts
keyed by variable name. XPT needs ``pandas`` (``pip install usdm-toolkit[xpt]``).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .model import Rows

SUPPORTED_SUFFIXES = (".json", ".csv", ".xpt")
_SEQ_COLUMN = "ITEMGROUPDATASEQ"


def load_dataset(path: str | Path) -> tuple[str, Rows]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".json":
        return _load_dataset_json(p)
    if suffix == ".csv":
        return p.stem.upper(), _load_csv(p)
    if suffix == ".xpt":
        return p.stem.upper(), _load_xpt(p)
    raise ValueError(f"{p}: unsupported dataset format '{suffix}'")


def scan_sdtm_dir(directory: str | Path) -> tuple[dict[str, Rows], tuple[str, ...]]:
    """Load every readable dataset in a folder (non-recursive).

    Returns ``(datasets, problems)``. A file that is not a readable dataset
    (e.g. ``define.json``) is listed in ``problems`` instead of aborting.
    If a domain exists in several formats, the first by SUPPORTED_SUFFIXES
    order wins (Dataset-JSON, then CSV, then XPT).
    """
    d = Path(directory)
    if not d.is_dir():
        raise ValueError(f"{d}: not a directory")
    out: dict[str, Rows] = {}
    problems: list[str] = []
    for suffix in SUPPORTED_SUFFIXES:
        for path in sorted(d.glob(f"*{suffix}")):
            try:
                name, rows = load_dataset(path)
            except ValueError as exc:
                problems.append(f"skipped {path.name}: {exc}")
                continue
            out.setdefault(name.upper(), rows)
    return out, tuple(problems)


def load_sdtm_dir(directory: str | Path) -> dict[str, Rows]:
    """Like :func:`scan_sdtm_dir` but returns only the datasets."""
    return scan_sdtm_dir(directory)[0]


def _load_dataset_json(p: Path) -> tuple[str, Rows]:
    try:
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{p}: invalid JSON ({exc.msg} at line {exc.lineno})") from exc
    if not isinstance(doc, dict):
        raise ValueError(f"{p}: not a Dataset-JSON object")

    if "columns" in doc and "rows" in doc:  # Dataset-JSON v1.1
        cols = [c.get("name") if isinstance(c, dict) else str(c)
                for c in doc["columns"] or []]
        name = doc.get("name") or doc.get("itemGroupOID") or p.stem
        return str(name).upper(), _to_dicts(cols, doc["rows"])

    for block in ("clinicalData", "referenceData"):  # Dataset-JSON v1.0
        groups = (doc.get(block) or {}).get("itemGroupData") or {}
        for oid, group in groups.items():
            cols = [i.get("name") for i in group.get("items", [])]
            name = group.get("name") or oid.split(".")[-1]
            return str(name).upper(), _to_dicts(cols, group.get("itemData", []))
    raise ValueError(f"{p}: no Dataset-JSON v1.0/v1.1 content found")


def _to_dicts(cols: list[str], records: list[list]) -> Rows:
    out = []
    for rec in records or []:
        if not isinstance(rec, list):
            raise ValueError("Dataset-JSON rows must be arrays")
        row = dict(zip(cols, rec))
        row.pop(_SEQ_COLUMN, None)
        out.append(row)
    return tuple(out)


def _load_csv(p: Path) -> Rows:
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return tuple(dict(r) for r in csv.DictReader(fh))


def _load_xpt(p: Path) -> Rows:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ValueError(
            f"{p}: reading XPT needs pandas (pip install pandas), "
            "or convert the dataset to Dataset-JSON/CSV") from exc
    frame = pd.read_sas(p, format="xport", encoding="latin-1")
    frame = frame.astype(object).where(frame.notna(), None)
    return tuple(frame.to_dict(orient="records"))
