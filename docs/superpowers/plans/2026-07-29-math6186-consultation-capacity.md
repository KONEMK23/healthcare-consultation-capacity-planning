# MATH6186 Consultation Capacity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested, reproducible Python analysis that converts worried-well compartment trajectories into stochastic daily consultation demand and optimized newsvendor capacity decisions.

**Architecture:** A small `math6186` package separates parameter validation, ODE simulation, demand generation, newsvendor optimization, experiments, and plotting. A single command runs the full deterministic-to-stochastic data flow, evaluates optimized and benchmark policies on common out-of-sample scenarios, and writes traceable CSV and PNG evidence for the report.

**Tech Stack:** Python 3.11+, NumPy, SciPy, pandas, Matplotlib, pytest, setuptools

## Global Constraints

- Model exactly four population fractions: `S`, `I_P`, `I_W`, and `R_P`.
- Use a 50-day horizon with an integer daily output grid from day 0 through day 50.
- Use baseline population `100_000`, `p_infected=1.0`, `p_worried=0.5`, coefficient of variation `0.15`, underage cost `5.0`, and overage cost `1.0`.
- Use behavioural values `alpha in {0.5, 1.0, 2.0}`.
- Use non-negative integer demand generated from a lower-truncated normal distribution whose mean equals deterministic demand.
- Use fixed and recorded random seeds; published results use seed `6186`.
- Evaluate optimized and mean-demand policies on identical out-of-sample scenarios.
- Treat outputs as synthetic scenario analysis, not empirical forecasts.
- Keep model, demand, optimization, experiments, presentation, and report evidence in separate files.

## File Map

- `pyproject.toml`: package metadata, dependencies, and pytest configuration.
- `src/math6186/__init__.py`: public package exports and version.
- `src/math6186/config.py`: validated dataclasses shared across components.
- `src/math6186/compartment_model.py`: ODE right-hand side, simulation, and diagnostics.
- `src/math6186/demand.py`: deterministic demand conversion and truncated-normal scenarios.
- `src/math6186/newsvendor.py`: critical fractile, sample cost, capacity solution, and policy metrics.
- `src/math6186/experiments.py`: experiment definitions, execution, and tidy result tables.
- `src/math6186/plots.py`: five publication-ready figure builders.
- `scripts/run_analysis.py`: complete reproducible analysis command.
- `tests/test_config.py`: parameter validation tests.
- `tests/test_compartment_model.py`: conservation, bounds, and qualitative reproduction tests.
- `tests/test_demand.py`: distribution, shape, non-negativity, and reproducibility tests.
- `tests/test_newsvendor.py`: optimizer and cost tests.
- `tests/test_experiments.py`: grid and benchmark comparison tests.
- `tests/test_plots.py`: figure construction and file-output tests.
- `tests/test_run_analysis.py`: end-to-end smoke and reproducibility tests.
- `outputs/data/`: generated CSV evidence.
- `outputs/figures/`: generated PNG figures.
- `report/outline.md`: report structure and evidence mapping.
- `report/literature-matrix.csv`: structured source notes for the four literature-review themes.
- `README.md`: environment setup and one-command reproduction instructions.

---

### Task 1: Project Foundation and Validated Configuration

**Files:**
- Create: `pyproject.toml`
- Create: `src/math6186/__init__.py`
- Create: `src/math6186/config.py`
- Create: `tests/test_config.py`

**Interfaces:**
- Consumes: no earlier task.
- Produces: `ModelParameters`, `DemandParameters`, and `NewsvendorCosts` dataclasses used by every later task.

- [ ] **Step 1: Write the failing configuration tests**

```python
# tests/test_config.py
import pytest

from math6186.config import DemandParameters, ModelParameters, NewsvendorCosts


def test_model_defaults_sum_to_one():
    params = ModelParameters()
    assert params.initial_state == pytest.approx((0.98, 0.01, 0.01, 0.0))
    assert sum(params.initial_state) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("field", "value"),
    [("beta_p", -0.1), ("gamma_w", -0.1), ("alpha", 0.0)],
)
def test_model_rejects_invalid_rates(field, value):
    values = {field: value}
    with pytest.raises(ValueError):
        ModelParameters(**values)


def test_model_rejects_initial_state_that_does_not_sum_to_one():
    with pytest.raises(ValueError, match="sum to one"):
        ModelParameters(initial_state=(0.9, 0.01, 0.01, 0.0))


def test_model_rejects_initial_state_with_wrong_length():
    with pytest.raises(ValueError, match="four values"):
        ModelParameters(initial_state=(0.98, 0.01, 0.01))


@pytest.mark.parametrize("field", ["p_infected", "p_worried"])
def test_demand_rejects_probabilities_above_one(field):
    with pytest.raises(ValueError):
        DemandParameters(**{field: 1.1})


def test_demand_rejects_unsupported_cv_and_negative_seed():
    with pytest.raises(ValueError, match="coefficient_of_variation"):
        DemandParameters(coefficient_of_variation=1.1)
    with pytest.raises(ValueError, match="seed"):
        DemandParameters(seed=-1)


def test_costs_expose_critical_fractile():
    costs = NewsvendorCosts(underage=5.0, overage=1.0)
    assert costs.critical_fractile == pytest.approx(5.0 / 6.0)
```

- [ ] **Step 2: Add package configuration and run the test to verify failure**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "math6186-worried-well"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "numpy>=1.26",
  "scipy>=1.11",
  "pandas>=2.1",
  "matplotlib>=3.8",
]

