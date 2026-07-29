from pathlib import Path

import pandas as pd

from scripts.run_analysis import main


def test_main_writes_reproducible_tables_and_figures(tmp_path: Path):
    first = main(tmp_path / "first", in_sample=100, out_sample=150, seed=6186)
    second = main(tmp_path / "second", in_sample=100, out_sample=150, seed=6186)

    assert set(first) == {"data_dir", "figure_dir"}
    first_summary = pd.read_csv(first["data_dir"] / "summary.csv")
    second_summary = pd.read_csv(second["data_dir"] / "summary.csv")
    pd.testing.assert_frame_equal(first_summary, second_summary)
    assert len(list(first["figure_dir"].glob("*.png"))) == 5
