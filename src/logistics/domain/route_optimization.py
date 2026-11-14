from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from src.logistics.domain.location_catalog import (
    Location,
    distance_km,
    find_location,
    path_length_km,
)


class RouteOptimizationStrategy(ABC):
    """Strategy (GoF): un algoritmo intercambiable para ordenar las paradas
    de una ruta. La primera parada es el origen (la bodega de salida) y
    ninguna estrategia la mueve."""

    name: str
    description: str

    @abstractmethod
    def order(self, stops: Sequence[Location]) -> list[Location]:
        """Devuelve las paradas en el orden de visita propuesto."""


class KeepOrderStrategy(RouteOptimizationStrategy):
    name = "none"
    description = "Respeta el orden en que se ingresaron las paradas"

    def order(self, stops: Sequence[Location]) -> list[Location]:
        return list(stops)


class NearestNeighborStrategy(RouteOptimizationStrategy):
    name = "nearest_neighbor"
    description = "Desde cada parada visita la más cercana que falte"

    def order(self, stops: Sequence[Location]) -> list[Location]:
        if not stops:
            return []
        ordered = [stops[0]]
        pending = list(stops[1:])
        while pending:
            nearest = min(pending, key=lambda stop: distance_km(ordered[-1], stop))
            pending.remove(nearest)
            ordered.append(nearest)
        return ordered


class TwoOptStrategy(RouteOptimizationStrategy):
    name = "two_opt"
    description = "Parte del vecino más cercano e invierte tramos mientras acorten el recorrido"

    def order(self, stops: Sequence[Location]) -> list[Location]:
        best = NearestNeighborStrategy().order(stops)
        improved = True
        while improved:
            improved = False
            for start in range(1, len(best) - 1):
                for end in range(start + 1, len(best)):
                    candidate = best[:start] + best[start : end + 1][::-1] + best[end + 1 :]
                    if path_length_km(candidate) < path_length_km(best) - 1e-9:
                        best = candidate
                        improved = True
        return best


_STRATEGIES: Mapping[str, RouteOptimizationStrategy] = MappingProxyType(
    {
        strategy.name: strategy
        for strategy in (KeepOrderStrategy(), NearestNeighborStrategy(), TwoOptStrategy())
    }
)


def available_strategies() -> tuple[RouteOptimizationStrategy, ...]:
    return tuple(_STRATEGIES.values())


def get_strategy(name: str) -> RouteOptimizationStrategy:
    strategy = _STRATEGIES.get(name)
    if strategy is None:
        raise ValueError(f"Estrategia de optimización no soportada: '{name}'")
    return strategy


@dataclass(frozen=True)
class PlannedStops:
    strategy: str
    stop_names: tuple[str, ...]
    total_distance_km: float


class RoutePlanner:
    """Context del Strategy: resuelve las paradas contra el catálogo y delega
    el orden de visita en la estrategia que le inyecten."""

    def __init__(self, strategy: RouteOptimizationStrategy):
        self._strategy = strategy

    def plan(self, stop_names: Sequence[str]) -> PlannedStops:
        ordered = self._strategy.order(resolve_locations(stop_names))
        return PlannedStops(
            strategy=self._strategy.name,
            stop_names=tuple(location.name for location in ordered),
            total_distance_km=round(path_length_km(ordered), 1),
        )


def resolve_locations(stop_names: Sequence[str]) -> list[Location]:
    """Traduce nombres a ubicaciones del catálogo; falla si alguna no existe."""
    locations: list[Location] = []
    unknown: list[str] = []
    for name in stop_names:
        location = find_location(name)
        if location is None:
            unknown.append(name)
        else:
            locations.append(location)
    if unknown:
        raise ValueError(
            "Para calcular u optimizar la ruta, estas paradas deben estar en el "
            f"catálogo de ubicaciones: {', '.join(unknown)}"
        )
    return locations


def all_in_catalog(stop_names: Sequence[str]) -> bool:
    return all(find_location(name) is not None for name in stop_names)
