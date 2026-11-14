from datetime import date
from typing import Literal

from src.logistics.domain.entities import DistributionRoute
from src.logistics.domain.repository import DistributionRouteRepository
from src.logistics.domain.route_builder import DistributionRouteBuilder
from src.logistics.domain.route_director import RouteDirector
from src.logistics.domain.route_optimization import (
    KeepOrderStrategy,
    RoutePlanner,
    all_in_catalog,
    get_strategy,
)

RouteType = Literal["standard", "express", "custom"]


class CreateDistributionRouteUseCase:
    """Caso de uso: ordena las paradas con la estrategia de optimización
    elegida (Strategy), usa el Builder (directamente, o vía Director para las
    recetas estándar/express) para construir la ruta, y la persiste a través
    del puerto de repositorio."""

    def __init__(self, repository: DistributionRouteRepository):
        self._repository = repository

    def execute(
        self,
        route_type: RouteType,
        stops: list[str],
        departure_date: date,
        vehicle_type: str | None = None,
        total_distance_km: float | None = None,
        optimization: str = KeepOrderStrategy.name,
    ) -> DistributionRoute:
        stops, total_distance_km = self._plan_stops(stops, total_distance_km, optimization)
        builder = DistributionRouteBuilder()

        if route_type == "standard":
            RouteDirector.configure_standard_route(builder, stops, departure_date)
        elif route_type == "express":
            RouteDirector.configure_express_route(builder, stops, departure_date)
        elif route_type == "custom":
            if vehicle_type is None:
                raise ValueError("route_type 'custom' requiere especificar vehicle_type")
            builder.set_vehicle(vehicle_type).set_departure_date(departure_date)
            for stop in stops:
                builder.add_stop(stop)
        else:
            raise ValueError(f"route_type no soportado: '{route_type}'")

        if total_distance_km is not None:
            builder.set_total_distance_km(total_distance_km)

        route = builder.build()
        return self._repository.save(route)

    @staticmethod
    def _plan_stops(
        stops: list[str], total_distance_km: float | None, optimization: str
    ) -> tuple[list[str], float | None]:
        """Con una estrategia de optimización, el orden y la distancia los
        calcula el planificador. Sin ella se respeta el orden recibido, y la
        distancia solo se calcula si no vino y todas las paradas son del
        catálogo."""
        strategy = get_strategy(optimization)
        is_optimizing = strategy.name != KeepOrderStrategy.name
        can_compute = total_distance_km is None and all_in_catalog(stops)
        if not is_optimizing and not can_compute:
            return stops, total_distance_km

        planned = RoutePlanner(strategy).plan(stops)
        return list(planned.stop_names), planned.total_distance_km
