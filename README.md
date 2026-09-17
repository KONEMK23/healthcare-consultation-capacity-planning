# Healthcare Consultation Capacity Planning and Stochastic Optimisation

This project reproduces the Singh-Gromov worried-well compartment model,
converts the trajectories into synthetic daily consultation demand, and solves
a repeated single-period newsvendor capacity problem.

## Setup

Use Python 3.11 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

The analysis was also tested with an Anaconda Python 3.12 interpreter; activate
the corresponding Conda environment before running the same install command.

## Verify

```powershell
python -m pytest -v
```

## Regenerate all evidence

```powershell
python scripts/run_analysis.py
```

The command writes CSV evidence to `outputs/data` and figures to
`outputs/figures`. Every experiment uses synthetic data and a recorded random
seed; outputs are scenario analysis rather than real-world forecasts.
Continuous demand draws are converted to appointment counts with seeded
stochastic rounding, which preserves the requested mean without silently
rounding small positive means to zero.

## Report evidence

- The planned report structure is in `report/outline.md`.
- `report/literature-matrix.csv` records the role and limitation of each starting source.
- `report/evidence-map.csv` links each planned quantitative claim to a generated
  table or figure.
- Re-run the analysis before drafting results so every number is current.
