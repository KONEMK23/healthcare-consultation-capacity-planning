# MATH6186 Report Draft Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a visually verified, evidence-traceable English Word draft of the MATH6186 worried-well consultation-capacity report.

**Architecture:** Keep the English narrative in a reviewable Markdown source, keep bibliographic and evidence provenance in separate machine-readable/supporting files, and generate the DOCX deterministically with a focused `python-docx` builder. Validate the source and DOCX structurally before rendering every page to PNG for visual inspection.

**Tech Stack:** Python 3.12 bundled workspace runtime, `python-docx`, standard-library CSV/JSON/ZIP/XML tools, existing NumPy/Pandas analysis pipeline, LibreOffice/Poppler through the bundled document renderer, Markdown source, DOCX output.

## Global Constraints

- The main English text must target approximately 4,500-5,500 words, excluding the title page, references, captions, and reproducibility appendix.
- The primary deliverable is `report/MATH6186_case_study_draft.docx`.
- All quantitative claims must trace to the four generated CSVs or five generated PNGs under `outputs/`.
- The report must use all five figures, each with a numbered caption and adjacent interpretation.
- Synthetic scenarios must be described as planning experiments, not forecasts or clinical estimates.
- Coursework assumptions and literature-derived quantities must be distinguished explicitly.
- The balanced-cost negative finite-sample policy difference must remain visible and must not be clamped or reframed as a saving.
- Personal identity fields must remain as the literal tokens `[[STUDENT_NAME]]` and `[[STUDENT_ID]]` until the user supplies them.
- Use the `narrative_proposal` document preset without mixing another preset.
- Use US Letter portrait, one-inch margins, 0.492-inch header/footer distance, and 6.5-inch/9360-DXA usable width.
- Use inline figures rather than floating anchors.
- Use the bundled workspace Python with `PYTHONNOUSERSITE=1` for DOCX work.
- Use the Anaconda Python at `D:\ProgramData\anaconda3\python.exe` for the existing analytical test suite.
- Do not add `python-docx` to the project dependencies; the document workflow owns that dependency.
- At execution time, create an isolated `codex/` worktree from `master` before changing report files.
- Render the final DOCX to PNGs and inspect every page before delivery.

---

## Planned file structure

- Create `report/references.json`: canonical citation metadata for the six starting sources.
- Create `report/report-source-notes.md`: evidence inventory, claim map, chart map, parameter-source notes, and caveat register.
- Modify `report/evidence-map.csv`: complete the assumptions/provenance mapping for initial conditions and behaviour.
- Create `scripts/validate_report_sources.py`: validate references, evidence paths, required columns, and source-note coverage.
- Create `report/MATH6186_case_study_draft.md`: authoritative English narrative and figure/table/value markers.
- Create `scripts/validate_report_draft.py`: validate headings, length, markers, citations, numeric-token resolution, and language constraints.
- Create `scripts/build_report_docx.py`: convert the validated source and generated evidence into the styled DOCX.
- Create `scripts/validate_report_docx.py`: inspect DOCX text, styles, page geometry, media, captions, tables, and unresolved markers.
- Create `report/MATH6186_case_study_draft.docx`: final rendered-and-reviewed draft.
- Modify `.gitignore`: ignore only task-local render intermediates under `tmp/report-render/`.

### Marker interfaces

The Markdown source will use these exact interfaces:

```text
[[STUDENT_NAME]]
[[STUDENT_ID]]
[@<reference-id>]
[[VALUE:<scenario>|<summary-column>|<format-spec>]]
[[FIGURE:<filename>|<caption>|<bookmark>]]
[[PARAMETER_TABLE]]
[[POLICY_TABLE]]
[[EQUATION:<equation-id>]]
[[REFERENCE:<reference-id>]]
```

`build_report_docx.py` must resolve every marker except the two permitted
identity tokens. It must reject an unknown scenario, column, format, figure,
equation identifier, or duplicate bookmark.

---

### Task 1: Establish the citation and evidence contract

