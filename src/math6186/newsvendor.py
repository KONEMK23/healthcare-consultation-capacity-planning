from __future__ import annotations

import numpy as np
import pandas as pd

from math6186.config import NewsvendorCosts


def _validated_demand(demand: np.ndarray) -> np.ndarray:
    values = np.asarray(demand)
    if values.size == 0 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Demand must be non-empty, finite, and non-negative.")
    if not np.equal(values, np.floor(values)).all():
        raise ValueError("Demand values must be integers.")
    return values


def _validated_capacity(capacity: int) -> int:
    value = np.asarray(capacity)
    if value.ndim != 0 or not np.isfinite(value) or value < 0:
        raise ValueError("capacity must be a non-negative integer.")
    if value != np.floor(value):
        raise ValueError("capacity must be an integer.")
    return int(value)


def _validated_capacities(capacities: np.ndarray) -> np.ndarray:
    values = np.asarray(capacities)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("capacities must be non-negative integers.")
    if not np.equal(values, np.floor(values)).all():
        raise ValueError("capacities must be integers.")
    return values.astype(int)


def sample_cost(
    demand: np.ndarray,
    capacity: int,
    costs: NewsvendorCosts,
) -> float:
    values = _validated_demand(demand)
    selected = _validated_capacity(capacity)
    shortage = np.maximum(values - selected, 0)
    unused = np.maximum(selected - values, 0)
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
    selected = _validated_capacities(capacities)
    if values.ndim != 2 or selected.shape != (values.shape[0],):
        raise ValueError("capacities must contain one value per demand row.")
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