[project.optional-dependencies]
test = ["pytest>=8.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

Run:

```powershell
python -m pip install -e ".[test]"
python -m pytest tests/test_config.py -v
```

Expected: collection fails because `math6186.config` does not exist.

- [ ] **Step 3: Implement the validated dataclasses**

```python
# src/math6186/config.py
from dataclasses import dataclass
from math import isclose


@dataclass(frozen=True)
class ModelParameters:
    beta_p: float = 0.74
    beta_w: float = 0.70
    beta_wp: float = 0.70
    gamma_p: float = 1.0 / 14.0
    gamma_w: float = 1.0 / 14.0
    delta_p: float = 1.0 / 240.0
    alpha: float = 1.0
    initial_state: tuple[float, float, float, float] = (0.98, 0.01, 0.01, 0.0)

    def __post_init__(self) -> None:
        rates = (
            self.beta_p,
            self.beta_w,
            self.beta_wp,
            self.gamma_p,
            self.gamma_w,
            self.delta_p,
        )
        if any(rate < 0.0 for rate in rates):
            raise ValueError("Transition rates must be non-negative.")
        if self.alpha <= 0.0:
            raise ValueError("alpha must be positive.")
        if len(self.initial_state) != 4:
            raise ValueError("initial_state must contain four values.")
        if any(value < 0.0 or value > 1.0 for value in self.initial_state):
            raise ValueError("Initial fractions must lie in [0, 1].")
        if not isclose(sum(self.initial_state), 1.0, abs_tol=1e-12):
            raise ValueError("Initial fractions must sum to one.")


@dataclass(frozen=True)
class DemandParameters:
    population: int = 100_000
    p_infected: float = 1.0
    p_worried: float = 0.5
    coefficient_of_variation: float = 0.15
    scenarios: int = 5_000
    seed: int = 6_186

    def __post_init__(self) -> None:
        if self.population <= 0 or self.scenarios <= 0:
            raise ValueError("population and scenarios must be positive.")
        if not 0.0 <= self.p_infected <= 1.0:
            raise ValueError("p_infected must lie in [0, 1].")
        if not 0.0 <= self.p_worried <= 1.0:
            raise ValueError("p_worried must lie in [0, 1].")
        if not 0.0 < self.coefficient_of_variation <= 1.0:
            raise ValueError("coefficient_of_variation must lie in (0, 1].")
        if self.seed < 0:
            raise ValueError("seed must be non-negative.")


@dataclass(frozen=True)
class NewsvendorCosts:
    underage: float = 5.0
    overage: float = 1.0

    def __post_init__(self) -> None:
        if self.underage <= 0.0 or self.overage <= 0.0:
            raise ValueError("underage and overage costs must be positive.")

    @property
    def critical_fractile(self) -> float:
        return self.underage / (self.underage + self.overage)
```

```python
# src/math6186/__init__.py
from math6186.config import DemandParameters, ModelParameters, NewsvendorCosts

__all__ = ["DemandParameters", "ModelParameters", "NewsvendorCosts"]
__version__ = "0.1.0"
```

- [ ] **Step 4: Run the configuration tests**

Run: `python -m pytest tests/test_config.py -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the project foundation**

```powershell
git add pyproject.toml src/math6186/__init__.py src/math6186/config.py tests/test_config.py
git commit -m "build: add validated project configuration"
```

---

### Task 2: Deterministic Compartmental Model

**Files:**
- Create: `src/math6186/compartment_model.py`
- Create: `tests/test_compartment_model.py`

**Interfaces:**
- Consumes: `ModelParameters` from Task 1.
- Produces: `compartment_rhs(t, state, params) -> numpy.ndarray` and `simulate(params, days=50, step_days=1) -> pandas.DataFrame`.

- [ ] **Step 1: Write failing conservation and simulation tests**

```python
# tests/test_compartment_model.py
import numpy as np
import pytest

from math6186.compartment_model import compartment_rhs, simulate
from math6186.config import ModelParameters


def test_rhs_conserves_population():
    params = ModelParameters()
    derivative = compartment_rhs(0.0, np.array(params.initial_state), params)
    assert derivative.sum() == pytest.approx(0.0, abs=1e-12)


def test_simulation_has_daily_grid_and_conserves_population():
    result = simulate(ModelParameters(), days=50, step_days=1)
    assert result["day"].tolist() == list(range(51))
    assert np.allclose(result[["S", "I_P", "I_W", "R_P"]].sum(axis=1), 1.0, atol=1e-7)
    assert result[["S", "I_P", "I_W", "R_P"]].to_numpy().min() >= -1e-8
    assert result[["S", "I_P", "I_W", "R_P"]].to_numpy().max() <= 1.0 + 1e-8


def test_simulation_reproduces_initial_state():
    params = ModelParameters()
    first = simulate(params).iloc[0]
    assert tuple(first[["S", "I_P", "I_W", "R_P"]]) == pytest.approx(params.initial_state)


def test_cautious_regime_reduces_infected_peak_relative_to_protesting():
    cautious = simulate(ModelParameters(alpha=0.5))
    protesting = simulate(ModelParameters(alpha=2.0))
    assert cautious["I_P"].max() < protesting["I_P"].max()
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `python -m pytest tests/test_compartment_model.py -v`

Expected: collection fails because `math6186.compartment_model` does not exist.

- [ ] **Step 3: Implement the ODE and diagnostics**

```python
# src/math6186/compartment_model.py
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from math6186.config import ModelParameters


STATE_COLUMNS = ["S", "I_P", "I_W", "R_P"]


def compartment_rhs(
    _time: float,
    state: np.ndarray,
    params: ModelParameters,
) -> np.ndarray:
    susceptible, infected, worried, recovered = state
    d_susceptible = (
        -(params.beta_p + params.beta_wp) * susceptible * infected
        - params.beta_w * susceptible * worried
        + params.delta_p * recovered
        + params.gamma_w * worried
    )
    d_infected = (
        params.beta_p * susceptible * infected
        + params.alpha * params.beta_p * infected * worried
        - params.gamma_p * infected
    )
    d_worried = (
        -params.alpha * params.beta_p * infected * worried
        + params.beta_w * susceptible * worried
        + params.beta_wp * susceptible * infected
        - params.gamma_w * worried
    )
    d_recovered = params.gamma_p * infected - params.delta_p * recovered
    return np.array([d_susceptible, d_infected, d_worried, d_recovered])


def simulate(
    params: ModelParameters,
    days: int = 50,
    step_days: int = 1,
) -> pd.DataFrame:
    if days <= 0 or step_days <= 0 or days % step_days != 0:
        raise ValueError("days must be positive and divisible by step_days.")
    evaluation_days = np.arange(0, days + step_days, step_days, dtype=float)
    solution = solve_ivp(
        compartment_rhs,
        (0.0, float(days)),
        params.initial_state,
        args=(params,),
        t_eval=evaluation_days,
        method="DOP853",
        rtol=1e-9,
        atol=1e-11,
    )
    if not solution.success:
        raise RuntimeError(f"ODE solver failed: {solution.message}")
    states = solution.y.T
    totals = states.sum(axis=1)
    if not np.allclose(totals, 1.0, atol=1e-7):
        raise RuntimeError("Population conservation check failed.")
    if states.min() < -1e-8 or states.max() > 1.0 + 1e-8:
        raise RuntimeError("Compartment state bounds check failed.")
    frame = pd.DataFrame(states, columns=STATE_COLUMNS)
    frame.insert(0, "day", evaluation_days.astype(int))
    frame["total"] = totals
    frame["pressure"] = frame["I_P"] + frame["I_W"]
    frame["risk_ratio"] = np.divide(
        frame["I_W"].to_numpy(),
        frame["I_P"].to_numpy(),
        out=np.full(len(frame), np.nan),
        where=frame["I_P"].to_numpy() > 1e-12,
    )
    return frame
```

- [ ] **Step 4: Run the model tests**

Run: `python -m pytest tests/test_compartment_model.py -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the deterministic model**

```powershell
git add src/math6186/compartment_model.py tests/test_compartment_model.py
git commit -m "feat: implement worried-well compartment model"
```

---

### Task 3: Stochastic Consultation Demand

**Files:**
- Create: `src/math6186/demand.py`
- Create: `tests/test_demand.py`

**Interfaces:**
- Consumes: a trajectory DataFrame from `simulate` and `DemandParameters`.
- Produces: `expected_demand(trajectory, params) -> pandas.Series` and `generate_scenarios(means, params) -> numpy.ndarray` with shape `(days, scenarios)`.

- [ ] **Step 1: Write failing demand tests**

```python
# tests/test_demand.py
import numpy as np
import pandas as pd
import pytest

from math6186.config import DemandParameters
from math6186.demand import expected_demand, generate_scenarios


def test_expected_demand_weights_infected_and_worried():
    trajectory = pd.DataFrame({"I_P": [0.01], "I_W": [0.02]})
    params = DemandParameters(population=100_000, p_infected=1.0, p_worried=0.5)
    assert expected_demand(trajectory, params).iloc[0] == pytest.approx(2_000.0)


def test_scenarios_are_non_negative_integer_and_reproducible():
    means = np.array([0.0, 100.0, 1_000.0])
    params = DemandParameters(scenarios=2_000, seed=123)
    first = generate_scenarios(means, params)
    second = generate_scenarios(means, params)
    assert first.shape == (3, 2_000)
    assert np.array_equal(first, second)
    assert np.issubdtype(first.dtype, np.integer)
    assert first.min() >= 0
    assert np.count_nonzero(first[0]) == 0


def test_truncated_distribution_preserves_requested_mean():
    means = np.array([1_000.0])
    params = DemandParameters(
        coefficient_of_variation=0.30,
        scenarios=100_000,
        seed=321,
    )
    draws = generate_scenarios(means, params)[0]
    assert draws.mean() == pytest.approx(1_000.0, rel=0.01)
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `python -m pytest tests/test_demand.py -v`

Expected: collection fails because `math6186.demand` does not exist.

- [ ] **Step 3: Implement mean-matched lower-truncated demand**

```python
# src/math6186/demand.py
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm, truncnorm

from math6186.config import DemandParameters


def expected_demand(
    trajectory: pd.DataFrame,
    params: DemandParameters,
) -> pd.Series:
    missing = {"I_P", "I_W"} - set(trajectory.columns)
    if missing:
        raise ValueError(f"Trajectory is missing columns: {sorted(missing)}")
    means = params.population * (
        params.p_infected * trajectory["I_P"]
        + params.p_worried * trajectory["I_W"]
    )
    if not np.isfinite(means).all() or (means < 0.0).any():
        raise ValueError("Expected demand must be finite and non-negative.")
    return means.rename("mean_demand")


def _standardized_location(coefficient_of_variation: float) -> float:
    target = 1.0 / coefficient_of_variation

    def mean_equation(location_in_sd: float) -> float:
        inverse_mills = norm.pdf(location_in_sd) / norm.cdf(location_in_sd)
        return location_in_sd + inverse_mills - target

    return brentq(mean_equation, -10.0, target)


def generate_scenarios(
    means: np.ndarray | pd.Series,
    params: DemandParameters,
) -> np.ndarray:
    requested_means = np.asarray(means, dtype=float)
    if requested_means.ndim != 1:
        raise ValueError("means must be one-dimensional.")
    if not np.isfinite(requested_means).all() or (requested_means < 0.0).any():
        raise ValueError("means must be finite and non-negative.")
    output = np.zeros((requested_means.size, params.scenarios), dtype=np.int64)
    positive = requested_means > 0.0
    if not positive.any():
        return output
    cv = params.coefficient_of_variation
    location_in_sd = _standardized_location(cv)
    rng = np.random.default_rng(params.seed)
    for row_index in np.flatnonzero(positive):
        requested_mean = requested_means[row_index]
        scale = cv * requested_mean
        location = location_in_sd * scale
        lower_standardized = -location_in_sd
        draws = truncnorm.rvs(
            lower_standardized,
            np.inf,
            loc=location,
            scale=scale,
            size=params.scenarios,
            random_state=rng,
        )
        output[row_index] = np.maximum(0, np.rint(draws)).astype(np.int64)
    return output
```

- [ ] **Step 4: Run the demand tests**

Run: `python -m pytest tests/test_demand.py -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the stochastic demand model**

```powershell
git add src/math6186/demand.py tests/test_demand.py
git commit -m "feat: generate reproducible stochastic demand"
```

---

### Task 4: Newsvendor Optimization and Policy Evaluation

**Files:**
- Create: `src/math6186/newsvendor.py`
- Create: `tests/test_newsvendor.py`

**Interfaces:**
- Consumes: one- or two-dimensional integer demand arrays and `NewsvendorCosts`.
- Produces: `sample_cost`, `optimal_capacity`, `enumerated_optimum`, and `evaluate_daily_policy`.

- [ ] **Step 1: Write failing optimizer tests**

```python
# tests/test_newsvendor.py
import numpy as np
import pytest

from math6186.config import NewsvendorCosts
from math6186.newsvendor import (
    enumerated_optimum,
    evaluate_daily_policy,
    optimal_capacity,
    sample_cost,
)


def test_sample_cost_uses_underage_and_overage_terms():
    demand = np.array([8, 10, 12])
    costs = NewsvendorCosts(underage=5.0, overage=1.0)
    assert sample_cost(demand, 10, costs) == pytest.approx((2 + 0 + 10) / 3)


def test_quantile_solution_matches_full_enumeration():
    demand = np.array([0, 2, 3, 4, 10, 12])
    costs = NewsvendorCosts(underage=5.0, overage=1.0)
    quantile_capacity = optimal_capacity(demand, costs)
    enumerated_capacity = enumerated_optimum(demand, costs)
    assert sample_cost(demand, quantile_capacity, costs) == pytest.approx(
        sample_cost(demand, enumerated_capacity, costs)
    )


def test_capacity_is_non_decreasing_with_shortage_penalty():
    demand = np.arange(20)
    balanced = optimal_capacity(demand, NewsvendorCosts(1.0, 1.0))
    severe = optimal_capacity(demand, NewsvendorCosts(10.0, 1.0))
    assert severe >= balanced


def test_daily_policy_metrics_have_expected_values():
    demand = np.array([[8, 10, 12], [1, 1, 1]])
    capacities = np.array([10, 1])
    result = evaluate_daily_policy(demand, capacities, NewsvendorCosts(5.0, 1.0))
    assert result.loc[0, "shortage_probability"] == pytest.approx(1.0 / 3.0)
    assert result.loc[1, "expected_cost"] == pytest.approx(0.0)
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `python -m pytest tests/test_newsvendor.py -v`

Expected: collection fails because `math6186.newsvendor` does not exist.

- [ ] **Step 3: Implement cost, quantile, enumeration, and metrics**

```python
# src/math6186/newsvendor.py
from __future__ import annotations

import numpy as np
import pandas as pd

from math6186.config import NewsvendorCosts


def _validated_demand(demand: np.ndarray) -> np.ndarray:
    values = np.asarray(demand)
    if values.size == 0 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Demand must be non-empty, finite, and non-negative.")
    return values


def sample_cost(
    demand: np.ndarray,
    capacity: int,
    costs: NewsvendorCosts,
) -> float:
    values = _validated_demand(demand)
    if capacity < 0:
        raise ValueError("capacity must be non-negative.")
    shortage = np.maximum(values - capacity, 0)
    unused = np.maximum(capacity - values, 0)
    return float(np.mean(costs.underage * shortage + costs.overage * unused))


def optimal_capacity(demand: np.ndarray, costs: NewsvendorCosts) -> int:
    values = _validated_demand(np.asarray(demand).reshape(-1))
    quantile = np.quantile(values, costs.critical_fractile, method="higher")
    return int(quantile)


def enumerated_optimum(demand: np.ndarray, costs: NewsvendorCosts) -> int:
    values = _validated_demand(np.asarray(demand).reshape(-1))
    candidates = np.arange(0, int(values.max()) + 1)
    sample_costs = np.array([sample_cost(values, int(q), costs) for q in candidates])
    return int(candidates[np.argmin(sample_costs)])


def evaluate_daily_policy(
    demand: np.ndarray,
    capacities: np.ndarray,
    costs: NewsvendorCosts,
) -> pd.DataFrame:
    values = _validated_demand(demand)
    selected = np.asarray(capacities, dtype=int)
    if values.ndim != 2 or selected.shape != (values.shape[0],):
        raise ValueError("capacities must contain one value per demand row.")
    if (selected < 0).any():
        raise ValueError("capacities must be non-negative.")
    shortage = np.maximum(values - selected[:, None], 0)
    unused = np.maximum(selected[:, None] - values, 0)
    cost = costs.underage * shortage + costs.overage * unused
    return pd.DataFrame(
        {
            "capacity": selected,
            "expected_cost": cost.mean(axis=1),
            "shortage_probability": (shortage > 0).mean(axis=1),
            "expected_shortage": shortage.mean(axis=1),
            "expected_unused": unused.mean(axis=1),
        }
    )
```

- [ ] **Step 4: Run the optimizer tests**

Run: `python -m pytest tests/test_newsvendor.py -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the newsvendor component**

```powershell
git add src/math6186/newsvendor.py tests/test_newsvendor.py
git commit -m "feat: optimize daily consultation capacity"
```

---

### Task 5: Experiment Grid and Out-of-Sample Benchmark

**Files:**
- Create: `src/math6186/experiments.py`
- Create: `tests/test_experiments.py`

**Interfaces:**
- Consumes: all model, demand, and optimizer interfaces from Tasks 1-4.
- Produces: `ExperimentConfig`, `build_experiment_grid()`, `run_experiment(config)`, and `run_all_experiments()` returning tidy trajectory, daily, summary, and parameter tables.

- [ ] **Step 1: Write failing experiment tests**

```python
# tests/test_experiments.py
import pandas as pd

from math6186.experiments import build_experiment_grid, run_all_experiments


def test_grid_contains_all_required_experiment_groups():
    grid = build_experiment_grid()
    assert set(grid["group"]) == {
        "behaviour",
        "uncertainty",
        "cost",
        "service_seeking",
        "initial_condition",
    }
    assert set(grid.loc[grid["group"] == "behaviour", "alpha"]) == {0.5, 1.0, 2.0}
    assert set(grid.loc[grid["group"] == "uncertainty", "cv"]) == {0.05, 0.15, 0.30}
    assert set(grid.loc[grid["group"] == "service_seeking", "p_worried"]) == {
        0.25,
        0.50,
        0.75,
        1.00,
    }


def test_run_all_experiments_returns_traceable_tables():
    outputs = run_all_experiments(in_sample=200, out_sample=300)
    assert set(outputs) == {"trajectories", "daily_metrics", "summary", "parameters"}
    assert all(isinstance(table, pd.DataFrame) for table in outputs.values())
    assert not outputs["summary"].empty
    assert {
        "optimized_total_cost",
        "mean_policy_total_cost",
        "relative_cost_reduction_pct",
    } <= set(outputs["summary"].columns)
    assert outputs["summary"][
        ["optimized_total_cost", "mean_policy_total_cost", "relative_cost_reduction_pct"]
    ].notna().all().all()
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `python -m pytest tests/test_experiments.py -v`

Expected: collection fails because `math6186.experiments` does not exist.

- [ ] **Step 3: Implement the experiment configuration and runner**

```python
# src/math6186/experiments.py
from __future__ import annotations

from dataclasses import asdict, dataclass, replace

import numpy as np
import pandas as pd

from math6186.compartment_model import simulate
from math6186.config import DemandParameters, ModelParameters, NewsvendorCosts
from math6186.demand import expected_demand, generate_scenarios
from math6186.newsvendor import evaluate_daily_policy, optimal_capacity


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    group: str
    alpha: float = 1.0
    cv: float = 0.15
    underage: float = 5.0
    overage: float = 1.0
    p_worried: float = 0.5
    initial_infected: float = 0.01
    initial_worried: float = 0.01


def build_experiment_grid() -> pd.DataFrame:
    configs: list[ExperimentConfig] = []
    configs.extend(
        ExperimentConfig(f"behaviour_alpha_{alpha:g}", "behaviour", alpha=alpha)
        for alpha in (0.5, 1.0, 2.0)
    )
    configs.extend(
        ExperimentConfig(
            f"uncertainty_alpha_{alpha:g}_cv_{cv:.2f}",
            "uncertainty",
            alpha=alpha,
            cv=cv,
        )
        for alpha in (0.5, 1.0, 2.0)
        for cv in (0.05, 0.15, 0.30)
    )
    configs.extend(
        ExperimentConfig(
            f"cost_cu_{underage:g}_co_1",
            "cost",
            underage=underage,
            overage=1.0,
        )
        for underage in (1.0, 5.0, 10.0)
    )
    configs.extend(
        ExperimentConfig(
            f"service_pw_{p_worried:.2f}",
            "service_seeking",
            p_worried=p_worried,
        )
        for p_worried in (0.25, 0.50, 0.75, 1.00)
    )
    initial_pairs = ((0.01, 0.001), (0.01, 0.01), (0.001, 0.01))
    configs.extend(
        ExperimentConfig(
            f"initial_ip_{infected:.3f}_iw_{worried:.3f}",
            "initial_condition",
            initial_infected=infected,
            initial_worried=worried,
        )
        for infected, worried in initial_pairs
    )
    return pd.DataFrame([asdict(config) for config in configs])


def _to_config(row: pd.Series) -> ExperimentConfig:
    return ExperimentConfig(**row.to_dict())


def run_experiment(
    config: ExperimentConfig,
    in_sample: int = 5_000,
    out_sample: int = 10_000,
    seed: int = 6_186,
) -> dict[str, pd.DataFrame]:
    initial_state = (
        1.0 - config.initial_infected - config.initial_worried,
        config.initial_infected,
        config.initial_worried,
        0.0,
    )
    model_params = ModelParameters(alpha=config.alpha, initial_state=initial_state)
    trajectory = simulate(model_params)
    in_params = DemandParameters(
        p_worried=config.p_worried,
        coefficient_of_variation=config.cv,
        scenarios=in_sample,
        seed=seed,
    )
    out_params = replace(in_params, scenarios=out_sample, seed=seed + 1)
    means = expected_demand(trajectory, in_params)
    in_demand = generate_scenarios(means, in_params)
    out_demand = generate_scenarios(means, out_params)
    costs = NewsvendorCosts(config.underage, config.overage)
    optimized_capacity = np.array(
        [optimal_capacity(row, costs) for row in in_demand],
        dtype=int,
    )
    mean_capacity = np.rint(means).astype(int).to_numpy()
    optimized = evaluate_daily_policy(out_demand, optimized_capacity, costs)
    mean_policy = evaluate_daily_policy(out_demand, mean_capacity, costs)
    daily = optimized.add_prefix("optimized_")
    daily = pd.concat(
        [
            trajectory[["day"]],
            means,
            pd.DataFrame(
                {
                    "demand_p05": np.quantile(out_demand, 0.05, axis=1),
                    "demand_p50": np.quantile(out_demand, 0.50, axis=1),
                    "demand_p95": np.quantile(out_demand, 0.95, axis=1),
                }
            ),
            daily,
            mean_policy.add_prefix("mean_policy_"),
        ],
        axis=1,
    )
    optimized_total = float(daily["optimized_expected_cost"].sum())
    mean_total = float(daily["mean_policy_expected_cost"].sum())
    reduction = 0.0 if mean_total == 0.0 else 100.0 * (mean_total - optimized_total) / mean_total
    summary = pd.DataFrame(
        [
            {
                "peak_infected": trajectory["I_P"].max(),
                "peak_infected_day": int(trajectory.loc[trajectory["I_P"].idxmax(), "day"]),
                "peak_worried": trajectory["I_W"].max(),
                "peak_worried_day": int(trajectory.loc[trajectory["I_W"].idxmax(), "day"]),
                "peak_pressure": trajectory["pressure"].max(),
                "peak_pressure_day": int(trajectory.loc[trajectory["pressure"].idxmax(), "day"]),
                "optimized_total_cost": optimized_total,
                "mean_policy_total_cost": mean_total,
                "relative_cost_reduction_pct": reduction,
            }
        ]
    )
    for table in (trajectory, daily, summary):
        table.insert(0, "scenario", config.name)
        table.insert(1, "group", config.group)
    parameters = pd.DataFrame([{**asdict(config), "seed": seed, "in_sample": in_sample, "out_sample": out_sample}])
    return {
        "trajectories": trajectory,
        "daily_metrics": daily,
        "summary": summary,
        "parameters": parameters,
    }


def run_all_experiments(
    in_sample: int = 5_000,
    out_sample: int = 10_000,
    seed: int = 6_186,
) -> dict[str, pd.DataFrame]:
    collected: dict[str, list[pd.DataFrame]] = {
        "trajectories": [],
        "daily_metrics": [],
        "summary": [],
        "parameters": [],
    }
    for _, row in build_experiment_grid().iterrows():
        outputs = run_experiment(_to_config(row), in_sample, out_sample, seed)
        for key, table in outputs.items():
            collected[key].append(table)
    return {
        key: pd.concat(tables, ignore_index=True)
        for key, tables in collected.items()
    }
```

- [ ] **Step 4: Run experiment tests**

Run: `python -m pytest tests/test_experiments.py -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the experiment pipeline**

```powershell
git add src/math6186/experiments.py tests/test_experiments.py
git commit -m "feat: add reproducible experiment grid"
```

---

### Task 6: Publication-Ready Figures

**Files:**
- Create: `src/math6186/plots.py`
- Create: `tests/test_plots.py`

**Interfaces:**
- Consumes: the four tidy tables from `run_all_experiments`.
- Produces: `save_all_figures(outputs, output_dir) -> list[pathlib.Path]`.

- [ ] **Step 1: Write failing plotting test**

```python
# tests/test_plots.py
from pathlib import Path

from math6186.experiments import run_all_experiments
from math6186.plots import save_all_figures


def test_save_all_figures_creates_five_nonempty_pngs(tmp_path: Path):
    outputs = run_all_experiments(in_sample=100, out_sample=150)
    paths = save_all_figures(outputs, tmp_path)
    assert len(paths) == 5
    assert all(path.suffix == ".png" for path in paths)
    assert all(path.exists() and path.stat().st_size > 10_000 for path in paths)
```

- [ ] **Step 2: Run the plotting test to verify failure**

Run: `python -m pytest tests/test_plots.py -v`

Expected: collection fails because `math6186.plots` does not exist.

- [ ] **Step 3: Implement five focused figure builders**

```python
# src/math6186/plots.py
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BEHAVIOUR_SCENARIOS = [
    "behaviour_alpha_0.5",
    "behaviour_alpha_1",
    "behaviour_alpha_2",
]
BEHAVIOUR_LABELS = {
    "behaviour_alpha_0.5": "Cautious (alpha=0.5)",
    "behaviour_alpha_1": "Default (alpha=1)",
    "behaviour_alpha_2": "High-contact (alpha=2)",
}


def _finish(fig: plt.Figure, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def save_all_figures(
    outputs: dict[str, pd.DataFrame],
    output_dir: str | Path,
) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    trajectories = outputs["trajectories"]
    daily = outputs["daily_metrics"]
    summary = outputs["summary"]
    selected_trajectories = trajectories[
        trajectories["scenario"].isin(BEHAVIOUR_SCENARIOS)
    ]
    selected_daily = daily[daily["scenario"].isin(BEHAVIOUR_SCENARIOS)]

    fig1, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True, sharey=True)
    for axis, scenario in zip(axes, BEHAVIOUR_SCENARIOS, strict=True):
        frame = selected_trajectories[selected_trajectories["scenario"] == scenario]
        for column, label in (
            ("S", "Susceptible"),
            ("I_P", "Infected"),
            ("I_W", "Worried-well"),
            ("R_P", "Recovered"),
        ):
            axis.plot(frame["day"], frame[column], label=label)
        axis.set_title(BEHAVIOUR_LABELS[scenario])
        axis.set_xlabel("Day")
    axes[0].set_ylabel("Population fraction")
    axes[-1].legend(frameon=False)
    path1 = _finish(fig1, destination / "figure_1_compartments.png")

    fig2, axis2 = plt.subplots(figsize=(7, 4))
    for scenario in BEHAVIOUR_SCENARIOS:
        frame = selected_trajectories[selected_trajectories["scenario"] == scenario]
        axis2.plot(frame["day"], frame["risk_ratio"], label=BEHAVIOUR_LABELS[scenario])
    axis2.axhline(1.0, color="black", linestyle="--", linewidth=1)
    axis2.set(xlabel="Day", ylabel="Worried-well / infected ratio")
    axis2.legend(frameon=False)
    path2 = _finish(fig2, destination / "figure_2_risk_ratio.png")

    default_daily = selected_daily[selected_daily["scenario"] == "behaviour_alpha_1"]
    fig3, axis3 = plt.subplots(figsize=(7, 4))
    axis3.fill_between(
        default_daily["day"],
        default_daily["demand_p05"],
        default_daily["demand_p95"],
        alpha=0.25,
        label="5th-95th percentile",
    )
    axis3.plot(default_daily["day"], default_daily["mean_demand"], label="Deterministic demand")
    axis3.set(xlabel="Day", ylabel="Consultation demand")
    axis3.legend(frameon=False)
    path3 = _finish(fig3, destination / "figure_3_demand_uncertainty.png")

    fig4, axis4 = plt.subplots(figsize=(7, 4))
    for scenario in BEHAVIOUR_SCENARIOS:
        frame = selected_daily[selected_daily["scenario"] == scenario]
        axis4.plot(frame["day"], frame["optimized_capacity"], label=BEHAVIOUR_LABELS[scenario])
    axis4.set(xlabel="Day", ylabel="Optimal consultation capacity")
    axis4.legend(frameon=False)
    path4 = _finish(fig4, destination / "figure_4_optimal_capacity.png")

    sensitivity = summary[summary["group"].isin(["uncertainty", "cost"])].merge(
        outputs["parameters"][["name", "alpha", "cv", "underage"]],
        left_on="scenario",
        right_on="name",
        how="left",
    )
    fig5, axes5 = plt.subplots(1, 2, figsize=(10, 4))
    uncertainty = sensitivity[sensitivity["group"] == "uncertainty"]
    for alpha, frame in uncertainty.groupby("alpha"):
        ordered = frame.sort_values("cv")
        axes5[0].plot(
            ordered["cv"],
            ordered["optimized_total_cost"],
            marker="o",
            label=f"alpha={alpha:g}",
        )
    axes5[0].set(xlabel="Coefficient of variation", ylabel="Optimized total expected cost")
    axes5[0].legend(frameon=False)
    costs = sensitivity[sensitivity["group"] == "cost"].sort_values("underage")
    axes5[1].plot(costs["underage"], costs["relative_cost_reduction_pct"], marker="o")
    axes5[1].set(xlabel="Underage cost", ylabel="Cost reduction vs mean policy (%)")
    path5 = _finish(fig5, destination / "figure_5_sensitivity.png")

    return [path1, path2, path3, path4, path5]
```

- [ ] **Step 4: Run the plotting test**

Run: `python -m pytest tests/test_plots.py -v`

Expected: all tests pass and Matplotlib produces no interactive window.

- [ ] **Step 5: Commit the plotting layer**

```powershell
git add src/math6186/plots.py tests/test_plots.py
git commit -m "feat: add publication-ready analysis figures"
```

---

### Task 7: One-Command Reproduction and Generated Evidence

**Files:**
- Create: `scripts/run_analysis.py`
- Create: `tests/test_run_analysis.py`
- Create: `README.md`
- Generate: `outputs/data/trajectories.csv`
- Generate: `outputs/data/daily_metrics.csv`
- Generate: `outputs/data/summary.csv`
- Generate: `outputs/data/parameters.csv`
- Generate: `outputs/figures/figure_1_compartments.png`
- Generate: `outputs/figures/figure_2_risk_ratio.png`
- Generate: `outputs/figures/figure_3_demand_uncertainty.png`
- Generate: `outputs/figures/figure_4_optimal_capacity.png`
- Generate: `outputs/figures/figure_5_sensitivity.png`

**Interfaces:**
- Consumes: `run_all_experiments` and `save_all_figures`.
- Produces: `main(output_root, in_sample, out_sample, seed) -> dict[str, pathlib.Path]` and a CLI callable with `python scripts/run_analysis.py`.

- [ ] **Step 1: Write the failing end-to-end test**

```python
# tests/test_run_analysis.py
from pathlib import Path

import pandas as pd

from scripts.run_analysis import main


def test_main_writes_reproducible_tables_and_figures(tmp_path: Path):
    first = main(tmp_path / "first", in_sample=100, out_sample=150, seed=6186)
    second = main(tmp_path / "second", in_sample=100, out_sample=150, seed=6186)
    assert set(first) == {"data_dir", "figure_dir"}
    first_summary = pd.read_csv(first["data_dir"] / "summary.csv")
    second_summary = pd.read_csv(second["data_dir"] / "summary.csv")
    pd.testing.assert_frame_equal(first_summary, second_summary)
    assert len(list(first["figure_dir"].glob("*.png"))) == 5
```

- [ ] **Step 2: Run the test to verify failure**

Run: `python -m pytest tests/test_run_analysis.py -v`

Expected: collection fails because `scripts.run_analysis` does not exist.

- [ ] **Step 3: Implement the analysis command**

```python
# scripts/run_analysis.py
from __future__ import annotations

import argparse
from pathlib import Path

from math6186.experiments import run_all_experiments
from math6186.plots import save_all_figures


def main(
    output_root: str | Path = "outputs",
    in_sample: int = 5_000,
    out_sample: int = 10_000,
    seed: int = 6_186,
) -> dict[str, Path]:
    root = Path(output_root)
    data_dir = root / "data"
    figure_dir = root / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    outputs = run_all_experiments(in_sample, out_sample, seed)
    for name, table in outputs.items():
        table.to_csv(data_dir / f"{name}.csv", index=False)
    save_all_figures(outputs, figure_dir)
    return {"data_dir": data_dir, "figure_dir": figure_dir}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the complete MATH6186 analysis.")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--in-sample", type=int, default=5_000)
    parser.add_argument("--out-sample", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=6_186)
    arguments = parser.parse_args()
    main(
        output_root=arguments.output_root,
        in_sample=arguments.in_sample,
        out_sample=arguments.out_sample,
        seed=arguments.seed,
    )
