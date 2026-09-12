from datetime import date

import pytest

from src.logistics.application.create_route import CreateDistributionRouteUseCase
from src.logistics.domain.entities import DistributionRoute


class _FakeDistributionRouteRepository:
    """Test double en memoria: cumple el puerto DistributionRouteRepository
    sin tocar ninguna base de datos."""

    def __init__(self):
        self.saved: list[DistributionRoute] = []

    def save(self, route: DistributionRoute) -> DistributionRoute:
        self.saved.append(route)
        return route

    def get(self, route_id: int) -> DistributionRoute | None:
        return None

    def list_all(self) -> list[DistributionRoute]:
        return list(self.saved)


def test_execute_with_standard_route_type_uses_director_recipe():
    repository = _FakeDistributionRouteRepository()
    use_case = CreateDistributionRouteUseCase(repository)

    route = use_case.execute(
        route_type="standard",
        stops=["Bodega Central", "Cliente A", "Cliente B"],
        departure_date=date(2026, 9, 10),
    )

    assert route.vehicle_type == "camion_estandar"
    assert route in repository.saved


def test_execute_with_express_route_type_uses_director_recipe():
    repository = _FakeDistributionRouteRepository()
    use_case = CreateDistributionRouteUseCase(repository)

    route = use_case.execute(
        route_type="express",
        stops=["Bodega Central", "Cliente A"],
        departure_date=date(2026, 9, 10),
    )

    assert route.vehicle_type == "moto_express"
    assert route in repository.saved


def test_execute_with_custom_route_type_uses_given_vehicle_type():
    repository = _FakeDistributionRouteRepository()
    use_case = CreateDistributionRouteUseCase(repository)

    route = use_case.execute(
        route_type="custom",
        stops=["Bodega Central", "Cliente A"],
        departure_date=date(2026, 9, 10),
        vehicle_type="furgon_refrigerado",
    )

    assert route.vehicle_type == "furgon_refrigerado"


def test_execute_with_custom_route_type_without_vehicle_type_raises_value_error():
    repository = _FakeDistributionRouteRepository()
    use_case = CreateDistributionRouteUseCase(repository)

    with pytest.raises(ValueError):
        use_case.execute(
            route_type="custom",
            stops=["Bodega Central", "Cliente A"],
            departure_date=date(2026, 9, 10),
        )


def test_execute_sets_total_distance_km_when_provided():
    repository = _FakeDistributionRouteRepository()
    use_case = CreateDistributionRouteUseCase(repository)

    route = use_case.execute(
        route_type="standard",
        stops=["Bodega Central", "Cliente A"],
        departure_date=date(2026, 9, 10),
        total_distance_km=15.3,
    )

    assert route.total_distance_km == 15.3
