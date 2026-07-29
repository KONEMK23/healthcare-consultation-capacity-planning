from __future__ import annotations

from dataclasses import asdict, dataclass, replace

import numpy as np
import pandas as pd

from math6186.compartment_model import simulate
from math6186.config import DemandParameters, ModelParameters, NewsvendorCosts
from math6186.demand import expected_demand, generate_scenarios
from math6186.newsvendor import evaluate_daily_policy, optimal_capacity


MODEL_STRUCTURE_PROVENANCE = (
    "Singh and Gromov (2025), doi:10.1371/journal.pone.0319550 "
    "(four-compartment model structure)"
)
BEHAVIOUR_PROVENANCE = "Singh and Gromov (2025) behavioural alpha scenarios"
RATE_PARAMETER_PROVENANCE = (
    "Singh and Gromov (2025) baseline model values adopted for this coursework"
)
SERVICE_DEMAND_PROVENANCE = (
    "Coursework modelling assumption (synthetic population and service-seeking rates)"
)
UNCERTAINTY_PROVENANCE = (
    "Coursework modelling assumption (coefficient-of-variation sensitivity)"
)
COST_PROVENANCE = "Coursework modelling assumption (newsvendor cost sensitivity)"


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    group: str
    alpha: float = 1.0
    cv: float = 0.15
    underage: float = 5.0
    overage: float = 1.0
    p_worried: float = 0.5
    initial_infected: float = 0.01
    initial_worried: float = 0.01


def build_experiment_grid() -> pd.DataFrame:
    """Return the named, reproducible sensitivity-analysis configurations."""
    configs: list[ExperimentConfig] = []
    configs.extend(
        ExperimentConfig(f"behaviour_alpha_{alpha:g}", "behaviour", alpha=alpha)
        for alpha in (0.5, 1.0, 2.0)
    )
    configs.extend(
        ExperimentConfig(
            f"uncertainty_alpha_{alpha:g}_cv_{cv:.2f}",
            "uncertainty",
            alpha=alpha,
            cv=cv,
        )
        for alpha in (0.5, 1.0, 2.0)
        for cv in (0.05, 0.15, 0.30)
    )
    configs.extend(
        ExperimentConfig(
            f"cost_cu_{underage:g}_co_1",
            "cost",
            underage=underage,
            overage=1.0,
        )
        for underage in (1.0, 5.0, 10.0)
    )
    configs.extend(
        ExperimentConfig(
            f"service_pw_{p_worried:.2f}",
            "service_seeking",
            p_worried=p_worried,
        )
        for p_worried in (0.25, 0.50, 0.75, 1.00)
    )
    configs.extend(
        ExperimentConfig(
            f"initial_ip_{infected:.3f}_iw_{worried:.3f}",
            "initial_condition",
            initial_infected=infected,
            initial_worried=worried,
        )
        for infected, worried in ((0.01, 0.001), (0.01, 0.01), (0.001, 0.01))
    )
    return pd.DataFrame([asdict(config) for config in configs])


def _to_config(row: pd.Series) -> ExperimentConfig:
    return ExperimentConfig(**row.to_dict())


