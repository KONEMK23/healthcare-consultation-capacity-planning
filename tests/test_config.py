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
