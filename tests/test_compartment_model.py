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
