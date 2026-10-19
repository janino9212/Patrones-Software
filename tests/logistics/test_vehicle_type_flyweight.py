import dataclasses
import threading
from datetime import date

import pytest

from src.logistics.domain.entities import DistributionRoute, RouteStop
from src.logistics.domain.vehicle_type import VehicleType, VehicleTypeFactory


def _route(vehicle_type: str) -> DistributionRoute:
    return DistributionRoute(
        vehicle_type=vehicle_type,
        departure_date=date(2026, 10, 1),
        stops=(RouteStop(1, "A"), RouteStop(2, "B")),
    )


def test_same_catalog_code_returns_the_same_shared_instance():
    assert VehicleTypeFactory.get("camion_estandar") is VehicleTypeFactory.get("camion_estandar")


def test_different_codes_return_different_flyweights():
    assert VehicleTypeFactory.get("camion_estandar") is not VehicleTypeFactory.get("moto_express")


def test_catalog_declares_intrinsic_state():
    assert VehicleTypeFactory.get("furgon_refrigerado").refrigerated is True
    assert VehicleTypeFactory.get("camion_estandar").refrigerated is False
    assert VehicleTypeFactory.get("moto_express").refrigerated is False


def test_flyweight_is_immutable():
    vehicle = VehicleTypeFactory.get("camion_estandar")

    with pytest.raises(dataclasses.FrozenInstanceError):
        vehicle.refrigerated = True


def test_unknown_code_is_not_pooled_to_avoid_unbounded_growth():
    size_before = VehicleTypeFactory.pool_size()

    unknown = VehicleTypeFactory.get("vehiculo-inventado-por-un-usuario")

    assert isinstance(unknown, VehicleType)
    assert unknown.code == "vehiculo-inventado-por-un-usuario"
    assert unknown.refrigerated is False
    assert VehicleTypeFactory.pool_size() == size_before


def test_many_routes_share_one_vehicle_flyweight():
    routes = [_route("camion_estandar") for _ in range(1000)]

    assert len({id(route.vehicle) for route in routes}) == 1


def test_route_exposes_vehicle_flyweight_for_its_code():
    assert _route("furgon_refrigerado").vehicle is VehicleTypeFactory.get("furgon_refrigerado")


def test_factory_returns_the_same_instance_under_concurrent_access():
    results: list[VehicleType] = []

    def worker():
        results.append(VehicleTypeFactory.get("moto_express"))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len({id(vehicle) for vehicle in results}) == 1


def test_api_response_exposes_refrigerated_flag(client):
    payload = {
        "route_type": "custom",
        "stops": ["Bodega Central", "Cliente A"],
        "departure_date": "2026-10-01",
    }
    refrigerated = client.post(
        "/logistics/routes", json={**payload, "vehicle_type": "furgon_refrigerado"}
    )
    standard = client.post("/logistics/routes", json={**payload, "route_type": "standard"})

    assert refrigerated.status_code == 201
    assert refrigerated.json()["refrigerated"] is True
    assert standard.json()["refrigerated"] is False
