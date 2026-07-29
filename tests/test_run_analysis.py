from pathlib import Path

import pandas as pd

from scripts.run_analysis import main


def test_main_writes_reproducible_tables_and_figures(tmp_path: Path):
    csv_schemas = {
        "daily_metrics.csv": [
            "scenario",
            "group",
            "day",
            "mean_demand",
            "demand_p05",
            "demand_p50",
            "demand_p95",
            "optimized_capacity",
            "optimized_expected_cost",
            "optimized_shortage_probability",
            "optimized_expected_shortage",
            "optimized_expected_unused",
            "mean_policy_capacity",
            "mean_policy_expected_cost",
            "mean_policy_shortage_probability",
            "mean_policy_expected_shortage",
            "mean_policy_expected_unused",
        ],
        "parameters.csv": [
            "scenario",
            "group",
            "alpha",
            "beta_p",
            "beta_w",
            "beta_wp",
            "gamma_p",
            "gamma_w",
            "delta_p",
            "initial_susceptible",
            "initial_infected",
            "initial_worried",
            "initial_recovered",
            "population",
            "p_infected",
            "p_worried",
            "cv",
            "underage",
            "overage",
            "in_sample_seed",
            "out_sample_seed",
            "in_sample",
            "out_sample",
            "model_structure_provenance",
            "behaviour_provenance",
            "rate_parameter_provenance",
            "initial_condition_provenance",
            "service_demand_provenance",
            "uncertainty_provenance",
            "cost_provenance",
        ],
        "summary.csv": [
            "scenario",
            "group",
            "peak_infected",
            "peak_infected_day",
            "peak_worried",
            "peak_worried_day",
            "peak_pressure",
            "peak_pressure_day",
            "optimized_total_cost",
            "mean_policy_total_cost",
            "relative_cost_reduction_pct",
        ],
        "trajectories.csv": [
            "scenario",
            "group",
            "day",
            "S",
            "I_P",
            "I_W",
            "R_P",
            "total",
            "pressure",
            "risk_ratio",
        ],
    }
    figure_names = [
        "figure_1_compartments.png",
        "figure_2_risk_ratio.png",
        "figure_3_demand_uncertainty.png",
        "figure_4_optimal_capacity.png",
        "figure_5_sensitivity.png",
    ]
    stale_data = tmp_path / "first" / "data"
    stale_figures = tmp_path / "first" / "figures"
    stale_data.mkdir(parents=True)
    stale_figures.mkdir(parents=True)
    (stale_data / "unexpected.csv").write_text("stale\n", encoding="utf-8")
    (stale_figures / "unexpected.png").write_bytes(b"stale")

    first = main(tmp_path / "first", in_sample=100, out_sample=150, seed=6186)
    second = main(tmp_path / "second", in_sample=100, out_sample=150, seed=6186)

    assert set(first) == {"data_dir", "figure_dir"}
    assert sorted(path.name for path in first["data_dir"].iterdir()) == sorted(csv_schemas)
    assert sorted(path.name for path in first["figure_dir"].iterdir()) == figure_names
    for filename, expected_columns in csv_schemas.items():
        first_path = first["data_dir"] / filename
        second_path = second["data_dir"] / filename
        assert first_path.stat().st_size > 0
        assert second_path.stat().st_size > 0
        first_table = pd.read_csv(first_path)
        second_table = pd.read_csv(second_path)
        assert first_table.columns.tolist() == expected_columns
        assert not first_table.empty
        pd.testing.assert_frame_equal(first_table, second_table)
    for filename in figure_names:
        assert (first["figure_dir"] / filename).stat().st_size > 10_000
        assert (second["figure_dir"] / filename).stat().st_size > 10_000
