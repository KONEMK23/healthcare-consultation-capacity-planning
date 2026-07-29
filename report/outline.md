# MATH6186 Case Study Report Outline

## 1. Introduction

Define the worried-well problem, explain why consultation capacity is an
operational decision, and state the research question:

> How should daily consultation capacity change when worried-well behaviour,
> demand uncertainty, and shortage costs vary during the early outbreak?

## 2. Literature Review

Organize the review into worried-well behaviour, behavioural compartmental
models, stochastic healthcare demand, and the classical newsvendor model.
Conclude by identifying the connection made in this project.

## 3. Deterministic Model

Present the four equations, parameter table, behavioural regimes, initial
conditions, conservation assumption, and the 50-day horizon.

## 4. Stochastic Demand

Define the service-seeking equation, explain the synthetic population and
service-seeking assumptions, define the mean-matched truncated normal
distribution, and explain the fixed seed.

## 5. Newsvendor Formulation

Define daily capacity, underage and overage costs, the sample-average objective,
the critical fractile, integer rounding, and the mean-demand benchmark.

## 6. Experimental Design

Describe the five experiment groups, in-sample optimization scenarios,
out-of-sample evaluation scenarios, common random numbers, and performance
measures.

## 7. Results

### 7.1 Behavioural regimes

Use Figures 1, 2, and 4 plus the peak-value columns in `summary.csv`.

### 7.2 Demand uncertainty

Use Figure 3 and the uncertainty rows in `daily_metrics.csv`.

### 7.3 Cost and service-level sensitivity

Use Figure 5 and the cost rows in `summary.csv`.

### 7.4 Worried-well service-seeking and initial conditions

Use the corresponding scenario groups in `summary.csv`.

### 7.5 Optimized policy versus mean-demand policy

Use the three policy-cost columns in `summary.csv`.

## 8. Discussion

Interpret operational implications, explain why psychological demand changes
capacity even without increasing infections, and discuss synthetic-data,
single-resource, repeated-single-period, and parameter-assumption limitations.

## 9. Conclusion

Answer the research question using only results traceable to generated evidence.
