"""Minimal conformance-rule executor for USDM JSON instances.

Rules are defined in YAML files with the fields:

- ``id``          unique rule identifier, e.g. ``USDM-REQ-001``
- ``description`` human-readable statement of the constraint
- ``severity``    ``error`` | ``warning`` | ``info``
- ``scope``       USDM ``instanceType`` the rule applies to (e.g. ``StudyArm``)
- ``expression``  a JSONata boolean expression evaluated against each matching
                  node; a falsy / undefined result is a violation

The executor walks the JSON tree, collects every object whose
``instanceType`` equals ``scope``, and evaluates the JSONata expression on
each node in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import yaml

try:
    import jsonata
except ImportError:  # pragma: no cover - dependency is declared
    jsonata = None

DEFAULT_RULES_DIR = Path(__file__).parent / "library"


@dataclass
class Rule:
    id: str
    description: str
    severity: str
    scope: str
    expression: str
    source_file: str = ""


@dataclass
class Violation:
    rule_id: str
    severity: str
    description: str
    node_type: str
    node_id: str
    detail: str = ""


def load_rules(rules_dir: str | Path | None = None) -> list[Rule]:
    """Load all rule definitions from ``*.yml`` / ``*.yaml`` files in a dir.

    Each file may contain a single rule mapping or a ``rules:`` list.
    Defaults to the bundled rule library.
    """
    directory = Path(rules_dir) if rules_dir else DEFAULT_RULES_DIR
    rules: list[Rule] = []
    for path in sorted(directory.glob("*.y*ml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        entries = doc.get("rules", []) if isinstance(doc, dict) and "rules" in doc else [doc]
        for entry in entries:
            rules.append(Rule(
                id=entry["id"],
                description=entry.get("description", ""),
                severity=entry.get("severity", "error"),
                scope=entry["scope"],
                expression=entry["expression"],
                source_file=path.name,
            ))
    return rules


def _walk(node: Any) -> Iterator[dict]:
    """Yield every dict in the tree that carries an ``instanceType``."""
    if isinstance(node, dict):
        if isinstance(node.get("instanceType"), str):
            yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item)


def run_rules(usdm: dict, rules: list[Rule]) -> list[Violation]:
    """Evaluate rules against a USDM JSON instance; return violations."""
    if jsonata is None:
        raise RuntimeError(
            "jsonata-python is not installed; the rules module requires it."
        )
    nodes = list(_walk(usdm))
    violations: list[Violation] = []
    for rule in rules:
        compiled = jsonata.Jsonata(rule.expression)
        for node in nodes:
            if node.get("instanceType") != rule.scope:
                continue
            try:
                result = compiled.evaluate(node)
            except Exception as exc:  # JSONata runtime error on this node
                violations.append(Violation(
                    rule_id=rule.id, severity=rule.severity,
                    description=rule.description,
                    node_type=rule.scope, node_id=str(node.get("id", "?")),
                    detail=f"expression error: {exc}",
                ))
                continue
            if not result:
                violations.append(Violation(
                    rule_id=rule.id, severity=rule.severity,
                    description=rule.description,
                    node_type=rule.scope, node_id=str(node.get("id", "?")),
                    detail=f"expression evaluated to {result!r}",
                ))
    return violations