```

- [ ] **Step 4: Write exact reproduction instructions**

````markdown
# MATH6186 Worried-Well Capacity Project

This project reproduces the Singh-Gromov worried-well compartment model,
converts the trajectories into synthetic daily consultation demand, and solves
a repeated single-period newsvendor capacity problem.

## Setup

```powershell
python -m venv .venv
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
````

- [ ] **Step 5: Run the end-to-end test and full suite**

Run:

```powershell
python -m pytest tests/test_run_analysis.py -v
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Generate the full evidence set**

Run: `python scripts/run_analysis.py`

Expected: four non-empty CSV files in `outputs/data`, five non-empty PNG files in `outputs/figures`, and no warnings or tracebacks.

- [ ] **Step 7: Inspect numerical output**

Run:

```powershell
python -c "import numpy as np, pandas as pd; s=pd.read_csv('outputs/data/summary.csv'); columns=['optimized_total_cost','mean_policy_total_cost','relative_cost_reduction_pct']; print(s.groupby('group')[columns].describe()); assert np.isfinite(s[columns].to_numpy()).all()"
```

Expected: grouped descriptive statistics print successfully, all policy-comparison metrics are finite, and the assertion exits with code 0. The sign of the relative cost difference is a result to interpret, not a pre-imposed test condition.

- [ ] **Step 8: Commit the reproducible analysis and outputs**

```powershell
git add scripts/run_analysis.py tests/test_run_analysis.py README.md outputs/data outputs/figures
git commit -m "feat: generate reproducible MATH6186 evidence"
```

---

### Task 8: Report Outline and Evidence Traceability

**Files:**
- Create: `report/outline.md`
- Create: `report/literature-matrix.csv`
- Create: `report/evidence-map.csv`
- Modify: `README.md`

**Interfaces:**
- Consumes: generated CSV and PNG evidence from Task 7.
- Produces: a report skeleton, a structured literature matrix, and an explicit mapping from each planned quantitative claim to its source artifact.

- [ ] **Step 1: Create the report outline with section purposes**

```markdown
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
```

- [ ] **Step 2: Create the literature matrix**

```csv
theme,source,year,doi_or_url,role_in_review,critical_note
worried_well,"Singh, B. and Gromov, D. Mathematically modeling worried-well behavior during infectious disease outbreaks",2025,https://doi.org/10.1371/journal.pone.0319550,"Defines the four-compartment baseline and behavioural regimes","Provides synthetic early-outbreak dynamics but does not estimate consultation capacity"
worried_well,"Chatterjee, S.S. et al. Worried well and COVID-19: re-emergence of an old quandary",2020,https://doi.org/10.1016/j.ajp.2020.102247,"Explains clinical and healthcare-system relevance of worried-well demand","Conceptual clinical discussion rather than an optimization study"
behaviour_and_risk,"Asmundson, G.J.G. and Taylor, S. Coronaphobia: fear and the 2019-nCoV outbreak",2020,https://doi.org/10.1016/j.janxdis.2020.102196,"Supports the role of anxiety and perceived risk during an emerging outbreak","Does not provide a compartmental resource-planning model"
compartmental_models,"Blyuss, K.B. and Kyrychko, Y.N. On a basic model of a two-disease epidemic",2005,https://doi.org/10.1016/j.amc.2003.10.033,"Provides the two-process modelling foundation cited by Singh and Gromov","Models interacting transmission processes but not worried-well capacity demand"
resource_allocation,"Singh, B. and Rebennack, S. Release immediately or sequentially? Strategies for allocating scarce therapeutic resources during disease outbreaks",2025,https://doi.org/10.1080/24725854.2025.2525918,"Connects outbreak timing to scarce healthcare resource decisions","Addresses release policies rather than a classical newsvendor capacity decision"
newsvendor,"Qin, Y. et al. The newsvendor problem: Review and directions for future research",2011,https://doi.org/10.1016/j.ejor.2010.11.024,"Provides the critical-fractile foundation and major newsvendor extensions","The present project deliberately uses only the classical single-resource form"
```

- [ ] **Step 3: Verify the literature matrix is complete and uniquely keyed**

Run:

```powershell
python -c "import pandas as pd; m=pd.read_csv('report/literature-matrix.csv'); required={'theme','source','year','doi_or_url','role_in_review','critical_note'}; assert required <= set(m.columns); assert len(m)==6; assert m.doi_or_url.is_unique; assert not m.isna().any().any(); print(m.groupby('theme').size())"
```

Expected: six complete and DOI-unique sources print across the worried-well, behavioural, compartmental, resource-allocation, and newsvendor themes.

- [ ] **Step 4: Create the evidence map**

```csv
report_section,planned_claim,evidence_file,required_columns
3,The ODE preserves total population,outputs/data/trajectories.csv,S;I_P;I_W;R_P;total
7.1,Behaviour changes infected and worried-well peaks,outputs/data/summary.csv,peak_infected;peak_infected_day;peak_worried;peak_worried_day
7.1,Worried-well pressure can exceed infection pressure early,outputs/figures/figure_2_risk_ratio.png,
7.2,Demand uncertainty changes safety capacity,outputs/data/daily_metrics.csv,scenario;mean_demand;optimized_capacity;demand_p05;demand_p95
7.3,Shortage cost changes optimized capacity and expected cost,outputs/data/daily_metrics.csv,scenario;optimized_capacity;optimized_expected_cost
7.4,Worried-well service seeking changes consultation demand,outputs/data/daily_metrics.csv,scenario;mean_demand
7.5,Policy comparison quantifies the cost difference from mean planning,outputs/data/summary.csv,optimized_total_cost;mean_policy_total_cost;relative_cost_reduction_pct
8,Results are synthetic scenario analysis,outputs/data/parameters.csv,seed;in_sample;out_sample
```

- [ ] **Step 5: Add the report links to the README**

Append:

```markdown
## Report evidence

