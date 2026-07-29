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
