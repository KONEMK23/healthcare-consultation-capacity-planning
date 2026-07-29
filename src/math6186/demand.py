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

    coefficient_of_variation = params.coefficient_of_variation
    location_in_sd = _standardized_location(coefficient_of_variation)
    draw_rng = np.random.default_rng(params.seed)
    integerization_rng = np.random.default_rng(
        np.random.SeedSequence([params.seed, 0x4D415448])
    )
    for row_index in np.flatnonzero(positive):
        requested_mean = requested_means[row_index]
        scale = coefficient_of_variation * requested_mean
        location = location_in_sd * scale
        draws = truncnorm.rvs(
            -location_in_sd,
            np.inf,
            loc=location,
            scale=scale,
            size=params.scenarios,
            random_state=draw_rng,
        )
        if not np.isfinite(draws).all() or (draws >= float(2**63)).any():
            raise ValueError("Generated demand exceeds the supported integer range.")
        integer_parts = np.floor(draws).astype(np.int64)
        fractional_parts = draws - integer_parts
        round_up = integerization_rng.random(params.scenarios) < fractional_parts
        output[row_index] = integer_parts + round_up.astype(np.int64)
    return output
