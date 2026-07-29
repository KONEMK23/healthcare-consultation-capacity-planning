# MATH6186 Worried-Well Capacity Project

This project reproduces the Singh-Gromov worried-well compartment model,
converts the trajectories into synthetic daily consultation demand, and solves
a repeated single-period newsvendor capacity problem.

## Setup

```powershell
& "D:\ProgramData\anaconda3\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

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
