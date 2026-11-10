"""Starter map: biomedical concept NCI C-code -> (SDTM domain, --TESTCD).

This is a deliberately small seed covering common vital signs and chemistry
tests, where the BC code is the same NCI code as the SDTM CT test code.
Production use should load the full mapping from CDISC COSMoS BC/SDTM
dataset specializations (``--bc-map`` on the CLI accepts a YAML file).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .model import BcMap

DEFAULT_BC_MAP: dict[str, tuple[str, str]] = {
    # Vital signs (VSTESTCD codelist C66741)
    "C25298": ("VS", "SYSBP"),
    "C25299": ("VS", "DIABP"),
    "C49676": ("VS", "PULSE"),
    "C49677": ("VS", "HR"),
    "C25206": ("VS", "TEMP"),
    "C25208": ("VS", "WEIGHT"),
    "C25347": ("VS", "HEIGHT"),
    # Laboratory (LBTESTCD codelist C65047)
    "C64433": ("LB", "ALT"),
    "C64467": ("LB", "AST"),
    "C64431": ("LB", "ALB"),
    "C64432": ("LB", "ALP"),
    "C64547": ("LB", "CREAT"),
    "C64853": ("LB", "K"),
    "C64809": ("LB", "SODIUM"),
    "C64849": ("LB", "HBA1C"),
}


def load_bc_map(path: str | Path) -> dict[str, tuple[str, str]]:
    """Read ``{C-code: {domain: VS, testcd: SYSBP}}`` YAML into a map."""
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a mapping of C-code -> domain/testcd")
    out = {}
    for code, spec in raw.items():
        if not isinstance(spec, dict) or not spec.get("domain") or not spec.get("testcd"):
            raise ValueError(f"{path}: entry '{code}' needs 'domain' and 'testcd'")
        out[str(code)] = (str(spec["domain"]).upper(), str(spec["testcd"]).upper())
    return out


def merged(custom: BcMap | None) -> dict[str, tuple[str, str]]:
    """Built-in map overlaid with ``custom``; domain/testcd upper-cased."""
    extra = {str(code): (str(dom).upper(), str(test).upper())
             for code, (dom, test) in (custom or {}).items()}
    return {**DEFAULT_BC_MAP, **extra}
