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


@pytest.mark.parametrize(
    ("demand", "costs", "expected"),
    [
        (np.array([31, 7]), NewsvendorCosts(1.0, 5.0), 7),
        (np.array([3, 8, 20, 21, 40]), NewsvendorCosts(2.0, 5.0), 8),
    ],
)
def test_capacity_uses_empirical_inverse_cdf_order_statistic(
    demand,
    costs,
    expected,
):
    assert optimal_capacity(demand, costs) == expected
    assert enumerated_optimum(demand, costs) == expected


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


@pytest.mark.parametrize(
    ("optimizer", "demand"),
    [
        (sample_cost, np.array([1.5])),
        (optimal_capacity, np.array([1.5])),
        (enumerated_optimum, np.array([1.5])),
    ],
)
def test_sample_functions_reject_fractional_demand(optimizer, demand):
    costs = NewsvendorCosts()
    if optimizer is sample_cost:
        with pytest.raises(ValueError, match="integers"):
            optimizer(demand, 1, costs)
    else:
        with pytest.raises(ValueError, match="integers"):
            optimizer(demand, costs)


def test_daily_policy_rejects_fractional_demand():
    with pytest.raises(ValueError, match="integers"):
        evaluate_daily_policy(np.array([[1.5]]), np.array([1]), NewsvendorCosts())


def test_sample_cost_rejects_fractional_capacity():
    with pytest.raises(ValueError, match="integer"):
        sample_cost(np.array([1]), 1.5, NewsvendorCosts())


def test_daily_policy_rejects_fractional_capacity():
    with pytest.raises(ValueError, match="integers"):
        evaluate_daily_policy(np.array([[1]]), np.array([1.5]), NewsvendorCosts())


def test_sample_cost_normalizes_unsigned_demand_before_subtraction():
    demand = np.array([1], dtype=np.uint8)

    assert sample_cost(demand, 2, NewsvendorCosts(5.0, 1.0)) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "demand",
    [
        np.array(["1"]),
        np.array([True]),
        np.array([np.iinfo(np.int64).max], dtype=np.uint64)
        + np.array([1], dtype=np.uint64),
        np.array([float(2**63)]),
    ],
)
def test_demand_rejects_unsupported_or_overflowing_representations(demand):
    with pytest.raises(ValueError, match="Demand"):
        sample_cost(demand, 1, NewsvendorCosts())


def test_enumerated_optimum_matches_independent_brute_force_on_random_samples():
    rng = np.random.default_rng(20260729)
    for _ in range(30):
        demand = rng.integers(0, 25, size=20)
        costs = NewsvendorCosts(
            underage=float(rng.integers(1, 11)),
            overage=float(rng.integers(1, 11)),
        )
        brute_costs = [
            sum(
                costs.underage * max(int(value) - capacity, 0)
                + costs.overage * max(capacity - int(value), 0)
                for value in demand
            )
            / len(demand)
            for capacity in range(int(demand.max()) + 1)
        ]
        expected = int(np.argmin(brute_costs))

        assert enumerated_optimum(demand, costs) == expected


def test_enumeration_handles_sparse_demand_with_huge_breakpoint():
    demand = np.array([0, np.iinfo(np.int64).max], dtype=np.int64)

    assert enumerated_optimum(demand, NewsvendorCosts(1.0, 5.0)) == 0


def test_sample_cost_rejects_capacity_above_signed_arithmetic_range():
    with pytest.raises(ValueError, match="capacity"):
        sample_cost(np.array([1]), float(2**63), NewsvendorCosts())
