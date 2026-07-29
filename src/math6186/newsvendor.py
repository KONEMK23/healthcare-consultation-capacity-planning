from __future__ import annotations

from math import ceil

import numpy as np
import pandas as pd

from math6186.config import NewsvendorCosts


def _exceeds_signed_integer_range(values: np.ndarray) -> bool:
    if values.dtype.kind == "f":
        return bool((values >= float(2**63)).any())
    return bool((values > np.iinfo(np.int64).max).any())


def _validated_demand(demand: np.ndarray) -> np.ndarray:
    values = np.asarray(demand)
    if values.size == 0:
        raise ValueError("Demand must be non-empty, finite, and non-negative.")
    if values.dtype.kind not in "iuf":
        raise ValueError("Demand must use a supported numeric representation.")
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Demand must be non-empty, finite, and non-negative.")
    if not np.equal(values, np.floor(values)).all():
        raise ValueError("Demand values must be integers.")
    if _exceeds_signed_integer_range(values):
        raise ValueError("Demand values exceed the supported integer range.")
    return values.astype(np.int64, copy=False)


def _validated_capacity(capacity: int) -> int:
    value = np.asarray(capacity)
    if (
        value.ndim != 0
        or value.dtype.kind not in "iuf"
        or not np.isfinite(value)
        or value < 0
        or _exceeds_signed_integer_range(value)
    ):
        raise ValueError("capacity must be a non-negative integer.")
    if value != np.floor(value):
        raise ValueError("capacity must be an integer.")
    return int(value)


def _validated_capacities(capacities: np.ndarray) -> np.ndarray:
    values = np.asarray(capacities)
    if values.dtype.kind not in "iuf":
        raise ValueError("capacities must be non-negative integers.")
    if (
        not np.isfinite(values).all()
        or (values < 0).any()
        or _exceeds_signed_integer_range(values)
    ):
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
    order_index = ceil(values.size * costs.critical_fractile) - 1
    return int(np.partition(values, order_index)[order_index])


def enumerated_optimum(demand: np.ndarray, costs: NewsvendorCosts) -> int:
    values = _validated_demand(np.asarray(demand).reshape(-1))
    unique_values, counts = np.unique(values, return_counts=True)
    candidates = (
        unique_values
        if unique_values[0] == 0
        else np.concatenate((np.array([0], dtype=np.int64), unique_values))
    )
    cumulative_counts = np.cumsum(counts, dtype=np.int64)
    cumulative_demand = np.cumsum(
        unique_values.astype(np.float64) * counts.astype(np.float64)
    )
    positions = np.searchsorted(unique_values, candidates, side="right") - 1
    counts_at_or_below = np.zeros(candidates.size, dtype=np.float64)
    demand_at_or_below = np.zeros(candidates.size, dtype=np.float64)
    present = positions >= 0
    counts_at_or_below[present] = cumulative_counts[positions[present]]
    demand_at_or_below[present] = cumulative_demand[positions[present]]
    candidate_values = candidates.astype(np.float64)
    unused = candidate_values * counts_at_or_below - demand_at_or_below
    shortage = (
        cumulative_demand[-1]
        - demand_at_or_below
        - candidate_values * (values.size - counts_at_or_below)
    )
    sample_costs = (
        costs.underage * shortage + costs.overage * unused
    ) / values.size
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
