# MATH6186 Worried-Well Consultation Capacity Design

## 1. Objective

Build a reproducible operational-research study that connects:

1. the deterministic worried-well compartmental model in Singh and Gromov (2025);
2. a transparent stochastic demand model;
3. a repeated single-period newsvendor model for daily medical consultation or diagnostic appointment capacity; and
4. computational experiments that explain how behaviour, uncertainty, and cost asymmetry affect capacity decisions.

The decision is the number of consultation or diagnostic appointment slots to prepare for each day of the early outbreak. The analysis must distinguish biological infection demand from worried-well demand while treating both as potential pressure on healthcare capacity.

## 2. Scope

### Included

- Reproduction of the four-compartment deterministic model.
- Three behavioural regimes controlled by the worried-well contact modifier.
- Conversion of compartment trajectories into expected daily service demand.
- Non-negative stochastic demand scenarios.
- Scenario-based and quantile-based newsvendor solutions.
- Sensitivity analysis for behaviour, uncertainty, shortage/overage costs, service-seeking rates, and initial conditions.
- Reproducible tables and figures suitable for use as evidence in the final report.
- Numerical and structural checks for the ODE, demand generator, and optimizer.

### Excluded

- Parameter estimation from patient-level data.
- Geographic network or multi-region coupling.
- Age structure, mortality, births, and migration.
- Multi-resource allocation, queueing, staffing rosters, or dynamic inventory carry-over.
- A full stochastic differential equation model.
- Claims that synthetic outputs are forecasts of a real outbreak.

These exclusions keep the project aligned with the brief's request for a simple stochastic extension and a simple newsvendor model.

## 3. Deterministic Compartmental Model

Let the population fractions be:

- \(S(t)\): susceptible to both pathogen and worry;
- \(I_P(t)\): genuinely infected by the pathogen;
- \(I_W(t)\): worried-well, worried but not pathogen-infected; and
- \(R_P(t)\): recovered from pathogen infection.

The model is:

\[
\frac{dS}{dt}
=-(\beta_P+\beta_{WP})SI_P-\beta_WSI_W+\delta_PR_P+\gamma_WI_W,
\]

\[
\frac{dI_P}{dt}
=\beta_PSI_P+\alpha\beta_PI_PI_W-\gamma_PI_P,
\]

\[
\frac{dI_W}{dt}
=-\alpha\beta_PI_PI_W+\beta_WSI_W+\beta_{WP}SI_P-\gamma_WI_W,
\]

\[
\frac{dR_P}{dt}
=\gamma_PI_P-\delta_PR_P.
\]

The baseline parameters are:

| Parameter | Baseline | Interpretation |
|---|---:|---|
| \(\beta_P\) | 0.74 day\(^{-1}\) | Pathogen transmission coefficient |
| \(\beta_W\) | 0.70 day\(^{-1}\) | Worry transmission from worried-well contact |
| \(\beta_{WP}\) | 0.70 day\(^{-1}\) | Worry transmission from infected contact |
| \(\gamma_P\) | \(1/14\) day\(^{-1}\) | Pathogen recovery rate |
| \(\gamma_W\) | \(1/14\) day\(^{-1}\) | Worry recovery rate |
| \(\delta_P\) | \(1/240\) day\(^{-1}\) | Loss-of-immunity rate |
| \(I_P(0)\) | 0.01 | Initially infected fraction |
| \(I_W(0)\) | 0.01 | Initially worried-well fraction |
| \(R_P(0)\) | 0 | Initially recovered fraction |
| \(S(0)\) | 0.98 | Remaining population fraction |

The primary behavioural regimes are:

- cautious: \(\alpha=0.5\);
- default: \(\alpha=1.0\); and
- protesting/high-contact: \(\alpha=2.0\).

The main time horizon is 50 days because the source figures use a horizontal axis labelled in days. The source figure captions' reference to 50 weeks will be treated as an apparent labelling inconsistency and will not be silently reproduced.

## 4. Healthcare Demand Model

Let \(N=100{,}000\) be a synthetic regional population. The expected number of people seeking consultation or diagnostic service on day \(t\) is:

\[
\mu_t=N\left(p_PI_P(t)+p_WI_W(t)\right).
\]

The baseline service-seeking probabilities are:

- \(p_P=1.0\): each genuinely infected individual represents one unit of potential service demand;
- \(p_W=0.5\): half of the worried-well population seeks a consultation or diagnostic appointment.

