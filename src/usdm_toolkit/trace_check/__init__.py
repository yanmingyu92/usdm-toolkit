"""trace_check: cross-artifact consistency between a USDM protocol and SDTM data.

Conformance validators (CDISC CORE, Pinnacle 21) check each standard on its
own. trace-check checks that the artifacts agree with each other: protocol
arms, epochs, elements, visits, criteria, objectives and the Schedule of
Activities against TA/TE/TV/TI/TS and subject-level DM/SV/SE/EX/findings data.
"""

from .engine import ALL_RULES, run_trace_check
from .model import Finding, RuleSpec, TraceReport

__all__ = ["ALL_RULES", "Finding", "RuleSpec", "TraceReport", "run_trace_check"]
