from datetime import date

from src.logistics.domain.route_builder import DistributionRouteBuilder
from src.logistics.domain.route_director import RouteDirector


def test_configure_standard_route_uses_standard_vehicle_and_no_special_notes():
    builder = DistributionRouteBuilder()
    stops = ["Bodega Central", "Cliente A", "Cliente B"]

    RouteDirector.configure_standard_route(builder, stops, date(2026, 9, 10))
    route = builder.build()

    assert route.vehicle_type == "camion_estandar"
    assert route.notes is None
    assert [stop.location for stop in route.stops] == stops


def test_configure_express_route_uses_express_vehicle_and_sets_notes():
    builder = DistributionRouteBuilder()
    stops = ["Bodega Central", "Cliente A"]

    RouteDirector.configure_express_route(builder, stops, date(2026, 9, 10))
    route = builder.build()

    assert route.vehicle_type == "moto_express"
    assert route.notes is not None
    assert [stop.location for stop in route.stops] == stops


def test_director_returns_the_same_builder_instance_for_chaining():
    builder = DistributionRouteBuilder()

    returned = RouteDirector.configure_standard_route(
        builder, ["Bodega Central", "Cliente A"], date(2026, 9, 10)
    )

    assert returned is builder
