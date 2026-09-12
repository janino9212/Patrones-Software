from datetime import date

from src.logistics.domain.entities import DistributionRoute, RouteStop
from src.logistics.infrastructure.repository import SqlDistributionRouteRepository


def _sample_route(**overrides) -> DistributionRoute:
    defaults = dict(
        vehicle_type="camion_estandar",
        departure_date=date(2026, 9, 10),
        stops=(
            RouteStop(sequence=1, location="Bodega Central"),
            RouteStop(sequence=2, location="Cliente A"),
        ),
        total_distance_km=10.0,
        notes=None,
    )
    defaults.update(overrides)
    return DistributionRoute(**defaults)


def test_save_assigns_route_id_and_persists_stops(db_session):
    repository = SqlDistributionRouteRepository(db_session)

    saved = repository.save(_sample_route())

    assert saved.route_id is not None
    assert [stop.location for stop in saved.stops] == ["Bodega Central", "Cliente A"]


def test_get_returns_the_saved_route(db_session):
    repository = SqlDistributionRouteRepository(db_session)
    saved = repository.save(_sample_route())

    found = repository.get(saved.route_id)

    assert found is not None
    assert found.route_id == saved.route_id
    assert found.vehicle_type == "camion_estandar"


def test_get_returns_none_for_unknown_route_id(db_session):
    repository = SqlDistributionRouteRepository(db_session)

    assert repository.get(999999) is None


def test_list_all_returns_every_saved_route(db_session):
    repository = SqlDistributionRouteRepository(db_session)
    repository.save(_sample_route())
    repository.save(_sample_route(vehicle_type="moto_express"))

    routes = repository.list_all()

    assert len(routes) == 2
