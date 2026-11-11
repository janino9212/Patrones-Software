from datetime import date

from src.logistics.domain.entities import DistributionRoute, RouteStop
from src.logistics.domain.route_corridor import RouteCorridor
from src.logistics.domain.route_leaf import SingleRoute

_CITIES = ["Bucaramanga", "Bogotá", "Girón", "Tunja"]


def _create(client, **overrides) -> dict:
    payload = {
        "route_type": "standard",
        "stops": ["Bodega Central", "Cliente A"],
        "departure_date": "2026-09-10",
        **overrides,
    }
    response = client.post("/logistics/routes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---- Strategy -------------------------------------------------------------


def test_route_without_optimization_keeps_order_and_computes_distance(client):
    body = _create(client, stops=_CITIES)

    assert [stop["location"] for stop in body["stops"]] == _CITIES
    assert body["total_distance_km"] > 0


def test_optimized_route_reorders_stops_and_is_shorter(client):
    plain = _create(client, stops=_CITIES)
    optimized = _create(client, stops=_CITIES, optimization="nearest_neighbor")

    assert [stop["location"] for stop in optimized["stops"]] == [
        "Bucaramanga", "Girón", "Tunja", "Bogotá",
    ]
    assert optimized["total_distance_km"] < plain["total_distance_km"]


def test_optimization_with_stop_outside_catalog_returns_400(client):
    response = client.post(
        "/logistics/routes",
        json={
            "route_type": "standard",
            "stops": ["Bucaramanga", "Cliente A"],
            "departure_date": "2026-09-10",
            "optimization": "two_opt",
        },
    )

    assert response.status_code == 400
    assert "Cliente A" in response.json()["detail"]


def test_free_text_stops_without_optimization_keep_distance_empty(client):
    body = _create(client)

    assert body["total_distance_km"] is None


def test_explicit_distance_is_kept_when_not_optimizing(client):
    body = _create(client, stops=_CITIES, total_distance_km=999.0)

    assert body["total_distance_km"] == 999.0


def test_compare_runs_every_strategy_on_the_same_stops(client):
    response = client.post("/logistics/optimizations/compare", json={"stops": _CITIES})

    assert response.status_code == 200
    by_name = {item["strategy"]: item for item in response.json()}
    assert set(by_name) == {"none", "nearest_neighbor", "two_opt"}
    assert by_name["two_opt"]["total_distance_km"] <= by_name["none"]["total_distance_km"]
    assert all(item["stops"][0] == "Bucaramanga" for item in by_name.values())


def test_compare_with_unknown_stop_returns_400(client):
    response = client.post(
        "/logistics/optimizations/compare", json={"stops": ["Bucaramanga", "Narnia"]}
    )

    assert response.status_code == 400


def test_catalog_endpoints_list_locations_and_vehicle_types(client):
    locations = client.get("/logistics/locations").json()
    vehicles = client.get("/logistics/vehicle-types").json()

    assert "Bucaramanga" in [location["name"] for location in locations]
    assert {"code": "furgon_refrigerado", "refrigerated": True} in vehicles


# ---- State ----------------------------------------------------------------


def test_new_route_starts_planned(client):
    body = _create(client)

    assert body["status"] == "planned"
    assert body["allowed_actions"] == ["dispatch", "cancel"]


def test_route_lifecycle_through_the_api(client):
    route_id = _create(client)["route_id"]

    dispatched = client.post(f"/logistics/routes/{route_id}/transition", json={"action": "dispatch"})
    delivered = client.post(f"/logistics/routes/{route_id}/transition", json={"action": "deliver"})

    assert dispatched.json()["status"] == "in_transit"
    assert delivered.json()["status"] == "delivered"
    assert delivered.json()["allowed_actions"] == []
    assert client.get(f"/logistics/routes/{route_id}").json()["status"] == "delivered"


def test_invalid_transition_returns_409_and_keeps_status(client):
    route_id = _create(client)["route_id"]

    response = client.post(f"/logistics/routes/{route_id}/transition", json={"action": "deliver"})

    assert response.status_code == 409
    assert "planificada" in response.json()["detail"]
    assert client.get(f"/logistics/routes/{route_id}").json()["status"] == "planned"


def test_transition_on_unknown_route_returns_404(client):
    response = client.post("/logistics/routes/9999/transition", json={"action": "dispatch"})

    assert response.status_code == 404


def test_transition_with_unknown_action_returns_422(client):
    route_id = _create(client)["route_id"]

    response = client.post(f"/logistics/routes/{route_id}/transition", json={"action": "volar"})

    assert response.status_code == 422


# ---- Iterator -------------------------------------------------------------


def _leaf(route_id: int) -> SingleRoute:
    route = DistributionRoute(
        vehicle_type="camion_estandar",
        departure_date=date(2026, 9, 10),
        stops=(RouteStop(1, "A"), RouteStop(2, "B")),
        total_distance_km=float(route_id),
        route_id=route_id,
    )
    return SingleRoute(route)


def test_iterator_walks_nested_corridors_depth_first():
    leaves = {number: _leaf(number) for number in range(1, 6)}
    inner = RouteCorridor("interno")
    inner.add(leaves[2])
    inner.add(leaves[3])
    deepest = RouteCorridor("profundo")
    deepest.add(leaves[4])
    inner.add(deepest)
    root = RouteCorridor("raíz")
    root.add(leaves[1])
    root.add(inner)
    root.add(leaves[5])

    assert list(root) == [leaves[1], leaves[2], leaves[3], leaves[4], leaves[5]]


def test_iterator_skips_empty_corridors_and_supports_independent_traversals():
    root = RouteCorridor("raíz")
    root.add(RouteCorridor("vacío"))
    only = _leaf(1)
    root.add(only)

    first, second = iter(root), iter(root)

    assert next(first) is only
    assert next(second) is only
    assert list(RouteCorridor("sin hijos")) == []


def test_nested_corridor_api_lists_every_route_and_sums_distance(client):
    ids = [
        _create(client, route_type="custom", vehicle_type="furgon", total_distance_km=km)["route_id"]
        for km in (10.0, 2.5, 4.0)
    ]

    response = client.post(
        "/logistics/corridors",
        json={
            "name": "Nacional",
            "route_ids": [ids[0]],
            "sub_corridors": [{"name": "Santander", "route_ids": [ids[1], ids[2]]}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["total_distance_km"] == 16.5
    assert len(body["routes"]) == 3
    assert body["routes"][0].startswith(f"Ruta #{ids[0]}")


def test_corridor_without_routes_or_sub_corridors_returns_422(client):
    response = client.post("/logistics/corridors", json={"name": "Vacío"})

    assert response.status_code == 422


def test_corridor_nested_too_deep_returns_422(client):
    payload: dict = {"name": "n5", "route_ids": [1]}
    for level in range(4, 0, -1):
        payload = {"name": f"n{level}", "sub_corridors": [payload]}

    response = client.post("/logistics/corridors", json=payload)

    assert response.status_code == 422
