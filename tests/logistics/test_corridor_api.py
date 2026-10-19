def _create_route(client, distance: float | None) -> int:
    payload = {
        "route_type": "custom",
        "stops": ["Bodega Central", "Cliente A"],
        "departure_date": "2026-09-10",
        "vehicle_type": "furgon",
    }
    if distance is not None:
        payload["total_distance_km"] = distance
    response = client.post("/logistics/routes", json=payload)
    assert response.status_code == 201
    return response.json()["route_id"]


def test_create_corridor_sums_distance_of_existing_routes(client):
    first = _create_route(client, 10.0)
    second = _create_route(client, 2.5)

    response = client.post(
        "/logistics/corridors", json={"name": "Norte", "route_ids": [first, second]}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Norte"
    assert body["total_distance_km"] == 12.5
    assert len(body["routes"]) == 2


def test_create_corridor_with_unknown_route_returns_404(client):
    response = client.post(
        "/logistics/corridors", json={"name": "Norte", "route_ids": [9999]}
    )

    assert response.status_code == 404
    assert "9999" in response.json()["detail"]


def test_create_corridor_without_routes_returns_422(client):
    response = client.post("/logistics/corridors", json={"name": "Norte", "route_ids": []})

    assert response.status_code == 422


def test_create_corridor_counts_route_without_distance_as_zero(client):
    with_distance = _create_route(client, 7.0)
    without_distance = _create_route(client, None)

    response = client.post(
        "/logistics/corridors",
        json={"name": "Mixto", "route_ids": [with_distance, without_distance]},
    )

    assert response.status_code == 201
    assert response.json()["total_distance_km"] == 7.0
