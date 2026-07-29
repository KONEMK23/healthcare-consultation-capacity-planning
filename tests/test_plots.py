from pathlib import Path

from math6186.experiments import run_all_experiments
from math6186.plots import save_all_figures


def test_save_all_figures_creates_five_nonempty_pngs(tmp_path: Path):
    outputs = run_all_experiments(in_sample=100, out_sample=150)
    paths = save_all_figures(outputs, tmp_path)

    assert len(paths) == 5
    assert all(path.suffix == ".png" for path in paths)
    assert all(path.exists() and path.stat().st_size > 10_000 for path in paths)
