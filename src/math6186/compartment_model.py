from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from math6186.config import ModelParameters


STATE_COLUMNS = ["S", "I_P", "I_W", "R_P"]


def compartment_rhs(
    _time: float,
    state: np.ndarray,
    params: ModelParameters,
) -> np.ndarray:
    susceptible, infected, worried, recovered = state
    d_susceptible = (
        -(params.beta_p + params.beta_wp) * susceptible * infected
        - params.beta_w * susceptible * worried
        + params.delta_p * recovered
        + params.gamma_w * worried
    )
    d_infected = (
        params.beta_p * susceptible * infected
        + params.alpha * params.beta_p * infected * worried
        - params.gamma_p * infected
    )
    d_worried = (
        -params.alpha * params.beta_p * infected * worried
        + params.beta_w * susceptible * worried
        + params.beta_wp * susceptible * infected
        - params.gamma_w * worried
    )
    d_recovered = params.gamma_p * infected - params.delta_p * recovered
    return np.array([d_susceptible, d_infected, d_worried, d_recovered])


def simulate(
    params: ModelParameters,
    days: int = 50,
    step_days: int = 1,
) -> pd.DataFrame:
    if days <= 0 or step_days <= 0 or days % step_days != 0:
        raise ValueError("days must be positive and divisible by step_days.")
    evaluation_days = np.arange(0, days + step_days, step_days, dtype=float)
    solution = solve_ivp(
        compartment_rhs,
        (0.0, float(days)),
        params.initial_state,
        args=(params,),
        t_eval=evaluation_days,
        method="DOP853",
        rtol=1e-9,
        atol=1e-11,
    )
    if not solution.success:
        raise RuntimeError(f"ODE solver failed: {solution.message}")
    states = solution.y.T
    totals = states.sum(axis=1)
    if not np.allclose(totals, 1.0, atol=1e-7):
        raise RuntimeError("Population conservation check failed.")
    if states.min() < -1e-8 or states.max() > 1.0 + 1e-8:
        raise RuntimeError("Compartment state bounds check failed.")
    frame = pd.DataFrame(states, columns=STATE_COLUMNS)
    frame.insert(0, "day", evaluation_days.astype(int))
    frame["total"] = totals
    frame["pressure"] = frame["I_P"] + frame["I_W"]
    frame["risk_ratio"] = np.divide(
        frame["I_W"].to_numpy(),
        frame["I_P"].to_numpy(),
        out=np.full(len(frame), np.nan),
        where=frame["I_P"].to_numpy() > 1e-12,
    )
    return frame