The values are modelling assumptions, not empirical estimates. Results will therefore be reported as synthetic scenario analysis and will include sensitivity analysis for \(p_W\).

For day \(t\) and scenario \(s\), demand follows a lower-truncated normal distribution:

\[
D_{t,s}\sim
\operatorname{TruncatedNormal}
\left(\mu_t,(\sigma\mu_t)^2;D_{t,s}\ge0\right).
\]

Generated values are rounded to non-negative integers because capacity is measured in appointment slots. A fixed random seed makes every published experiment reproducible.

The baseline coefficient of variation is \(\sigma=0.15\). The main uncertainty levels are \(0.05\), \(0.15\), and \(0.30\). This explicit truncated distribution resolves the brief's mathematically ambiguous example of a normally distributed variable constrained between zero and one.

## 5. Newsvendor Model

For each day \(t\), choose an integer capacity \(q_t\ge0\). The scenario-based objective is:

\[
\min_{q_t\in\mathbb{Z}_{\ge0}}
\frac{1}{M}\sum_{s=1}^{M}
\left[
c_u(D_{t,s}-q_t)^+
+c_o(q_t-D_{t,s})^+
\right],
\]

where:

- \(c_u>0\) is the cost per unit of unmet demand;
- \(c_o>0\) is the cost per unit of unused capacity;
- \((x)^+=\max(x,0)\); and
- \(M\) is the number of demand scenarios.

The baseline costs are \(c_u=5\) and \(c_o=1\), so shortage is five times as costly as overage. The corresponding critical fractile is:

\[
\tau=\frac{c_u}{c_u+c_o}.
\]

For continuous demand, the analytical optimum is the \(\tau\)-quantile. For empirical integer scenarios, the implementation will use an empirical quantile and verify it against direct enumeration of nearby integer capacities. This produces both a fast solution and an independent correctness check.

This is a repeated single-period model: each day is a separate planning decision and unused capacity is not carried into the next day. The interpretation is daily appointment capacity, not physical inventory.

## 6. Experiment Design

### Experiment 1: Deterministic reproduction

Run \(\alpha\in\{0.5,1.0,2.0\}\) with baseline parameters. Report:

- trajectories of \(S,I_P,I_W,R_P\);
- total potential pressure \(I_P+I_W\);
- risk ratio \(I_W/I_P\), with undefined values handled explicitly when \(I_P=0\);
- peak sizes and peak days.

### Experiment 2: Demand uncertainty

For each behavioural regime, vary:

\[
\sigma\in\{0.05,0.15,0.30\}.
\]

Report how uncertainty changes optimal capacity, expected cost, shortage probability, expected shortage, and expected unused capacity.

### Experiment 3: Cost asymmetry

Use:

| Scenario | \(c_u\) | \(c_o\) | Critical fractile |
|---|---:|---:|---:|
| Balanced | 1 | 1 | 0.50 |
| Moderate shortage penalty | 5 | 1 | 0.83 |
| Severe shortage penalty | 10 | 1 | 0.91 |

Report how the service level and optimal capacity respond to the shortage penalty.

### Experiment 4: Worried-well service-seeking

Use:

\[
p_W\in\{0.25,0.50,0.75,1.00\}.
\]

This experiment measures how psychological demand changes resource requirements even when pathogen dynamics are unchanged.

### Experiment 5: Initial-condition sensitivity

Compare:

- \(I_P(0)=0.01,\ I_W(0)=0.001\);
- \(I_P(0)=0.01,\ I_W(0)=0.01\); and
- \(I_P(0)=0.001,\ I_W(0)=0.01\).

The remaining fraction is assigned to \(S(0)\), with \(R_P(0)=0\).

### Policy benchmark

Compare optimized capacity with a mean-demand policy:

\[
q_t^{\text{mean}}=\operatorname{round}(\mu_t).
\]

Use identical out-of-sample demand scenarios for both policies. Report relative cost reduction:

\[
100\frac{C_{\text{mean}}-C_{\text{opt}}}{C_{\text{mean}}}.
\]

## 7. Software Architecture

The implementation will use Python with NumPy, SciPy, pandas, and Matplotlib.

Proposed components:

