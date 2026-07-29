import pandas as pd

from math6186.experiments import build_experiment_grid, run_all_experiments


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
