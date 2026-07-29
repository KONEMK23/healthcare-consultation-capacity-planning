# MATH6186 Case Study Report Draft Design

**Date:** 29 July 2026

**Status:** Approved direction; written specification awaiting final review

**Primary deliverable:** `report/MATH6186_case_study_draft.docx`

## 1. Purpose

Create a polished English technical-report draft that answers:

> How should daily consultation capacity change when worried-well behaviour,
> demand uncertainty, and shortage costs vary during the early outbreak?

The report will explain the deterministic worried-well model, the stochastic
consultation-demand extension, and the repeated single-period newsvendor
decision. It will interpret the generated computational evidence without
presenting the synthetic scenarios as real forecasts.

## 2. Audience and assessment alignment

The primary audience is the MATH6186 assessor. The report will assume
operational-research knowledge but no specialist epidemiology background.

The narrative will reflect the assessment guidance:

- literature review and understanding: approximately 25% of the substantive
  discussion;
- newsvendor formulation, assumptions, and implementation: approximately 30%;
- experiments, interpretation, applicability, and limitations: approximately
  30%;
- the remaining attention will be given to exposition, figures, tables,
  organization, and references.

These percentages guide emphasis rather than impose mechanical section lengths.

## 3. Scope and target length

The main text will target approximately 4,500-5,500 words, excluding the title
page, references, figure and table captions, and reproducibility appendix. The
assignment brief states no explicit word limit, so clarity and assessment
coverage govern the final length.

The report will contain:

1. title page;
2. abstract;
3. introduction and research question;
4. literature review;
5. deterministic worried-well model;
6. stochastic consultation-demand model;
7. newsvendor formulation;
8. experimental design;
9. results and sensitivity analysis;
10. discussion and limitations;
11. conclusion;
12. references;
13. a short reproducibility appendix.

## 4. Evidence and source boundary

All quantitative claims will be traceable to the existing generated evidence:

- `outputs/data/trajectories.csv`;
- `outputs/data/daily_metrics.csv`;
- `outputs/data/summary.csv`;
- `outputs/data/parameters.csv`;
- the five figures in `outputs/figures`;
- `report/evidence-map.csv`;
- `report/literature-matrix.csv`.

The Singh and Gromov paper provides the compartment-model basis. Other sources
in the literature matrix support worried-well behaviour, behavioural risk,
compartment modelling, resource allocation, and the classical newsvendor
problem. References will be written in a consistent Harvard-style author-date
format. No source, result, or parameter provenance will be invented.

Coursework assumptions will be labelled explicitly. In particular, the
service-seeking probabilities, coefficient of variation, shortage and overage
costs, stochastic-sample sizes, and some sensitivity cases are modelling
choices rather than estimated clinical quantities.

## 5. Report argument

The report will follow an answer-first technical narrative:

1. Worried-well behaviour can create substantial early consultation pressure
   even when it does not increase the infected population directly.
2. Consultation demand is uncertain because deterministic compartment
   trajectories are translated into stochastic daily appointment counts.
3. The newsvendor critical fractile converts the shortage-to-overage cost ratio
   into an optimal daily capacity.
4. Behaviour, uncertainty, service seeking, initial conditions, and the cost
   ratio change capacity and expected cost in different ways.
5. The optimized policy materially outperforms mean-demand planning when
   shortage cost exceeds overage cost, but a small negative finite-sample
   difference is retained honestly in the balanced-cost case.
6. The model is a transparent planning experiment, not a calibrated forecast.

## 6. Section design

### Abstract

State the problem, modelling chain, experiment design, central result, and main
limitation in approximately 180-220 words.

### Introduction

Define the worried-well operational problem, motivate consultation capacity,
state the research question, and summarize the contribution and report
structure.

### Literature review

Organize sources by theme rather than as isolated summaries:

- worried-well behaviour and pandemic anxiety;
- behavioural compartment models;
- stochastic healthcare-resource demand;
- the newsvendor model and resource allocation.

