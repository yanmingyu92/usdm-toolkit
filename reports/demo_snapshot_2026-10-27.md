# Demo Snapshot — 2026-10-27 DDF SME Meeting（静态备份）

> 用途：2026-10-27 DDF 双周 SME 会议 5 分钟 demo 的**静态备份**。
> 若 Teams 屏幕共享失败或现场网络/环境出问题，直接共享本文件即可讲完核心内容。
> 所有数字均为 2026-10-22 在本机实测真实输出（Windows + Git Bash + `.venv`）。
>
> 生成命令（全部实测通过）：
>
> ```bash
> cd "C:/Users/JaimeYan/OneDrive - Kardigan/personal_testing/clinivista_docker/usdm-toolkit"
> source .venv/Scripts/activate
> python -m usdm_toolkit.cli ct-align --yaml data/source/dataStructure.yml --ct data/source/USDM_CT.xlsx --out reports/demo_ct_align.md --format md
> python -m usdm_toolkit.cli trial-design --input data/examples/complex_1.json --out reports/demo_trial_design
> python -m usdm_toolkit.cli rules --input data/examples/complex_1.json --out reports/demo_rules_complex_1.md --format md
> ```

---

## 1. ct-align：模型 vs. 受控术语一致性（v4.0.0 deliverables）

**一句话结果：全自动复现 DDF-RA issue #716 报告的全部 27 处 mismatch（27/27），并额外发现 7 条 issue 中未提及的 value-list 类型不一致。**

实测终端输出：

```
ct-align: 263 findings written to reports/demo_ct_align.md
```

（exit code = 1，属预期行为：存在 error 级 findings 时返回 1，方便接 CI。全程约 1.7 秒。）

Summary by rule（摘自 `reports/demo_ct_align.md`）：

| Rule | Severity | Count |
| --- | --- | --- |
| `CLASS_NOT_IN_CT` | warning | 2 |
| `ATTR_CCODE_MISMATCH` | error | 27 |
| `ATTR_TERM_MISMATCH` | error | 27 |
| `ATTR_DEFINITION_MISMATCH` | error | 27 |
| `CT_ATTR_NOT_IN_YAML` | info | 172 |
| `CLASSIFICATION_WITHOUT_VALUE_LIST` | warning | 1 |
| `VALUE_LIST_TYPE_MISMATCH` | warning | 7 |
| **Total** | | **263** |

与 issue 的对照（详见 `reports/ct_align_report_2026-10-22.md`）：

- **#716**：27 个 attribute 的 C-code / preferred term / definition mismatch，工具逐条复现（27/27），且每条都自动指出"YAML 里的 code 实际属于 CT 中哪一行"。
- **#717 / #718**：同样逐条复现。
- **新发现（7 条，`VALUE_LIST_TYPE_MISMATCH`）**：以下属性在 YAML 中是 `Code`/`AliasCode` 类型，但 CT 中 `Has Value List = N`：

| Location | YAML type | CT Has Value List |
| --- | --- | --- |
| AliasCode.standardCode | `#/Code` | N |
| AliasCode.standardCodeAliases | `#/Code` | N |
| BiomedicalConcept.code | `#/AliasCode` | N |
| BiomedicalConceptCategory.code | `#/AliasCode` | N |
| BiomedicalConceptProperty.code | `#/AliasCode` | N |
| CommentAnnotation.codes | `#/Code` | N |
| ResponseCode.code | `#/Code` | N |

## 2. trial-design：USDM v4.0.0 JSON → SDTM Trial Design 域

输入：`data/examples/complex_1.json`（Lilly LY900018 / NCT03421379，Phase 3 nasal glucagon 研究）。

实测终端输出：

```
trial-design: TS=9, TA=10, TE=5, TV=7, TI=0 rows written to reports/demo_trial_design (5 files)
```

TA.csv 前 4 行（共 10 行数据）：

```csv
STUDYID,DOMAIN,ARMCD,ARM,TAETORD,ETCD,ELEMENT,EPOCH
LY900018,TA,LYG,LY-G,1,SCREENIN,Screening,Screening
LY900018,TA,LYG,LY-G,2,GLUCLY90,GLUC_LY900018,Period 1
LY900018,TA,LYG,LY-G,3,WASHOUT,Wash Out,Wash Out
```

TV.csv 前 4 行（共 7 行数据）：

```csv
STUDYID,DOMAIN,VISITNUM,VISIT
LY900018,TV,1,Screening
LY900018,TV,2,"Period 1, Day -1"
LY900018,TV,3,"Period 1, Day 1"
```

TS.csv 前 3 行（共 9 行数据）：

```csv
STUDYID,DOMAIN,TSSEQ,TSPARMCD,TSPARM,TSVAL
LY900018,TS,1,STUDYID,Study Identifier,LY900018
LY900018,TS,2,TITLE,Trial Title,"A Phase 3 Study of Nasal Glucagon (LY900018) Compared to Intramuscular Glucagon ...
```

TI.csv 只有表头（`STUDYID,DOMAIN,IETESTCD,IETEST,IECAT`）——complex_1 不含 eligibility criteria 内容，属预期。

完整 USDM-path → SDTM-variable 映射及已标注的假设见 `docs/trial_design_mapping.md`。

## 3. rules：JSONata 一致性规则引擎

内置 starter rule library（`src/usdm_toolkit/rules/library/`），5 条规则全部派生自 `dataStructure.yml` 中 `Cardinality = 1` / `1..*` 的必填属性：

| Rule | Severity | Scope | 约束 |
| --- | --- | --- | --- |
| `USDM-REQ-001` | error | `StudyVersion` | 至少一个 study identifier（1..*） |
| `USDM-REQ-002` | error | `StudyVersion` | 至少一个 study title（1..*） |
| `USDM-REQ-003` | error | `StudyArm` | 必须有 type code（1） |
| `USDM-REQ-004` | error | `Encounter` | name 非空（1） |
| `USDM-REQ-005` | error | `InterventionalStudyDesign` | 必须有 intervention model code（1） |

对 complex_1 的实测结果：

```
rules: 0 violations written to reports/demo_rules_complex_1.md
```

（exit code = 0：合法实例全部通过。）

反向验证（把一个合法实例的 `titles` 清空后重跑，证明规则真的在工作）：

```
rules: 1 violations written to reports/demo_rules_broken.md
```

```markdown
| `USDM-REQ-002` | error | StudyVersion | `StudyVersion_1` | expression evaluated to False |
```

---

*Snapshot generated from real CLI runs on 2026-10-22; source files pinned to DDF-RA tag v4.0.0.*
