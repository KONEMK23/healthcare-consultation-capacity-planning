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