**Files:**

- Create: `report/references.json`
- Create: `report/report-source-notes.md`
- Modify: `report/evidence-map.csv`
- Create: `scripts/validate_report_sources.py`

**Interfaces:**

- Consumes: `report/literature-matrix.csv`, `outputs/data/*.csv`, `outputs/figures/*.png`, the assignment brief, and the supplied Singh-Gromov PDF.
- Produces: `references.json` keyed by `singh_gromov_2025`, `chatterjee_2020`, `asmundson_taylor_2020`, `blyuss_kyrychko_2005`, `singh_rebennack_2025`, and `qin_2011`; a source-note contract used by Tasks 2-4.

- [ ] **Step 1: Record the canonical reference schema**

Create `report/references.json` as a JSON array. Every object must contain
`id`, `authors`, `year`, `title`, `journal`, `volume`, `issue`,
`pages_or_article`, `doi`, `url`, `role`, and `limitation`. Use these verified
Crossref/publisher metadata values:

| ID | Authors | Year | Journal | Volume(issue) | Pages/article | DOI |
|---|---|---:|---|---|---|---|
| `singh_gromov_2025` | Bismark Singh; Dmitry Gromov | 2025 | PLOS ONE | 20(9) | e0319550 | 10.1371/journal.pone.0319550 |
| `chatterjee_2020` | Seshadri Sekhar Chatterjee; Mansi Vora; Barikar C. Malathesh; Ranjan Bhattacharyya | 2020 | Asian Journal of Psychiatry | 54 | 102247 | 10.1016/j.ajp.2020.102247 |
| `asmundson_taylor_2020` | Gordon J. G. Asmundson; Steven Taylor | 2020 | Journal of Anxiety Disorders | 70 | 102196 | 10.1016/j.janxdis.2020.102196 |
| `blyuss_kyrychko_2005` | Konstantin B. Blyuss; Yuliya N. Kyrychko | 2005 | Applied Mathematics and Computation | 160(1) | 177-187 | 10.1016/j.amc.2003.10.033 |
| `singh_rebennack_2025` | Bismark Singh; Steffen Rebennack | 2025 | IISE Transactions | 58(4) | 489-502 | 10.1080/24725854.2025.2525918 |
| `qin_2011` | Yan Qin; Ruoxuan Wang; Asoo J. Vakharia; Yuwen Chen; Michelle M. H. Seref | 2011 | European Journal of Operational Research | 213(2) | 361-374 | 10.1016/j.ejor.2010.11.024 |

Use the exact titles already recorded in `report/literature-matrix.csv`. Use
`https://doi.org/<doi>` as each URL and copy the matrix's role and critical
note into `role` and `limitation`.

- [ ] **Step 2: Complete the assumptions evidence row**

Update the `3-4` assumptions/provenance row of
`report/evidence-map.csv`. Its required-column list must include:

```text
alpha;beta_p;beta_w;beta_wp;gamma_p;gamma_w;delta_p;
initial_susceptible;initial_infected;initial_worried;initial_recovered;
population;p_infected;p_worried;cv;underage;overage;
model_structure_provenance;behaviour_provenance;rate_parameter_provenance;
initial_condition_provenance;service_demand_provenance;
uncertainty_provenance;cost_provenance
```

Keep the value on one CSV field and preserve the existing
`outputs/data/parameters.csv` evidence path.

- [ ] **Step 3: Write the source notes**

Create `report/report-source-notes.md` with these visible headings:

```markdown
# MATH6186 Report Source Notes
## Reporting question and audience
## Source inventory
## Quantitative claim map
## Chart map
## Parameter provenance
## Citation-use map
## Caveat register
## Reproducibility record
```

The chart map must contain one record per figure with:

```text
report section | analytical question | figure file | supported claim |
adjacent caveat
```

The caveat register must include synthetic data, assumed service-seeking
probabilities, assumed CV and costs, no empirical calibration, a single pooled
resource, repeated independent daily decisions, finite-sample comparison, and
the two outside-domain numerical limitations recorded during final code review.

