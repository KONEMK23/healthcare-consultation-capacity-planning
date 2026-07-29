import pandas as pd

import math6186.experiments as experiments
from math6186.experiments import (
    ExperimentConfig,
    build_experiment_grid,
    run_all_experiments,
    run_experiment,
)


def test_grid_contains_all_required_experiment_groups():
    """Removing a required scenario variation must fail this coverage check."""
    grid = build_experiment_grid()

    assert set(grid["group"]) == {
        "behaviour",
        "uncertainty",
        "cost",
        "service_seeking",
        "initial_condition",
    }
    assert set(grid.loc[grid["group"] == "behaviour", "alpha"]) == {0.5, 1.0, 2.0}
    assert set(grid.loc[grid["group"] == "uncertainty", "cv"]) == {0.05, 0.15, 0.30}
    assert set(grid.loc[grid["group"] == "service_seeking", "p_worried"]) == {
        0.25,
        0.50,
        0.75,
        1.00,
    }
    assert grid["group"].value_counts().to_dict() == {
        "uncertainty": 9,
        "service_seeking": 4,
        "behaviour": 3,
        "cost": 3,
        "initial_condition": 3,
    }
    assert set(
        map(
            tuple,
            grid.loc[grid["group"] == "uncertainty", ["alpha", "cv"]].to_numpy(),
        )
    ) == {
        (0.5, 0.05),
        (0.5, 0.15),
        (0.5, 0.30),
        (1.0, 0.05),
        (1.0, 0.15),
        (1.0, 0.30),
        (2.0, 0.05),
        (2.0, 0.15),
        (2.0, 0.30),
    }
    assert set(
        map(
            tuple,
            grid.loc[grid["group"] == "cost", ["underage", "overage"]].to_numpy(),
        )
    ) == {(1.0, 1.0), (5.0, 1.0), (10.0, 1.0)}
    assert set(
        map(
            tuple,
            grid.loc[
                grid["group"] == "initial_condition",
                ["initial_infected", "initial_worried"],
            ].to_numpy(),
        )
    ) == {(0.01, 0.001), (0.01, 0.01), (0.001, 0.01)}


def test_run_all_experiments_returns_traceable_tables():
    """Returning missing metrics or non-tabular output must fail this contract check."""
    outputs = run_all_experiments(in_sample=200, out_sample=300)

    assert set(outputs) == {"trajectories", "daily_metrics", "summary", "parameters"}
    assert all(isinstance(table, pd.DataFrame) for table in outputs.values())
    assert not outputs["summary"].empty
    assert {
        "optimized_total_cost",
        "mean_policy_total_cost",
        "relative_cost_reduction_pct",
    } <= set(outputs["summary"].columns)
    assert outputs["summary"][
        ["optimized_total_cost", "mean_policy_total_cost", "relative_cost_reduction_pct"]
    ].notna().all().all()
    for table_name in ("trajectories", "daily_metrics", "summary"):
        assert {"scenario", "group"} <= set(outputs[table_name].columns)
    assert {"name", "group", "in_sample_seed", "out_sample_seed"} <= set(
        outputs["parameters"].columns
    )
    assert set(outputs["parameters"]["in_sample_seed"]) == {6_186}
    assert set(outputs["parameters"]["out_sample_seed"]) == {6_187}


def test_run_experiment_uses_distinct_seeded_draws_and_common_out_sample(
    monkeypatch,
):
    """Reusing a draw or evaluating policies on different draws must fail."""
    demand_params = []
    generated_demand = []
    evaluated_demand = []
    real_generate = experiments.generate_scenarios
    real_evaluate = experiments.evaluate_daily_policy

    def generate_spy(means, params):
        demand = real_generate(means, params)
        demand_params.append(params)
        generated_demand.append(demand)
        return demand

    def evaluate_spy(demand, capacities, costs):
        evaluated_demand.append(demand)
        return real_evaluate(demand, capacities, costs)

    monkeypatch.setattr(experiments, "generate_scenarios", generate_spy)
    monkeypatch.setattr(experiments, "evaluate_daily_policy", evaluate_spy)

    outputs = run_experiment(
        ExperimentConfig(name="seed_check", group="test"),
        in_sample=20,
        out_sample=30,
        seed=123,
    )

    assert [params.seed for params in demand_params] == [123, 124]
    assert len(evaluated_demand) == 2
    assert evaluated_demand[0] is generated_demand[1]
    assert evaluated_demand[1] is generated_demand[1]
    assert (outputs["parameters"][["in_sample_seed", "out_sample_seed"]].iloc[0]).to_dict() == {
        "in_sample_seed": 123,
        "out_sample_seed": 124,
    }
