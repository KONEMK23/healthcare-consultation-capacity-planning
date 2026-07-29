from pathlib import Path

from math6186.experiments import run_all_experiments
from math6186.plots import save_all_figures


def test_save_all_figures_creates_five_nonempty_pngs(tmp_path: Path):
    (tmp_path / "unexpected.png").write_bytes(b"stale")
    outputs = run_all_experiments(in_sample=100, out_sample=150)
    paths = save_all_figures(outputs, tmp_path)

    expected_names = [
        "figure_1_compartments.png",
        "figure_2_risk_ratio.png",
        "figure_3_demand_uncertainty.png",
        "figure_4_optimal_capacity.png",
        "figure_5_sensitivity.png",
    ]
    assert [path.name for path in paths] == expected_names
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(expected_names)
    assert all(path.exists() and path.stat().st_size > 10_000 for path in paths)