- The planned report structure is in `report/outline.md`.
- `report/literature-matrix.csv` records the role and limitation of each starting source.
- `report/evidence-map.csv` links each planned quantitative claim to a generated
  table or figure.
- Re-run the analysis before drafting results so every number is current.
```

- [ ] **Step 6: Verify every mapped evidence file and column**

Run:

```powershell
python -c "from pathlib import Path; import pandas as pd; m=pd.read_csv('report/evidence-map.csv').fillna(''); missing=[p for p in m.evidence_file.unique() if not Path(p).exists()]; assert not missing, missing; failures=[]; [(failures.append((r.evidence_file, sorted(set(r.required_columns.split(';'))-set(pd.read_csv(r.evidence_file,nrows=1).columns)))) if Path(r.evidence_file).suffix=='.csv' and set(r.required_columns.split(';'))-set(pd.read_csv(r.evidence_file,nrows=1).columns) else None) for r in m.itertuples()]; assert not failures, failures; print(m.to_string(index=False))"
```

Expected: the complete evidence map prints and the command exits with code 0.

- [ ] **Step 7: Run final quality gates**

Run:

```powershell
python -m pytest -v
python scripts/run_analysis.py
git diff --check
git status --short
```

Expected: all tests pass, analysis regeneration succeeds, `git diff --check` reports no errors, and status lists only the literature matrix, evidence map, report outline, and README modification intended for this task.

- [ ] **Step 8: Commit the report evidence framework**

```powershell
git add report/outline.md report/literature-matrix.csv report/evidence-map.csv README.md
git commit -m "docs: map report claims to generated evidence"
```

## Final Acceptance Checklist

- [ ] `python -m pytest -v` passes without skipped or xfailed tests.
- [ ] `python scripts/run_analysis.py` regenerates all four CSV files and five PNG files.
- [ ] Re-running with seed `6186` produces identical CSV outputs.
- [ ] Every trajectory passes population conservation and state-bound checks.
- [ ] Every demand sample is finite, non-negative, integer-valued, and reproducible.
- [ ] Empirical-quantile newsvendor costs match direct enumeration on test samples.
- [ ] Optimized and mean-policy out-of-sample costs are finite and their signed differences are reported without assuming the optimized policy must win in every finite sample.
- [ ] Figures use day units, readable legends, descriptive axes, and no interactive backend.
- [ ] `report/literature-matrix.csv` contains six complete, DOI-unique starting sources spanning every literature-review theme.
- [ ] `report/evidence-map.csv` points only to existing files and valid result columns.
- [ ] The report outline labels all data and outputs as synthetic scenario analysis.