- [ ] **Step 4: Implement the source validator**

Create `scripts/validate_report_sources.py` using only the Python standard
library. It must:

```python
EXPECTED_REFERENCE_IDS = {
    "singh_gromov_2025",
    "chatterjee_2020",
    "asmundson_taylor_2020",
    "blyuss_kyrychko_2005",
    "singh_rebennack_2025",
    "qin_2011",
}
EXPECTED_CSVS = {
    "daily_metrics.csv",
    "parameters.csv",
    "summary.csv",
    "trajectories.csv",
}
EXPECTED_FIGURES = {
    "figure_1_compartments.png",
    "figure_2_risk_ratio.png",
    "figure_3_demand_uncertainty.png",
    "figure_4_optimal_capacity.png",
    "figure_5_sensitivity.png",
}
```

Reject duplicate reference IDs, missing reference fields, non-DOI URLs for the
six canonical references, missing evidence files, empty evidence files,
unresolvable evidence-map columns, missing figure records in the chart map, or
an assumptions row that omits any required provenance field.

- [ ] **Step 5: Run the validator**

Run:

```powershell
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_sources.py
```

Expected output:

```text
Report source validation passed: 6 references, 12 evidence claims, 5 figures.
```

- [ ] **Step 6: Commit the evidence contract**

```powershell
git add report/references.json report/report-source-notes.md report/evidence-map.csv scripts/validate_report_sources.py
git commit -m "docs: establish report evidence contract"
```

---

### Task 2: Draft the complete evidence-linked English narrative

**Files:**

- Create: `report/MATH6186_case_study_draft.md`
- Create: `scripts/validate_report_draft.py`

**Interfaces:**

- Consumes: Task 1 reference IDs and source notes; `outputs/data/summary.csv`; the implemented equations in `src/math6186/`.
- Produces: a complete Markdown manuscript using the marker grammar; the DOCX builder in Task 3 consumes this file.

- [ ] **Step 1: Write the validation rules before the manuscript**

Create `scripts/validate_report_draft.py` with:

```python
REQUIRED_HEADINGS = [
    "Abstract",
    "1. Introduction",
    "2. Literature Review",
    "3. Deterministic Worried-Well Model",
    "4. Stochastic Consultation Demand",
    "5. Newsvendor Formulation",
    "6. Experimental Design",
    "7. Results",
    "8. Discussion",
    "9. Conclusion",
    "References",
    "Appendix A. Reproducibility",
]
REQUIRED_FIGURES = [
    "figure_1_compartments.png",
    "figure_2_risk_ratio.png",
    "figure_3_demand_uncertainty.png",
    "figure_4_optimal_capacity.png",
    "figure_5_sensitivity.png",
]
PERMITTED_IDENTITY_TOKENS = {"[[STUDENT_NAME]]", "[[STUDENT_ID]]"}
```

The validator must count 4,500-5,500 main-text words after excluding the title
block, references, captions, and Appendix A. It must also verify:

- every required heading appears once and in order;
- each figure marker appears once and uses a unique `fig1`-`fig5` bookmark;
- `[[PARAMETER_TABLE]]` and `[[POLICY_TABLE]]` each appear once;
- every one of the six reference IDs is cited at least once as
  `[@reference_id]`;
- every citation key exists in `references.json`;
- every `[[VALUE:...]]` token resolves to one row and one numeric column in
  `summary.csv`;
- all equation IDs belong to `compartment_system`, `expected_demand`,
  `sample_average_cost`, or `critical_fractile`;
- no unresolved square-bracket marker exists except the two identity tokens;
- the prose does not call the outputs forecasts, predictions, observed demand,
  patient data, or clinically calibrated results.

- [ ] **Step 2: Run the validator before the manuscript exists**

Run:

```powershell
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_draft.py
```

Expected: failure naming the missing
`report/MATH6186_case_study_draft.md`.

