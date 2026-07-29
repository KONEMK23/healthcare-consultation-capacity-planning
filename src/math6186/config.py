from dataclasses import dataclass
from math import isclose


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
        rates = (
            self.beta_p,
            self.beta_w,
            self.beta_wp,
            self.gamma_p,
            self.gamma_w,
            self.delta_p,
        )
        if any(rate < 0.0 for rate in rates):
            raise ValueError("Transition rates must be non-negative.")
        if self.alpha <= 0.0:
            raise ValueError("alpha must be positive.")
        if len(self.initial_state) != 4:
            raise ValueError("initial_state must contain four values.")
        if any(value < 0.0 or value > 1.0 for value in self.initial_state):
            raise ValueError("Initial fractions must lie in [0, 1].")
        if not isclose(sum(self.initial_state), 1.0, abs_tol=1e-12):
            raise ValueError("Initial fractions must sum to one.")


@dataclass(frozen=True)
class DemandParameters:
    population: int = 100_000
    p_infected: float = 1.0
    p_worried: float = 0.5
    coefficient_of_variation: float = 0.15
    scenarios: int = 5_000
    seed: int = 6_186

    def __post_init__(self) -> None:
        if self.population <= 0 or self.scenarios <= 0:
            raise ValueError("population and scenarios must be positive.")
        if not 0.0 <= self.p_infected <= 1.0:
            raise ValueError("p_infected must lie in [0, 1].")
        if not 0.0 <= self.p_worried <= 1.0:
            raise ValueError("p_worried must lie in [0, 1].")
        if not 0.0 < self.coefficient_of_variation <= 1.0:
            raise ValueError("coefficient_of_variation must lie in (0, 1].")
        if self.seed < 0:
            raise ValueError("seed must be non-negative.")


@dataclass(frozen=True)
class NewsvendorCosts:
    underage: float = 5.0
    overage: float = 1.0

    def __post_init__(self) -> None:
        if self.underage <= 0.0 or self.overage <= 0.0:
            raise ValueError("underage and overage costs must be positive.")

    @property
    def critical_fractile(self) -> float:
        return self.underage / (self.underage + self.overage)
