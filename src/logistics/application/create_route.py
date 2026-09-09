from datetime import date
from typing import Literal

from src.logistics.domain.entities import DistributionRoute
from src.logistics.domain.repository import DistributionRouteRepository
from src.logistics.domain.route_builder import DistributionRouteBuilder
from src.logistics.domain.route_director import RouteDirector

RouteType = Literal["standard", "express", "custom"]


class CreateDistributionRouteUseCase:
    """Caso de uso: usa el Builder (directamente, o vía Director para las
    recetas estándar/express) para construir la ruta, y la persiste a
    través del puerto de repositorio."""

    def __init__(self, repository: DistributionRouteRepository):
        self._repository = repository

    def execute(
        self,
        route_type: RouteType,
        stops: list[str],
        departure_date: date,
        vehicle_type: str | None = None,
        total_distance_km: float | None = None,
    ) -> DistributionRoute:
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
