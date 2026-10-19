from datetime import date

from src.logistics.domain.entities import DistributionRoute, RouteStop
from src.logistics.domain.route_component import RouteComponent
from src.logistics.domain.route_corridor import RouteCorridor
from src.logistics.domain.route_leaf import SingleRoute


def _route(route_id: int, distance: float | None) -> DistributionRoute:
    return DistributionRoute(
        route_id=route_id,
        vehicle_type="camion_estandar",
        departure_date=date(2026, 9, 10),
        stops=(RouteStop(1, "A"), RouteStop(2, "B")),
        total_distance_km=distance,
    )


def test_single_route_exposes_its_own_distance_and_description():
    leaf = SingleRoute(_route(7, 12.5))

    assert leaf.total_distance_km() == 12.5
    assert leaf.describe() == "Ruta #7 (camion_estandar)"


def test_single_route_without_distance_counts_as_zero():
    assert SingleRoute(_route(1, None)).total_distance_km() == 0.0


def test_empty_corridor_has_zero_distance():
    assert RouteCorridor("vacio").total_distance_km() == 0


def test_corridor_sums_distances_of_its_children():
    corridor = RouteCorridor("norte")
    corridor.add(SingleRoute(_route(1, 10.0)))
    corridor.add(SingleRoute(_route(2, 5.5)))

    assert corridor.total_distance_km() == 15.5
    assert corridor.describe() == "Corredor 'norte' (2 componentes)"


def test_corridor_can_contain_other_corridors():
    inner = RouteCorridor("interno")
    inner.add(SingleRoute(_route(1, 4.0)))
    outer = RouteCorridor("externo")
    outer.add(inner)
    outer.add(SingleRoute(_route(2, 6.0)))

    assert isinstance(inner, RouteComponent)
    assert outer.total_distance_km() == 10.0
