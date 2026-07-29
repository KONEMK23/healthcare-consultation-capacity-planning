from dataclasses import dataclass
from math import isclose, isfinite
from numbers import Integral, Real

import numpy as np


def _finite_real(name: str, value: object) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (Real, np.integer, np.floating)
    ):
        raise ValueError(f"{name} must be a finite real number.")
    normalized = float(value)
    if not isfinite(normalized):
        raise ValueError(f"{name} must be a finite real number.")
    return normalized


def _integer(name: str, value: object, *, positive: bool) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (Integral, np.integer)
    ):
        qualifier = "positive" if positive else "non-negative"
        raise ValueError(f"{name} must be a {qualifier} integer.")
    normalized = int(value)
    if (positive and normalized <= 0) or (not positive and normalized < 0):
        qualifier = "positive" if positive else "non-negative"
        raise ValueError(f"{name} must be a {qualifier} integer.")
    return normalized


@dataclass(frozen=True)
class ModelParameters:
    beta_p: float = 0.74
    beta_w: float = 0.70
    beta_wp: float = 0.70
    gamma_p: float = 1.0 / 14.0
    gamma_w: float = 1.0 / 14.0
    delta_p: float = 1.0 / 240.0
    alpha: float = 1.0
    initial_state: tuple[float, float, float, float] = (0.98, 0.01, 0.01, 0.0)

    def __post_init__(self) -> None:
        for name in ("beta_p", "beta_w", "beta_wp", "gamma_p", "gamma_w", "delta_p"):
            value = _finite_real(name, getattr(self, name))
            if value < 0.0:
                raise ValueError(f"{name} must be non-negative.")
            object.__setattr__(self, name, value)
        alpha = _finite_real("alpha", self.alpha)
        if alpha <= 0.0:
            raise ValueError("alpha must be positive.")
        object.__setattr__(self, "alpha", alpha)
        try:
            state = tuple(self.initial_state)
        except TypeError as exc:
            raise ValueError("initial_state must contain four finite real values.") from exc
        if len(state) != 4:
            raise ValueError("initial_state must contain four values.")
        normalized_state = tuple(
            _finite_real(f"initial_state[{index}]", value)
            for index, value in enumerate(state)
        )
        if any(value < 0.0 or value > 1.0 for value in normalized_state):
            raise ValueError("initial_state fractions must lie in [0, 1].")
        if not isclose(sum(normalized_state), 1.0, abs_tol=1e-12):
            raise ValueError("Initial fractions must sum to one.")
        object.__setattr__(self, "initial_state", normalized_state)


@dataclass(frozen=True)
class DemandParameters:
    population: int = 100_000
    p_infected: float = 1.0
    p_worried: float = 0.5
    coefficient_of_variation: float = 0.15
    scenarios: int = 5_000
    seed: int = 6_186

    def __post_init__(self) -> None:
        population = _integer("population", self.population, positive=True)
        scenarios = _integer("scenarios", self.scenarios, positive=True)
        seed = _integer("seed", self.seed, positive=False)
        p_infected = _finite_real("p_infected", self.p_infected)
        p_worried = _finite_real("p_worried", self.p_worried)
        coefficient_of_variation = _finite_real(
            "coefficient_of_variation", self.coefficient_of_variation
        )
        if not 0.0 <= p_infected <= 1.0:
            raise ValueError("p_infected must lie in [0, 1].")
        if not 0.0 <= p_worried <= 1.0:
            raise ValueError("p_worried must lie in [0, 1].")
        if not 0.0 < coefficient_of_variation <= 1.0:
            raise ValueError("coefficient_of_variation must lie in (0, 1].")
        object.__setattr__(self, "population", population)
        object.__setattr__(self, "scenarios", scenarios)
        object.__setattr__(self, "seed", seed)
        object.__setattr__(self, "p_infected", p_infected)
        object.__setattr__(self, "p_worried", p_worried)
        object.__setattr__(
            self, "coefficient_of_variation", coefficient_of_variation
        )


@dataclass(frozen=True)
class NewsvendorCosts:
    underage: float = 5.0
    overage: float = 1.0

    def __post_init__(self) -> None:
        underage = _finite_real("underage", self.underage)
        overage = _finite_real("overage", self.overage)
        if underage <= 0.0:
            raise ValueError("underage must be positive.")
        if overage <= 0.0:
            raise ValueError("overage must be positive.")
        object.__setattr__(self, "underage", underage)
        object.__setattr__(self, "overage", overage)

    @property
    def critical_fractile(self) -> float:
        if self.underage >= self.overage:
            return 1.0 / (1.0 + self.overage / self.underage)
        ratio = self.underage / self.overage
        return ratio / (1.0 + ratio)