- `src/compartment_model.py`: parameters, differential equations, ODE solution, and conservation diagnostics.
- `src/demand.py`: expected demand conversion and stochastic scenario generation.
- `src/newsvendor.py`: cost calculation, empirical quantile solution, and enumeration cross-check.
- `src/experiments.py`: experiment definitions and tidy result tables.
- `src/plots.py`: publication-ready figures with consistent labels and units.
- `scripts/run_analysis.py`: one command that regenerates all results.
- `tests/`: unit and regression tests.
- `outputs/data/`: generated CSV tables.
- `outputs/figures/`: generated figures.
- `report/`: report outline and later report source.

Model logic, experiments, and presentation are separated so that changing one assumption does not require rewriting the entire analysis.

## 8. Data Flow

1. Load a validated parameter set.
2. Solve the deterministic ODE on a common daily time grid.
3. Check state bounds and population conservation.
4. Convert \(I_P(t)\) and \(I_W(t)\) into expected demand \(\mu_t\).
5. Generate seeded non-negative integer demand scenarios.
6. Solve the daily newsvendor problem.
7. Evaluate optimized and benchmark policies on separate out-of-sample scenarios.
8. Save tidy tables and figures with scenario metadata.
9. Use only saved, reproducible results as quantitative evidence in the report.

## 9. Validation and Error Handling

### Input validation

- All rates must be non-negative.
- \(\alpha,N,p_P,p_W,c_u,c_o,M\) must be positive where required.
- \(p_P,p_W\in[0,1]\).
- Initial fractions must be in \([0,1]\) and sum to one within tolerance.
- Random seeds and experiment identifiers must be recorded.

### ODE validation

- \(S+I_P+I_W+R_P=1\) within numerical tolerance at every time point.
- States remain within a small numerical tolerance of \([0,1]\).
- Initial values are reproduced exactly.
- Baseline qualitative ordering is checked against the source paper without claiming exact graphical duplication.

### Demand validation

- Every demand scenario is finite, non-negative, and integer-valued.
- Zero expected demand produces zero demand without numerical errors.
- Sample means and standard deviations are checked against the requested distribution within Monte Carlo tolerance.

### Optimization validation

- Costs are non-negative.
- Empirical-quantile capacity is compared with direct enumeration.
- The selected integer capacity has no higher sample cost than its adjacent feasible capacities.
- Optimized capacity is non-decreasing as the critical fractile increases for a fixed demand sample.
- Benchmark comparison uses common out-of-sample scenarios.

## 10. Outputs

Minimum planned evidence:

1. one compartment trajectory figure comparing behavioural regimes;
2. one \(I_W/I_P\) ratio figure;
3. one expected-demand and uncertainty-band figure;
4. one optimal-capacity figure;
5. one sensitivity figure for uncertainty and cost asymmetry;
6. one table of peak values and days;
7. one table comparing optimized and mean-demand policies; and
8. one table summarizing assumptions and parameter sources.

Every figure will state units, scenario, and parameter values. Every table will be generated from saved results rather than manually transcribed.

## 11. Report Structure

The report will follow this evidence chain:

1. **Introduction and motivation**: worried-well demand and the operational decision.
2. **Literature review**: worried-well behaviour, compartmental modelling, stochastic demand, and the classical newsvendor problem.
3. **Deterministic model**: compartments, equations, parameters, assumptions, and reproduction results.
4. **Stochastic demand model**: service-seeking conversion, distribution choice, and synthetic-data limitations.
5. **Newsvendor formulation**: decision, objective, constraints, critical fractile, and benchmark.
6. **Experimental design**: scenarios, performance measures, and reproducibility.
7. **Results**: behaviour, uncertainty, costs, service-seeking, and initial-condition sensitivity.
8. **Discussion**: healthcare implications, limitations, and extensions.
9. **Conclusion**: main decision insights.

The strongest emphasis will be on the newsvendor formulation and the interpretation of computational experiments because these components jointly account for most of the assessment guidance.

## 12. Success Criteria

The project is successful when:

- the deterministic model is reproduced with conservation and state-bound checks passing;
- stochastic scenarios are reproducible and mathematically consistent;
- newsvendor solutions pass independent enumeration checks;
- all five experiment groups can be regenerated with one command;
- results distinguish infection-driven and worry-driven healthcare pressure;
- every quantitative report claim traces to a saved table or figure; and
- limitations clearly distinguish synthetic scenario analysis from empirical forecasting.
