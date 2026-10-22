# Example USDM JSON files

Downloaded from the integration-test fixtures of the CDISC `usdm` reference
package (https://github.com/cdisc-org/usdm), branch `main`, package version
0.67.0, which implements **USDM model version 4.0.0** (each file also carries
`"usdmVersion": "4.0.0"`).

| File | Path in repo | Download date | Size (bytes) |
| --- | --- | --- | --- |
| `arms_epochs.json` | `tests/integration_test_files/arms_epochs.json` | 2026-10-22 | 73383 |
| `complex_1.json` | `tests/integration_test_files/complex_1.json` | 2026-10-22 | 201990 |
| `simple_1.json` | `tests/integration_test_files/simple_1.json` | 2026-10-22 | 233263 |
| `eligibility_criteria_1.json` | `tests/integration_test_files/eligibility_criteria_1.json` | 2026-10-22 | 130949 |

Raw URL pattern:

- https://raw.githubusercontent.com/cdisc-org/usdm/main/tests/integration_test_files/<name>.json

These files are test fixtures from the upstream package (synthetic study
definitions, not real protocols) and remain subject to the upstream license.