- [ ] **Step 3: Write the title block and section skeleton**

Create `report/MATH6186_case_study_draft.md` with:

```markdown
# Planning Consultation Capacity Under Worried-Well Demand

**Student:** [[STUDENT_NAME]]
**Student ID:** [[STUDENT_ID]]
**Module:** MATH6186 Operational Research Case Study
**Facilitator:** Dr Bismark Singh
**Submission date:** 8 September 2026

## Abstract
## 1. Introduction
## 2. Literature Review
## 3. Deterministic Worried-Well Model
## 4. Stochastic Consultation Demand
## 5. Newsvendor Formulation
## 6. Experimental Design
## 7. Results
### 7.1 Behavioural regimes
### 7.2 Demand uncertainty
### 7.3 Cost and service-level sensitivity
### 7.4 Service-seeking and initial-condition sensitivity
### 7.5 Optimized policy versus mean-demand planning
## 8. Discussion
## 9. Conclusion
## References
## Appendix A. Reproducibility
```

- [ ] **Step 4: Draft the literature and modelling sections**

Write approximately:

- 180-200 words for the abstract;
- 350-400 words for the introduction;
- 1,050-1,150 words for the thematic literature review;
- 1,150-1,250 words across deterministic, stochastic, and newsvendor models;
- 350-400 words for experimental design.

Use all six citation IDs and make each source's limitation explicit. Present
these four equation markers adjacent to their definitions:

```text
[[EQUATION:compartment_system]]
[[EQUATION:expected_demand]]
[[EQUATION:sample_average_cost]]
[[EQUATION:critical_fractile]]
```

State the implemented baseline parameters exactly: population 100,000;
`beta_p=0.74`; `beta_w=0.70`; `beta_wp=0.70`;
`gamma_p=gamma_w=1/14`; `delta_p=1/240`; initial state
`(0.98, 0.01, 0.01, 0)`; baseline `p_P=1`; baseline `p_W=0.5`;
baseline CV `0.15`; 5,000 optimization samples; 10,000 evaluation samples;
seeds 6186 and 6187.

- [ ] **Step 5: Draft the results with evidence markers**

Write approximately 900-1,000 words. Insert the five markers in order:

```text
[[FIGURE:figure_1_compartments.png|Compartment trajectories under cautious, default, and high-contact behaviour.|fig1]]
[[FIGURE:figure_2_risk_ratio.png|Ratio of worried-well to genuinely infected population over the 50-day horizon.|fig2]]
[[FIGURE:figure_3_demand_uncertainty.png|Daily consultation-demand uncertainty under default behaviour.|fig3]]
[[FIGURE:figure_4_optimal_capacity.png|Optimized daily consultation capacity by behavioural regime.|fig4]]
[[FIGURE:figure_5_sensitivity.png|Uncertainty and cost sensitivity; the right-hand panel fixes overage cost at c_o = 1.|fig5]]
```

Use `[[VALUE:...]]` tokens for the key policy comparisons, including:

```text
[[VALUE:behaviour_alpha_1|optimized_total_cost|,.1f]]
[[VALUE:behaviour_alpha_1|mean_policy_total_cost|,.1f]]
[[VALUE:behaviour_alpha_1|relative_cost_reduction_pct|.2f]]
[[VALUE:cost_cu_1_co_1|relative_cost_reduction_pct|.4f]]
[[VALUE:cost_cu_10_co_1|relative_cost_reduction_pct|.2f]]
```

Insert `[[POLICY_TABLE]]` after the first aggregate policy comparison. Pair
every figure with a prose paragraph before or after it that explains the
takeaway, how to read it, and the limitation or implication.

- [ ] **Step 6: Draft discussion, conclusion, references, and appendix**

Write approximately:

- 550-650 words for the discussion;
- 160-200 words for the conclusion.

Insert `[[PARAMETER_TABLE]]` in Section 3. In the discussion, cover every
caveat from Task 1 and distinguish project-domain limitations from the two
outside-domain integer/cost-ratio edge cases. In Appendix A, state:

