def _register_stage_change(client, product_id: str, previous_stage: str, stage: str) -> None:
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "stage_change",
            "product_id": product_id,
            "stage": stage,
            "previous_stage": previous_stage,
            "responsible": "Planta 1",
        },
    )
    assert response.status_code == 201


def test_overview_returns_tracking_summary_and_forecast(client, auth_headers):
    _register_stage_change(client, "PROD-ov-1", "fabricacion", "transporte")
    _register_stage_change(client, "PROD-ov-1", "transporte", "entrega")

    response = client.get("/products/PROD-ov-1/overview", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["product_id"] == "PROD-ov-1"
    assert body["current_stage"] == "entrega"
    assert body["events_count"] == 2
    assert body["last_event_at"] is not None
    assert body["forecast"]["based_on_events"] == 2
    assert body["forecast"]["predicted_demand"] == 25.0


def test_overview_for_unknown_product_returns_empty_summary(client, auth_headers):
    response = client.get("/products/NO-EXISTE/overview", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["current_stage"] is None
    assert body["events_count"] == 0
    assert body["forecast"]["trend"] == "insuficientes datos"


def test_overview_without_token_returns_401(client):
    response = client.get("/products/PROD-ov-1/overview")

    assert response.status_code == 401


def test_overview_with_invalid_token_returns_401(client):
    response = client.get(
        "/products/PROD-ov-1/overview", headers={"Authorization": "Bearer no-es-un-jwt"}
    )

    assert response.status_code == 401
