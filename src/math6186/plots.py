from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BEHAVIOUR_SCENARIOS = [
    "behaviour_alpha_0.5",
    "behaviour_alpha_1",
    "behaviour_alpha_2",
]
BEHAVIOUR_LABELS = {
    "behaviour_alpha_0.5": "Cautious (alpha=0.5)",
    "behaviour_alpha_1": "Default (alpha=1)",
    "behaviour_alpha_2": "High-contact (alpha=2)",
}


def _finish(fig: plt.Figure, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def save_all_figures(
    outputs: dict[str, pd.DataFrame],
    output_dir: str | Path,
) -> list[Path]:
    """Save the five figures supporting the consultation-capacity analysis."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    trajectories = outputs["trajectories"]
    daily = outputs["daily_metrics"]
    summary = outputs["summary"]
    selected_trajectories = trajectories[
        trajectories["scenario"].isin(BEHAVIOUR_SCENARIOS)
    ]
    selected_daily = daily[daily["scenario"].isin(BEHAVIOUR_SCENARIOS)]

    fig1, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True, sharey=True)
    for axis, scenario in zip(axes, BEHAVIOUR_SCENARIOS, strict=True):
        frame = selected_trajectories[selected_trajectories["scenario"] == scenario]
        for column, label in (
            ("S", "Susceptible"),
            ("I_P", "Infected"),
            ("I_W", "Worried-well"),
            ("R_P", "Recovered"),
        ):
            axis.plot(frame["day"], frame[column], label=label)
        axis.set_title(BEHAVIOUR_LABELS[scenario])
        axis.set_xlabel("Day")
    axes[0].set_ylabel("Population fraction")
    axes[-1].legend(frameon=False)
    path1 = _finish(fig1, destination / "figure_1_compartments.png")

    fig2, axis2 = plt.subplots(figsize=(7, 4))
    for scenario in BEHAVIOUR_SCENARIOS:
        frame = selected_trajectories[selected_trajectories["scenario"] == scenario]
        axis2.plot(frame["day"], frame["risk_ratio"], label=BEHAVIOUR_LABELS[scenario])
    axis2.axhline(1.0, color="black", linestyle="--", linewidth=1)
    axis2.set(xlabel="Day", ylabel="Worried-well / infected ratio")
    axis2.legend(frameon=False)
    path2 = _finish(fig2, destination / "figure_2_risk_ratio.png")

    default_daily = selected_daily[selected_daily["scenario"] == "behaviour_alpha_1"]
    fig3, axis3 = plt.subplots(figsize=(7, 4))
    axis3.fill_between(
        default_daily["day"],
        default_daily["demand_p05"],
        default_daily["demand_p95"],
        alpha=0.25,
        label="5th-95th percentile",
    )
    axis3.plot(
        default_daily["day"],
        default_daily["mean_demand"],
        label="Deterministic demand",
    )
    axis3.set(xlabel="Day", ylabel="Consultation demand")
    axis3.legend(frameon=False)
    path3 = _finish(fig3, destination / "figure_3_demand_uncertainty.png")

    fig4, axis4 = plt.subplots(figsize=(7, 4))
    for scenario in BEHAVIOUR_SCENARIOS:
        frame = selected_daily[selected_daily["scenario"] == scenario]
        axis4.plot(
            frame["day"],
            frame["optimized_capacity"],
            label=BEHAVIOUR_LABELS[scenario],
        )
    axis4.set(xlabel="Day", ylabel="Optimal consultation capacity")
    axis4.legend(frameon=False)
    path4 = _finish(fig4, destination / "figure_4_optimal_capacity.png")

    sensitivity = summary[summary["group"].isin(["uncertainty", "cost"])].merge(
        outputs["parameters"][["name", "alpha", "cv", "underage"]],
        left_on="scenario",
        right_on="name",
        how="left",
    )
    fig5, axes5 = plt.subplots(1, 2, figsize=(10, 4))
    uncertainty = sensitivity[sensitivity["group"] == "uncertainty"]
    for alpha, frame in uncertainty.groupby("alpha"):
        ordered = frame.sort_values("cv")
        axes5[0].plot(
            ordered["cv"],
            ordered["optimized_total_cost"],
            marker="o",
            label=f"alpha={alpha:g}",
        )
    axes5[0].set(
        xlabel="Coefficient of variation",
        ylabel="Optimized total expected cost",
    )
    axes5[0].legend(frameon=False)
    costs = sensitivity[sensitivity["group"] == "cost"].sort_values("underage")
    axes5[1].plot(costs["underage"], costs["relative_cost_reduction_pct"], marker="o")
    axes5[1].set(
        xlabel="Underage cost",
        ylabel="Cost reduction vs mean policy (%)",
    )
    path5 = _finish(fig5, destination / "figure_5_sensitivity.png")

    return [path1, path2, path3, path4, path5]