```text
python scripts/run_analysis.py
in-sample seed = 6186
out-of-sample seed = 6187
in-sample scenarios = 5,000
out-of-sample scenarios = 10,000
```

The References section must contain one list item per citation key using
`[[REFERENCE:<id>]]`; the builder will render the canonical metadata.

- [ ] **Step 7: Run the draft validator and revise to green**

Run:

```powershell
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_draft.py
```

Expected output:

```text
Report draft validation passed: <word-count> main-text words, 6 references, 5 figures.
```

- [ ] **Step 8: Commit the manuscript**

```powershell
git add report/MATH6186_case_study_draft.md scripts/validate_report_draft.py
git commit -m "docs: draft evidence-linked MATH6186 report"
```

---

### Task 3: Build and structurally validate the Word report

**Files:**

- Modify: `.gitignore`
- Create: `scripts/build_report_docx.py`
- Create: `scripts/validate_report_docx.py`
- Create: `report/MATH6186_case_study_draft.docx`

**Interfaces:**

- Consumes: the Task 2 Markdown markers, Task 1 references, four CSVs, and five PNGs.
- Produces: `build_report(source: Path, output: Path) -> None`; a DOCX with resolved values, figures, tables, equations, captions, bookmarks, page furniture, and only the two permitted identity tokens.

- [ ] **Step 1: Implement a failing structural validator**

Create `scripts/validate_report_docx.py` using `python-docx`, `zipfile`, and
`lxml`. It must exit non-zero unless the DOCX satisfies:

```python
EXPECTED_SECTION_TITLES = [
    "Abstract",
    "1. Introduction",
    "2. Literature Review",
    "3. Deterministic Worried-Well Model",
    "4. Stochastic Consultation Demand",
    "5. Newsvendor Formulation",
    "6. Experimental Design",
    "7. Results",
    "8. Discussion",
    "9. Conclusion",
    "References",
    "Appendix A. Reproducibility",
]
EXPECTED_MEDIA_COUNT = 5
EXPECTED_TABLE_COUNT = 2
EXPECTED_CAPTIONS = 5
```

Also verify Letter dimensions, one-inch margins, 0.492-inch header/footer
distance, Normal/Heading 1/Heading 2/Heading 3/Caption style tokens, 9360-DXA
table width, 120-DXA table indent, inline rather than anchored drawings,
bookmarks `fig1`-`fig5`, no unresolved `[[VALUE:`, `[[FIGURE:`,
`[[EQUATION:`, `[[REFERENCE:`, `[[PARAMETER_TABLE]]`, or `[[POLICY_TABLE]]`
tokens, and no identity-like token other than the two permitted ones.

- [ ] **Step 2: Verify the validator fails before the DOCX exists**

Run with the bundled runtime:

```powershell
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_report_docx.py
```

Expected: failure naming the missing DOCX.

- [ ] **Step 3: Implement the document token map**

In `scripts/build_report_docx.py`, define:

```python
PRESET = {
    "page_width_inches": 8.5,
    "page_height_inches": 11.0,
    "margin_inches": 1.0,
    "header_footer_inches": 0.492,
    "content_width_dxa": 9360,
    "body_font": "Calibri",
    "body_size_pt": 11,
    "body_after_pt": 8,
    "body_line_spacing": 1.333,
    "h1": (16, "2E74B5", 18, 10),
    "h2": (13, "2E74B5", 12, 6),
    "h3": (12, "1F4D78", 8, 4),
    "table_indent_dxa": 120,
    "table_cell_margins_dxa": (80, 80, 120, 120),
    "table_header_fill": "F4F6F9",
}
```

Use an `editorial_cover` title-page pattern as one named override: centred
28-point dark-blue title, 14-point subtitle, generous vertical whitespace,
plain metadata lines, no title rule, and no decorative border. Suppress the
running header on the title page; subsequent pages use
`MATH6186 | Worried-Well Consultation Capacity` and a right-aligned page-number
field.

