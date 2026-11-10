# trace-check: protocol (USDM) ↔ SDTM cross-artifact checks

*Status: prototype (2026-11-10). Rules and thresholds will change.*

## Why

Conformance validators (CDISC CORE, Pinnacle 21) answer *"is this dataset a
valid SDTM dataset?"*. They do not answer *"does this dataset say the same
thing as the protocol?"*. Reviewers ask the second question. Those answers
end up in the reviewer's guide, and the inconsistencies are where information
requests start. With a machine-readable protocol (USDM v4, aligned with
ICH M11), that question can be checked automatically.

## How matching works

USDM has no SDTM short codes (ARMCD, ETCD, VISITNUM). Artifacts are therefore
linked by **labels**, in two steps:

1. Normalise both sides: lower-case, punctuation and underscores become spaces
   (`High - Start` = `HIGH_START`). Equal values are an exact match.
2. Otherwise apply a conservative fuzzy match (score ≥ 0.8):
   - character similarity, plus a prefix bonus (`Screen` ~ `Screening`) and a
     word-subset bonus (`Treatment` ~ `Treatment One`);
   - labels with **different numbers never match** (`Week 2` ≠ `Week 4`).

   Approximate matches are reported as info so a human can confirm them. EX
   treatment names are the exception: an approximate match there is reported
   as a warning, because it suggests a spelling inconsistency.

Pairing is one-to-one and greedy, best score first. Both the USDM `label` and
`name` are tried.

USDM narrative text is resolved before comparison: `<usdm:tag>` parameters go
through the SyntaxTemplateDictionary, and `<usdm:ref>` pulls the referenced
attribute. A tag that cannot be resolved is shown as `[name]`.

## Rule catalogue

| Rule | Severity | Checks |
|---|---|---|
| TC-TA-001 | error | Every protocol arm has rows in TA |
| TC-TA-002 | error | Every TA arm is a protocol arm |
| TC-TA-003 | warning | TA.EPOCH values ↔ protocol epochs |
| TC-TA-004 | warning | Element sequence per arm (TA by TAETORD) = protocol study cells |
| TC-TE-001 / 002 | warning | Protocol elements ↔ TE |
| TC-TV-001 / 002 | warning | Protocol encounters ↔ TV visits |
| TC-TI-001 | warning | Criteria correspond one-to-one, by category and number |
| TC-TI-002 | warning / info | TI text vs protocol text. A text that is an abbreviation (≥ 80% of TI's words are in the protocol text) is collapsed into one info finding |
| TC-TS-001 | warning / info | TITLE, TPHASE, TBLIND, PLANSUB, REGID, SPONSOR vs protocol. A missing parameter is info |
| TC-TS-002 | warning | TS OBJPRIM ↔ protocol primary objectives |
| TC-DM-001 | error | DM.ARM / ACTARM are protocol arms. Null-arm conventions (SCRNFAIL, NOTASSGN, NOTTRT, UNPLAN) are allowed |
| TC-DM-002 | info | Subjects whose actual arm differs from the planned arm |
| TC-SV-001 | warning | Scheduled SV visits are protocol encounters (UNSCHEDULED visits are ignored) |
| TC-SV-002 | warning | Each protocol encounter has SV records |
| TC-SE-001 | warning | SE elements are protocol elements |
| TC-EX-001 | warning | EX.EXTRT matches a protocol intervention or administrable product |
| TC-SOA-000 | info | Scheduled biomedical concepts with no SDTM mapping (not checked) |
| TC-SOA-001 | warning | Each scheduled test has records in its SDTM domain |
| TC-SOA-002 | warning | Each scheduled test has records at every planned visit |
| TC-SOA-003 | info | Test collected at visits the SoA does not schedule |

A rule is skipped, and listed in the report, when the datasets it needs are
not supplied.

## Known limitations (prototype)

- Only the first study version and the first study design are read.
- The BC → SDTM map is a 15-code starter. Production use needs the CDISC
  COSMoS dataset specializations.
- SoA checks use timeline instances that have an `encounterId`. Timing
  windows, conditional activities and sub-timelines are not yet interpreted.
- Matching is by label only. TV/SV `VISITNUM` and planned study days are not
  compared yet.
- Dataset-JSON v1.0 files with several item groups: only the first group is
  read.
- Label matching has guards against false pairings:
  - `Arm A` ≠ `Arm B`: labels that differ only in 1–2 letter words do not pair.
  - `Day -1` ≠ `Day 1`: the minus sign is kept.
  - `Week 2` ≠ `Week 4`: labels with different numbers do not pair.

  Even so, every approximate pairing is listed as info for a human to confirm.
- A rule that crashes on unexpected input is listed as skipped, with the error
  message; it does not stop the run. A file in the SDTM folder that is not a
  readable dataset (e.g. `define.json`) is skipped with a message.
- There are no ADaM, Define-XML or reviewer's-guide checks yet. These are next
  on the roadmap (USDM endpoints → ADaM PARAMCD; define.xml ↔ protocol
  version).
