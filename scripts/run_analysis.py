from __future__ import annotations

import argparse
from pathlib import Path

from math6186.experiments import run_all_experiments
from math6186.plots import save_all_figures


def main(
    output_root: str | Path = "outputs",
    in_sample: int = 5_000,
    out_sample: int = 10_000,
    seed: int = 6_186,
) -> dict[str, Path]:
    root = Path(output_root)
    data_dir = root / "data"
    figure_dir = root / "figures"
    outputs = run_all_experiments(in_sample, out_sample, seed)
    data_dir.mkdir(parents=True, exist_ok=True)
    for stale_table in data_dir.glob("*.csv"):
        stale_table.unlink()
    for name, table in outputs.items():
        table.to_csv(data_dir / f"{name}.csv", index=False)
    save_all_figures(outputs, figure_dir)
    return {"data_dir": data_dir, "figure_dir": figure_dir}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the complete MATH6186 analysis.")
    parser.add_argument("--output-root", default="outputs")
    parser.add_argument("--in-sample", type=int, default=5_000)
    parser.add_argument("--out-sample", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=6_186)
    arguments = parser.parse_args()
    main(
        output_root=arguments.output_root,
        in_sample=arguments.in_sample,
        out_sample=arguments.out_sample,
        seed=arguments.seed,
    )
