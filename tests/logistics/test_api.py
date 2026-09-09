def test_create_standard_route_returns_201(client):
    response = client.post(
        "/logistics/routes",
        json={
            "route_type": "standard",
            "stops": ["Bodega Central", "Cliente A", "Cliente B"],
            "departure_date": "2026-09-10",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["vehicle_type"] == "camion_estandar"
    assert len(body["stops"]) == 3
    assert body["route_id"] is not None


def test_create_express_route_returns_201(client):
    response = client.post(
        "/logistics/routes",
        json={
            "route_type": "express",
            "stops": ["Bodega Central", "Cliente A"],
            "departure_date": "2026-09-10",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["vehicle_type"] == "moto_express"
    assert body["notes"] is not None


def test_create_custom_route_without_vehicle_type_returns_400(client):
    response = client.post(
        "/logistics/routes",
        json={
            "route_type": "custom",
            "stops": ["Bodega Central", "Cliente A"],
            "departure_date": "2026-09-10",
        },
    )

    assert response.status_code == 400


def test_create_route_with_fewer_than_two_stops_returns_422(client):
    response = client.post(
        "/logistics/routes",
        json={
            "route_type": "standard",
            "stops": ["Bodega Central"],
            "departure_date": "2026-09-10",
        },
    )

    assert response.status_code == 422


def test_get_route_returns_created_route(client):
    create_response = client.post(
        "/logistics/routes",
        json={
            "route_type": "standard",
            "stops": ["Bodega Central", "Cliente A"],
            "departure_date": "2026-09-10",
        },
    )
    route_id = create_response.json()["route_id"]

    response = client.get(f"/logistics/routes/{route_id}")

    assert response.status_code == 200
    assert response.json()["route_id"] == route_id


def test_get_route_with_unknown_id_returns_404(client):
    response = client.get("/logistics/routes/999999")

    assert response.status_code == 404


def test_list_routes_returns_created_routes(client):
    client.post(
        "/logistics/routes",
        json={
            "route_type": "standard",
            "stops": ["Bodega Central", "Cliente A"],
            "departure_date": "2026-09-10",
        },
    )

    response = client.get("/logistics/routes")

    assert response.status_code == 200
    assert len(response.json()) >= 1
