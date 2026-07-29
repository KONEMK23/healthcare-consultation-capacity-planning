# MATH6186 Report Source Notes

## Reporting question and audience

How should daily consultation capacity change when worried-well behaviour, demand uncertainty, and shortage costs vary during an early outbreak? The audience is technically literate healthcare-operations readers. This is a reproducible synthetic planning experiment, not a forecast or clinical estimate.

## Source inventory

| Citation key | Role in report | Limitation carried into prose |
|---|---|---|
| `singh_gromov_2025` | Four-compartment model and behavioural regimes | Synthetic dynamics do not estimate consultation capacity. |
| `chatterjee_2020` | Healthcare relevance of worried-well demand | Conceptual discussion, not an optimization study. |
| `asmundson_taylor_2020` | Anxiety and perceived risk context | No compartmental resource-planning model. |
| `blyuss_kyrychko_2005` | Two-process modelling background | Does not model worried-well capacity demand. |
| `singh_rebennack_2025` | Scarce healthcare-resource context | Release policies, not this newsvendor capacity decision. |
| `qin_2011` | Classical newsvendor foundation | Only the single-resource form is used. |

`report/references.json` is the canonical source for author order, metadata, DOI URLs, roles, and limitations. Literature provides framing and interpretation; it does not supply unrecorded numerical inputs.

## Quantitative claim map

Every report number must be calculated from, or quoted directly from, the saved evidence below. Figures support qualitative readings only unless an adjacent value is traceable to its CSV.

| Section | Claim scope | Evidence |
|---|---|---|
| 3 | Population conservation | `trajectories.csv`: `S`, `I_P`, `I_W`, `R_P`, `total` |
| 3-4 | Model, demand, and cost assumptions | `parameters.csv` and the complete contract in `evidence-map.csv` |
| 7.1 | Behavioural peak size and timing | `summary.csv`: infected and worried-well peak columns |
| 7.1 | Early worried-well/infected pressure ratio | `figure_2_risk_ratio.png` |
| 7.2 | Demand interval and capacity | `daily_metrics.csv`: demand percentiles, mean, optimized capacity |
| 7.2 | Uncertainty sensitivity of optimized cost | `figure_5_sensitivity.png` |
| 7.3 | Shortage-cost sensitivity | `daily_metrics.csv`: capacity and optimized expected cost |
| 7.3 | Cost sensitivity of mean-policy comparison | `figure_5_sensitivity.png` |
| 7.4 | Service-seeking sensitivity | `daily_metrics.csv`: scenario and mean demand |
| 7.4 | Initial-condition sensitivity | `daily_metrics.csv`: scenario, demand, capacity |
| 7.5 | Optimized versus mean-demand policy | `summary.csv`: both total costs and signed relative difference |
| 8 | Synthetic status and seeds | `parameters.csv`: sample sizes, seeds, provenance |

## Chart map

| report section | analytical question | figure file | supported claim | adjacent caveat |
|---|---|---|---|---|
| 7.1 | How do behaviour regimes alter trajectories? | `figure_1_compartments.png` | Changing alpha changes synthetic compartment timing and relative size. | Deterministic model fractions, not observed prevalence. |
| 7.1 | When can worried-well pressure exceed infection pressure? | `figure_2_risk_ratio.png` | The generated ratio can exceed one early in the behavioural scenarios. | Conditional model ratio, not a measured consultation ratio. |
| 7.2 | What uncertainty surrounds default demand? | `figure_3_demand_uncertainty.png` | The saved 5th--95th band displays stochastic uncertainty around mean demand. | CV and service-seeking probabilities are coursework assumptions. |
| 7.1 | How does behaviour alter daily capacity? | `figure_4_optimal_capacity.png` | Optimized capacity changes over time and across alpha scenarios. | One pooled resource; no carry-over between days. |
| 7.2-7.3 | How do uncertainty and shortage cost affect cost? | `figure_5_sensitivity.png` | The panels compare optimized cost across CVs and signed mean-policy differences across underage costs. | Overage cost is fixed at 1; costs are assumed and comparisons are finite-sample. |

## Parameter provenance

`parameters.csv` is authoritative for each scenario. Its provenance columns separate literature-derived structure, behavioural regimes, baseline rates, and initial conditions from coursework assumptions for synthetic population, service-seeking probabilities, CV, costs, and initial-condition sensitivity. The `3-4` evidence-map row requires every corresponding parameter and provenance field.

## Citation-use map

- `singh_gromov_2025`: model structure, alpha regimes, baseline rates, and initial condition.
- `chatterjee_2020` and `asmundson_taylor_2020`: worried-well healthcare and psychological relevance, never calibration or capacity evidence.
- `blyuss_kyrychko_2005`: two-process modelling background only.
- `singh_rebennack_2025`: outbreak-resource context, distinct from this capacity model.
- `qin_2011`: classical newsvendor framework; decisions, costs, and synthetic experiments remain coursework choices.

## Caveat register

- Synthetic data are planning scenarios, never forecasts or clinical estimates.
- Service-seeking probabilities are assumed coursework inputs.
- CV and underage/overage costs are assumed coursework inputs, not calibrated economic quantities.
- There is no empirical calibration to patient, appointment, surveillance, or local-capacity data.
- Capacity is a single pooled resource, not separate staff, rooms, test types, urgency, or streams.
- Daily choices are repeated independent single-period decisions; unused capacity does not carry forward.
- The optimized-versus-mean comparison is finite-sample out-of-sample evidence. The balanced-cost `cost_cu_1_co_1` relative difference is negative and must not be called a saving.
- Outside the project domain, demand and capacity are validated only as non-negative integers in the signed 64-bit arithmetic range; larger values are rejected.
- Outside the project domain, extremely disproportionate positive finite cost ratios remain subject to floating-point precision and need numerical checking before interpretation.

## Reproducibility record

The evidence is the four CSV files in `outputs/data` and five PNGs in `outputs/figures`. Run `python scripts/run_analysis.py` after changing the model; the parameter record stores seeds 6186 and 6187 plus sample sizes. Then run:

```powershell
& 'D:\ProgramData\anaconda3\python.exe' scripts\validate_report_sources.py
```
