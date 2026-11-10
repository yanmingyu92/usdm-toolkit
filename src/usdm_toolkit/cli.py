"""Command line interface for usdm-toolkit.

Usage:
    python -m usdm_toolkit.cli ct-align --yaml dataStructure.yml --ct USDM_CT.xlsx \
        --out report.md [--format md|json]
    python -m usdm_toolkit.cli trial-design --input usdm.json --out <dir>
    python -m usdm_toolkit.cli rules --input usdm.json [--rules-dir <dir>] \
        [--out report.md] [--format md|json]
"""

from __future__ import annotations

import argparse
import json
import sys

from .ct_align.checker import check, load_ct, load_yaml_model
from .ct_align.report import render_json, render_markdown
from .rules import engine as rules_engine
from .rules import report as rules_report
from .trial_design import generate_domains, write_domains


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="usdm-toolkit")
    sub = parser.add_subparsers(dest="command", required=True)

    ct_align = sub.add_parser(
        "ct-align",
        help="Check consistency between dataStructure.yml and USDM_CT.xlsx",
    )
    ct_align.add_argument("--yaml", dest="yaml_path", required=True,
                          help="Path to dataStructure.yml")
    ct_align.add_argument("--ct", dest="ct_path", required=True,
                          help="Path to USDM_CT.xlsx")
    ct_align.add_argument("--out", dest="out_path", default=None,
                          help="Output report path (default: stdout)")
    ct_align.add_argument("--format", choices=["md", "json"], default="md",
                          help="Report format (default: md)")

    trial_design = sub.add_parser(
        "trial-design",
        help="Generate SDTM Trial Design domain CSVs from a USDM JSON study",
    )
    trial_design.add_argument("--input", dest="input_path", required=True,
                              help="Path to a USDM JSON study file")
    trial_design.add_argument("--out", dest="out_dir", required=True,
                              help="Output directory for TS/TA/TE/TV/TI CSVs")

    rules = sub.add_parser(
        "rules",
        help="Run conformance rules against a USDM JSON study",
    )
    rules.add_argument("--input", dest="input_path", required=True,
                       help="Path to a USDM JSON study file")
    rules.add_argument("--rules-dir", dest="rules_dir", default=None,
                       help="Directory with YAML rule definitions "
                            "(default: bundled library)")
    rules.add_argument("--out", dest="out_path", default=None,
                       help="Output report path (default: stdout)")
    rules.add_argument("--format", choices=["md", "json"], default="md",
                       help="Report format (default: md)")

    trace = sub.add_parser(
        "trace-check",
        help="Check a USDM protocol against SDTM datasets for cross-artifact "
             "consistency",
    )
    trace.add_argument("--usdm", dest="usdm_path", required=True,
                       help="Path to a USDM v4 JSON study file")
    trace.add_argument("--sdtm", dest="sdtm_dir", required=True,
                       help="Folder of SDTM datasets (Dataset-JSON, CSV or XPT)")
    trace.add_argument("--bc-map", dest="bc_map_path", default=None,
                       help="YAML map of BC C-code -> {domain, testcd} "
                            "(added to the built-in starter map)")
    trace.add_argument("--out", dest="out_path", default=None,
                       help="Output path; .xlsx/.json/.md picks the format "
                            "(default: Markdown to stdout)")
    return parser


def _run_trace_check(args: argparse.Namespace) -> int:
    from .trace_check import run_trace_check
    from .trace_check import report as trace_report
    from .trace_check.bc_map import load_bc_map
    from .trace_check.loaders import scan_sdtm_dir

    try:
        with open(args.usdm_path, encoding="utf-8") as fh:
            usdm = json.load(fh)
        if not isinstance(usdm, dict):
            raise ValueError(f"{args.usdm_path}: not a USDM JSON object")
        sdtm, problems = scan_sdtm_dir(args.sdtm_dir)
        bc_map = load_bc_map(args.bc_map_path) if args.bc_map_path else None
    except (OSError, ValueError) as exc:  # JSONDecodeError is a ValueError
        print(f"trace-check: {exc}", file=sys.stderr)
        return 2
    for problem in problems:
        print(f"trace-check: {problem}", file=sys.stderr)

    report = run_trace_check(usdm, sdtm, bc_map=bc_map)
    sources = {"usdm_source": args.usdm_path, "sdtm_source": args.sdtm_dir}
    out = args.out_path
    if out and out.lower().endswith(".xlsx"):
        trace_report.write_xlsx(report, out, **sources)
    else:
        text = (trace_report.render_json(report)
                if out and out.lower().endswith(".json")
                else trace_report.render_markdown(report, **sources))
        if out:
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(text)
        else:
            print(text)
    s = report.summary()
    print(f"trace-check: {s['error']} error(s), {s['warning']} warning(s), "
          f"{s['info']} info; {len(sdtm)} dataset(s) loaded"
          + (f"; report written to {out}" if out else ""), file=sys.stderr)
    return 1 if report.error_count else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "ct-align":
        model = load_yaml_model(args.yaml_path)
        ct = load_ct(args.ct_path)
        findings = check(model, ct)
        if args.format == "json":
            output = render_json(findings)
        else:
            output = render_markdown(
                findings, yaml_source=args.yaml_path, ct_source=args.ct_path
            )
        if args.out_path:
            with open(args.out_path, "w", encoding="utf-8") as fh:
                fh.write(output)
            print(f"ct-align: {len(findings)} findings written to {args.out_path}",
                  file=sys.stderr)
        else:
            print(output)
        errors = sum(1 for f in findings if f.severity == "error")
        return 1 if errors else 0

    if args.command == "trial-design":
        with open(args.input_path, encoding="utf-8") as fh:
            usdm = json.load(fh)
        domains = generate_domains(usdm)
        written = write_domains(domains, args.out_dir)
        counts = ", ".join(f"{d}={len(r)}" for d, r in domains.items())
        print(f"trial-design: {counts} rows written to {args.out_dir} "
              f"({len(written)} files)", file=sys.stderr)
        return 0

    if args.command == "rules":
        with open(args.input_path, encoding="utf-8") as fh:
            usdm = json.load(fh)
        rules = rules_engine.load_rules(args.rules_dir)
        violations = rules_engine.run_rules(usdm, rules)
        if args.format == "json":
            output = rules_report.render_json(violations)
        else:
            output = rules_report.render_markdown(
                violations, rules, input_source=args.input_path
            )
        if args.out_path:
            with open(args.out_path, "w", encoding="utf-8") as fh:
                fh.write(output)
            print(f"rules: {len(violations)} violations written to {args.out_path}",
                  file=sys.stderr)
        else:
            print(output)
        errors = sum(1 for v in violations if v.severity == "error")
        return 1 if errors else 0

    if args.command == "trace-check":
        return _run_trace_check(args)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