End with the gap addressed by linking worried-well dynamics to uncertain daily
capacity decisions.

### Deterministic and stochastic models

Present the four ordinary differential equations, initial conditions,
population-conservation property, parameter table, behavioural regimes, and
50-day horizon. Then define the consultation-demand equation, truncated-normal
uncertainty model, stochastic integerization, and fixed seeds.

### Newsvendor formulation

Define the decision variable, underage and overage costs, sample-average
objective, empirical critical-fractile solution, mean-demand benchmark, and
out-of-sample evaluation. Explain why the model is solved separately for each
day.

### Experimental design

Describe the behaviour, uncertainty, cost, service-seeking, and
initial-condition experiment groups. State the 5,000 in-sample and 10,000
out-of-sample scenario sizes, seeds 6186 and 6187, and common-random-number
comparison.

### Results

Use the five existing figures in a fixed reading order:

1. compartment trajectories;
2. worried-well-to-infected pressure ratio;
3. default demand uncertainty;
4. optimized capacity by behavioural regime;
5. uncertainty and cost sensitivity.

Each figure will have an adjacent paragraph that states the takeaway,
interpretation, and relevant caveat. A compact results table will report
selected policy costs and percentage differences. The Figure 5 caption or
adjacent text will state that the right-hand cost panel fixes overage cost at
`c_o = 1`.

### Discussion and conclusion

Translate results into operational implications, then discuss synthetic data,
parameter assumptions, a single pooled resource, daily independent decisions,
lack of intertemporal capacity adjustment, and lack of empirical calibration.
The conclusion will answer the research question without adding unsupported
claims.

## 7. Visual and document design

The document will use a restrained academic-report style:

- US Letter portrait with one-inch margins;
- a simple professional title page;
- Aptos or an available metrically stable sans-serif body font;
- consistent heading hierarchy and numbered sections;
- page numbers and a concise running header after the title page;
- equations centred and numbered only when referenced;
- figures inserted at readable width with numbered captions;
- tables used only for comparable numeric or parameter records;
- references formatted consistently with hanging indents.

The title page will contain placeholders for student name, student ID, module,
facilitator, and submission date because personal identifiers have not been
provided.

## 8. Reproducibility appendix

The appendix will briefly record:

- Python 3.11+ environment requirement;
- the analysis command `python scripts/run_analysis.py`;
- fixed seeds and sample sizes;
- the four CSV and five PNG outputs;
- the distinction between deterministic trajectories, stochastic samples, and
  out-of-sample policy evaluation.

Implementation listings will not be pasted into the main report.

## 9. Quality and verification

Before delivery:

1. regenerate the analytical outputs and confirm the test suite passes;
2. verify every important number against the saved CSV evidence;
3. check that each figure is cited and interpreted in the text;
4. confirm all references used in the prose appear in the reference list;
5. scan for unsupported claims, inconsistent notation, placeholders outside
   the title-page identity fields, and accidental claims of prediction;
6. render the DOCX to page images;
7. inspect every rendered page for clipping, broken equations, figure
   readability, awkward page breaks, and table overflow;
8. revise and re-render until the document passes visual inspection.

## 10. Non-goals

This draft will not:

- claim that synthetic outputs forecast a specific real outbreak;
- introduce an unvalidated multi-period inventory or queueing model;
- estimate parameters from patient-level data;
- hide the balanced-cost negative finite-sample policy difference;
- fabricate citations, parameter sources, or empirical validation;
- include personal identifying information that the user has not supplied.

## 11. Acceptance criteria

The design is successfully implemented when:

- an English DOCX of the planned scope exists under `report/`;
- the report is approximately within the target length and covers all assessed
  components;
- equations, assumptions, experiments, and results are internally consistent
  with the implemented model;
- every major quantitative claim is traceable to a generated artifact;
- all five figures appear with captions and adjacent interpretation;
- modelling assumptions and limitations are explicit;
- references are consistent and complete for all cited works;
- the latest rendered pages show no visible layout defects.
