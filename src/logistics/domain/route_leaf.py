from src.logistics.domain.entities import DistributionRoute
from src.logistics.domain.route_component import RouteComponent


class SingleRoute(RouteComponent):
    def __init__(self, route: DistributionRoute):
        self._route = route

    def total_distance_km(self) -> float:
        return self._route.total_distance_km or 0.0

    def describe(self) -> str:
        return f"Ruta #{self._route.route_id} ({self._route.vehicle_type})"