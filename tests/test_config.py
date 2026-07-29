import numpy as np
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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("beta_p", np.inf),
        ("beta_w", np.nan),
        ("gamma_p", "0.1"),
        ("delta_p", 1.0 + 0.0j),
        ("alpha", True),
    ],
)
def test_model_rejects_non_finite_or_non_real_parameters(field, value):
    with pytest.raises(ValueError, match=field):
        ModelParameters(**{field: value})


@pytest.mark.parametrize(
    "initial_state",
    [
        (np.nan, 0.0, 0.0, 1.0),
        (np.inf, 0.0, 0.0, 0.0),
        ("0.98", 0.01, 0.01, 0.0),
        (True, 0.0, 0.0, 0.0),
    ],
)
def test_model_rejects_invalid_initial_state_numeric_types(initial_state):
    with pytest.raises(ValueError, match="initial_state"):
        ModelParameters(initial_state=initial_state)


@pytest.mark.parametrize("field", ["population", "scenarios"])
@pytest.mark.parametrize("value", [0, -1, 1.5, np.nan, np.inf, "10", True])
def test_demand_requires_positive_integer_counts(field, value):
    with pytest.raises(ValueError, match=field):
        DemandParameters(**{field: value})


@pytest.mark.parametrize("value", [-1, 1.5, np.nan, np.inf, "6186", True])
def test_demand_requires_non_negative_integer_seed(value):
    with pytest.raises(ValueError, match="seed"):
        DemandParameters(seed=value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("p_infected", np.nan),
        ("p_worried", np.inf),
        ("coefficient_of_variation", "0.15"),
        ("coefficient_of_variation", True),
    ],
)
def test_demand_rejects_non_finite_or_non_real_rates(field, value):
    with pytest.raises(ValueError, match=field):
        DemandParameters(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("underage", np.nan),
        ("overage", np.inf),
        ("underage", "5"),
        ("overage", True),
    ],
)
def test_costs_require_finite_real_values(field, value):
    with pytest.raises(ValueError, match=field):
        NewsvendorCosts(**{field: value})


def test_configuration_accepts_legitimate_numpy_scalars():
    model = ModelParameters(beta_p=np.float64(0.74), alpha=np.float64(1.0))
    demand = DemandParameters(
        population=np.int64(100_000),
        p_infected=np.float64(1.0),
        p_worried=np.float64(0.5),
        coefficient_of_variation=np.float64(0.15),
        scenarios=np.int64(100),
        seed=np.int64(123),
    )
    costs = NewsvendorCosts(np.float64(5.0), np.float64(1.0))

    assert model.beta_p == pytest.approx(0.74)
    assert demand.scenarios == 100
    assert demand.seed == 123
    assert costs.critical_fractile == pytest.approx(5.0 / 6.0)


def test_costs_expose_critical_fractile():
    costs = NewsvendorCosts(underage=5.0, overage=1.0)
    assert costs.critical_fractile == pytest.approx(5.0 / 6.0)


def test_critical_fractile_remains_valid_for_large_finite_costs():
    costs = NewsvendorCosts(underage=1e308, overage=1e308)

    assert costs.critical_fractile == pytest.approx(0.5)
