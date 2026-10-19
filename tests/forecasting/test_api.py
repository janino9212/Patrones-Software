def _register_stage_change(client, product_id: str) -> None:
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "stage_change",
            "product_id": product_id,
            "stage": "transporte",
            "previous_stage": "fabricacion",
            "responsible": "Planta 1",
        },
    )
    assert response.status_code == 201


def test_report_for_unknown_product_returns_200_with_no_data(client, auth_headers):
    response = client.get("/forecasting/reports/NO-EXISTE", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["product_id"] == "NO-EXISTE"
    assert body["based_on_events"] == 0
    assert body["trend"] == "insuficientes datos"


def test_report_uses_tracking_events_of_the_product(client, auth_headers):
    for _ in range(3):
        _register_stage_change(client, "PROD-fc-1")

    body = client.get("/forecasting/reports/PROD-fc-1", headers=auth_headers).json()

    assert body["based_on_events"] == 3
    assert body["predicted_demand"] == 37.5
    assert body["trend"] == "alza"
    assert len(body["confidence_interval"]) == 2


def test_report_without_token_returns_401(client):
    response = client.get("/forecasting/reports/PROD-fc-1")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_report_with_invalid_token_returns_401(client):
    response = client.get(
        "/forecasting/reports/PROD-fc-1", headers={"Authorization": "Bearer no-es-un-jwt"}
    )

    assert response.status_code == 401
