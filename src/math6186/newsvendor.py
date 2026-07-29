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
