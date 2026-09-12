from datetime import date

import pytest

from src.logistics.domain.entities import DistributionRoute
from src.logistics.domain.route_builder import DistributionRouteBuilder


def test_build_returns_distribution_route_with_ordered_stops():
    route = (
        DistributionRouteBuilder()
        .set_vehicle("camion_estandar")
        .set_departure_date(date(2026, 9, 10))
        .add_stop("Bodega Central")
        .add_stop("Cliente A")
        .add_stop("Cliente B")
        .build()
    )

    assert isinstance(route, DistributionRoute)
    assert route.vehicle_type == "camion_estandar"
    assert [stop.location for stop in route.stops] == [
        "Bodega Central",
        "Cliente A",
        "Cliente B",
    ]
    assert [stop.sequence for stop in route.stops] == [1, 2, 3]


def test_build_includes_optional_parts_when_set():
    route = (
        DistributionRouteBuilder()
        .set_vehicle("camion_estandar")
        .set_departure_date(date(2026, 9, 10))
        .add_stop("Bodega Central")
        .add_stop("Cliente A")
        .set_total_distance_km(42.5)
        .set_notes("Entrega prioritaria")
        .build()
    )

    assert route.total_distance_km == 42.5
    assert route.notes == "Entrega prioritaria"


def test_build_without_vehicle_raises_value_error():
    builder = (
        DistributionRouteBuilder()
        .set_departure_date(date(2026, 9, 10))
        .add_stop("Bodega Central")
        .add_stop("Cliente A")
    )

    with pytest.raises(ValueError):
        builder.build()


def test_build_without_departure_date_raises_value_error():
    builder = (
        DistributionRouteBuilder()
        .set_vehicle("camion_estandar")
        .add_stop("Bodega Central")
        .add_stop("Cliente A")
    )

    with pytest.raises(ValueError):
        builder.build()


def test_build_with_fewer_than_two_stops_raises_value_error():
    builder = (
        DistributionRouteBuilder()
        .set_vehicle("camion_estandar")
        .set_departure_date(date(2026, 9, 10))
        .add_stop("Bodega Central")
    )

    with pytest.raises(ValueError):
        builder.build()