def run_experiment(
    config: ExperimentConfig,
    in_sample: int = 5_000,
    out_sample: int = 10_000,
    seed: int = 6_186,
) -> dict[str, pd.DataFrame]:
    """Optimize from an in-sample draw and evaluate both policies out of sample."""
    initial_state = (
        1.0 - config.initial_infected - config.initial_worried,
        config.initial_infected,
        config.initial_worried,
        0.0,
    )
    model_params = ModelParameters(alpha=config.alpha, initial_state=initial_state)
    trajectory = simulate(model_params)
    in_params = DemandParameters(
        p_worried=config.p_worried,
        coefficient_of_variation=config.cv,
        scenarios=in_sample,
        seed=seed,
    )
    out_params = replace(in_params, scenarios=out_sample, seed=seed + 1)
    means = expected_demand(trajectory, in_params)
    in_demand = generate_scenarios(means, in_params)
    out_demand = generate_scenarios(means, out_params)
    costs = NewsvendorCosts(config.underage, config.overage)
    optimized_capacity = np.array(
        [optimal_capacity(row, costs) for row in in_demand], dtype=int
    )
    mean_capacity = np.rint(means).astype(int).to_numpy()
    optimized = evaluate_daily_policy(out_demand, optimized_capacity, costs)
    mean_policy = evaluate_daily_policy(out_demand, mean_capacity, costs)
    daily = pd.concat(
        [
            trajectory[["day"]],
            means,
            pd.DataFrame(
                {
                    "demand_p05": np.quantile(out_demand, 0.05, axis=1),
                    "demand_p50": np.quantile(out_demand, 0.50, axis=1),
                    "demand_p95": np.quantile(out_demand, 0.95, axis=1),
                }
            ),
            optimized.add_prefix("optimized_"),
            mean_policy.add_prefix("mean_policy_"),
        ],
        axis=1,
    )
    optimized_total = float(daily["optimized_expected_cost"].sum())
    mean_total = float(daily["mean_policy_expected_cost"].sum())
    reduction = (
        0.0
        if mean_total == 0.0
        else 100.0 * (mean_total - optimized_total) / mean_total
    )
    summary = pd.DataFrame(
        [
            {
                "peak_infected": trajectory["I_P"].max(),
                "peak_infected_day": int(
                    trajectory.loc[trajectory["I_P"].idxmax(), "day"]
                ),
                "peak_worried": trajectory["I_W"].max(),
                "peak_worried_day": int(
                    trajectory.loc[trajectory["I_W"].idxmax(), "day"]
                ),
                "peak_pressure": trajectory["pressure"].max(),
                "peak_pressure_day": int(
                    trajectory.loc[trajectory["pressure"].idxmax(), "day"]
                ),
                "optimized_total_cost": optimized_total,
                "mean_policy_total_cost": mean_total,
                "relative_cost_reduction_pct": reduction,
            }
        ]
    )
    for table in (trajectory, daily, summary):
        table.insert(0, "scenario", config.name)
        table.insert(1, "group", config.group)
    baseline_initial_state = (
        config.initial_infected == 0.01 and config.initial_worried == 0.01
    )
    initial_condition_provenance = (
        "Singh and Gromov (2025) baseline initial condition"
        if baseline_initial_state
        else "Coursework modelling assumption (initial-condition sensitivity)"
    )
    parameters = pd.DataFrame(
        [
            {
                "scenario": config.name,
                "group": config.group,
                "alpha": model_params.alpha,
                "beta_p": model_params.beta_p,
                "beta_w": model_params.beta_w,
                "beta_wp": model_params.beta_wp,
                "gamma_p": model_params.gamma_p,
                "gamma_w": model_params.gamma_w,
                "delta_p": model_params.delta_p,
                "initial_susceptible": model_params.initial_state[0],
                "initial_infected": model_params.initial_state[1],
                "initial_worried": model_params.initial_state[2],
                "initial_recovered": model_params.initial_state[3],
                "population": in_params.population,
                "p_infected": in_params.p_infected,
                "p_worried": in_params.p_worried,
                "cv": in_params.coefficient_of_variation,
                "underage": costs.underage,
                "overage": costs.overage,
                "in_sample_seed": in_params.seed,
                "out_sample_seed": out_params.seed,
                "in_sample": in_sample,
                "out_sample": out_sample,
                "model_structure_provenance": MODEL_STRUCTURE_PROVENANCE,
                "behaviour_provenance": BEHAVIOUR_PROVENANCE,
                "rate_parameter_provenance": RATE_PARAMETER_PROVENANCE,
                "initial_condition_provenance": initial_condition_provenance,
                "service_demand_provenance": SERVICE_DEMAND_PROVENANCE,
                "uncertainty_provenance": UNCERTAINTY_PROVENANCE,
                "cost_provenance": COST_PROVENANCE,
            }
        ]
    )
    return {
        "trajectories": trajectory,
        "daily_metrics": daily,
        "summary": summary,
        "parameters": parameters,
    }


def run_all_experiments(
    in_sample: int = 5_000,
    out_sample: int = 10_000,
    seed: int = 6_186,
) -> dict[str, pd.DataFrame]:
    """Run every sensitivity configuration and concatenate the four tidy outputs."""
    collected: dict[str, list[pd.DataFrame]] = {
        "trajectories": [],
        "daily_metrics": [],
        "summary": [],
        "parameters": [],
    }
    for _, row in build_experiment_grid().iterrows():
        outputs = run_experiment(_to_config(row), in_sample, out_sample, seed)
        for key, table in outputs.items():
            collected[key].append(table)
    return {
        key: pd.concat(tables, ignore_index=True) for key, tables in collected.items()
    }