- [ ] **Step 4: Implement source parsing and marker resolution**

Implement these functions with the exact signatures:

```python
def load_references(path: Path) -> dict[str, dict[str, object]]: ...
def load_summary(path: Path) -> dict[str, dict[str, str]]: ...
def resolve_value_marker(marker: str, summary: dict[str, dict[str, str]]) -> str: ...
def parse_figure_marker(marker: str) -> tuple[str, str, str]: ...
def resolve_citation_marker(marker: str, references: dict[str, dict[str, object]]) -> str: ...
def resolve_inline_markup(paragraph: str, references: dict[str, dict[str, object]]) -> list[tuple[str, bool, bool]]: ...
def format_reference(record: dict[str, object]) -> str: ...
def build_report(source: Path, output: Path) -> None: ...
```

Reject unresolved or malformed markers rather than copying them into the DOCX.
Parse only the project's constrained Markdown subset: headings, paragraphs,
single-level bullets, `**bold**`, `*italic*`, `[@reference-id]` citations,
reference markers, and the explicit special markers. Citation markers render
as parenthetical Harvard-style author-date citations.

- [ ] **Step 5: Implement equations, figures, captions, and tables**

Map the four equation IDs to the implemented equations:

```text
dS/dt = -(beta_P + beta_WP)SI_P - beta_W SI_W + delta_P R_P + gamma_W I_W
dI_P/dt = beta_P SI_P + alpha beta_P I_P I_W - gamma_P I_P
dI_W/dt = -alpha beta_P I_P I_W + beta_W SI_W + beta_WP SI_P - gamma_W I_W
dR_P/dt = gamma_P I_P - delta_P R_P

m_t = N[p_P I_P(t) + p_W I_W(t)]

min_q (1/n) sum_j [c_u(D_j-q)^+ + c_o(q-D_j)^+]

tau = c_u/(c_u+c_o), q* = F_n^{-1}(tau)
```

Use Cambria Math, centred paragraphs, and equation labels only where the prose
references them. Insert each PNG inline at no more than 6.35 inches wide.

Create Caption-style paragraphs containing cached `SEQ Figure` display text
and bookmarks `fig1`-`fig5`. Create the parameter table from the baseline
`parameters.csv` row and the policy table from selected `summary.csv` rows.
Apply fixed DXA geometry; do not use autofit, percentage widths, or fixed row
heights.

- [ ] **Step 6: Build and materialize the DOCX**

Run:

```powershell
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\build_report_docx.py
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\Users\25470\.codex\plugins\cache\openai-primary-runtime\documents\26.727.11326\skills\documents\scripts\fields_materialize.py' report\MATH6186_case_study_draft.docx --out report\MATH6186_case_study_draft.materialized.docx
Move-Item -LiteralPath report\MATH6186_case_study_draft.materialized.docx -Destination report\MATH6186_case_study_draft.docx -Force
```

Expected: a non-empty DOCX containing all sections, two tables, five figures,
and resolved field display text.

- [ ] **Step 7: Run structural and figure audits**

Run:

```powershell
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_report_docx.py
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\Users\25470\.codex\plugins\cache\openai-primary-runtime\documents\26.727.11326\skills\documents\scripts\images_audit.py' report\MATH6186_case_study_draft.docx
```

Expected: structural validation passes and all drawings are inline.

- [ ] **Step 8: Commit the builder and first DOCX**

Before rendering, add this exact task-local intermediate path to `.gitignore`:

```gitignore
tmp/report-render/
```

Render the first DOCX and inspect every generated page:

```powershell
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\Users\25470\.codex\plugins\cache\openai-primary-runtime\documents\26.727.11326\skills\documents\render_docx.py' report\MATH6186_case_study_draft.docx --output_dir tmp\report-render --emit_pdf
```

If any page has clipping, overlap, broken tables, detached captions, or
unreadable figures, fix the source or builder, rebuild, revalidate, and rerender
before committing.

```powershell
git add .gitignore scripts/build_report_docx.py scripts/validate_report_docx.py report/MATH6186_case_study_draft.docx
git commit -m "feat: build formatted MATH6186 report draft"
```

---

### Task 4: Render, inspect, revise, and deliver the report

**Files:**

- Modify: `report/MATH6186_case_study_draft.md` (only for evidenced content or page-flow corrections)
- Modify: `scripts/build_report_docx.py` (only for layout corrections)
- Modify: `scripts/validate_report_draft.py` (only when a verified contract omission is found)
- Modify: `scripts/validate_report_docx.py` (only when a verified structural contract omission is found)
- Regenerate: `report/MATH6186_case_study_draft.docx`

**Interfaces:**

- Consumes: Tasks 1-3 and the bundled renderer.
- Produces: the visually verified DOCX and fresh verification evidence.

- [ ] **Step 1: Re-run the analytical foundation**

Run:

```powershell
& 'D:\ProgramData\anaconda3\python.exe' -m pytest -q
& 'D:\ProgramData\anaconda3\python.exe' scripts\run_analysis.py
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_sources.py
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_draft.py
```

Expected: 83 analytical tests pass; analysis regeneration and both report
validators exit zero.

- [ ] **Step 2: Rebuild and structurally validate from scratch**

Run the Task 3 build/materialization commands, then:

```powershell
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_report_docx.py
```

Expected: structural validation exits zero with exactly five figures and two
tables.

- [ ] **Step 3: Render the DOCX**

Run:

```powershell
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\Users\25470\.codex\plugins\cache\openai-primary-runtime\documents\26.727.11326\skills\documents\render_docx.py' report\MATH6186_case_study_draft.docx --output_dir tmp\report-render --emit_pdf
```

Expected: one `page-<N>.png` per DOCX page and a non-empty rendered PDF.

- [ ] **Step 4: Inspect every rendered page**

Open every `tmp/report-render/page-<N>.png` at 100% and verify:

- no clipped or overlapping text;
- no blank or nearly blank unintended pages;
- no isolated heading at a page bottom;
- equations are legible and remain with their explanations;
- all five figures are sharp, uncropped, and adjacent to their captions;
- both tables fit the page and wrap without boundary-hugging text;
- captions and figures do not separate awkwardly;
- heading hierarchy, page numbering, header, and references are consistent;
- the two permitted identity tokens are visually unobtrusive;
- Figure 5's caption explicitly states `c_o = 1` for the right-hand panel.

- [ ] **Step 5: Iterate on concrete render defects**

For each observed defect, record the page and cause, patch the Markdown or
builder, rebuild, rerun both validators, and rerender all pages. Repeat until
every page passes. Do not patch the generated DOCX manually.

- [ ] **Step 6: Run final verification**

Run:

```powershell
& 'D:\ProgramData\anaconda3\python.exe' -m pytest -q
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_sources.py
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_draft.py
$env:PYTHONNOUSERSITE='1'
& 'D:\Users\25470\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\validate_report_docx.py
git diff --check
git status --short
```

Expected: 83 tests pass; all three report validators pass; `git diff --check`
prints nothing; status contains only the intended task files before commit.

- [ ] **Step 7: Commit the visually verified deliverable**

```powershell
git add .gitignore report/references.json report/report-source-notes.md report/evidence-map.csv report/MATH6186_case_study_draft.md report/MATH6186_case_study_draft.docx scripts/validate_report_sources.py scripts/validate_report_draft.py scripts/build_report_docx.py scripts/validate_report_docx.py
git commit -m "docs: deliver verified MATH6186 report draft"
```

- [ ] **Step 8: Handoff**

Report the final DOCX as the primary output. State the fresh analytical-test
count, main-text word count, rendered page count, and that all pages were
visually inspected. Mention that `[[STUDENT_NAME]]` and `[[STUDENT_ID]]`
remain for the user to replace.
