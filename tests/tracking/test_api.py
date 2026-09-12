def test_register_sensor_event_returns_201(client):
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "sensor",
            "product_id": "PROD-api-1",
            "stage": "transporte",
            "sensor_type": "temperatura",
            "reading_value": 4.5,
            "unit": "C",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["event_type"] == "sensor"
    assert body["product_id"] == "PROD-api-1"
    assert body["details"]["sensor_type"] == "temperatura"


def test_register_stage_change_event_returns_201(client):
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "stage_change",
            "product_id": "PROD-api-2",
            "stage": "entrega",
            "previous_stage": "transporte",
            "responsible": "Transportista X",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["event_type"] == "stage_change"
    assert body["details"]["previous_stage"] == "transporte"


def test_register_event_with_unsupported_type_returns_422(client):
    response = client.post(
        "/tracking/events",
        json={"event_type": "tipo_raro", "product_id": "PROD-1", "stage": "x"},
    )

    assert response.status_code == 422


def test_register_sensor_event_missing_required_field_returns_422(client):
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "sensor",
            "product_id": "PROD-1",
            "stage": "transporte",
            # faltan sensor_type, reading_value, unit
        },
    )

    assert response.status_code == 422


def test_list_events_returns_events_for_product(client):
    client.post(
        "/tracking/events",
        json={
            "event_type": "stage_change",
            "product_id": "PROD-api-listado",
            "stage": "fabricacion",
            "previous_stage": "pendiente",
            "responsible": "Planta 1",
        },
    )

    response = client.get("/tracking/events/PROD-api-listado")

    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["product_id"] == "PROD-api-listado"


def test_list_events_returns_empty_list_for_unknown_product(client):
    response = client.get("/tracking/events/NO-EXISTE")

    assert response.status_code == 200
    assert response.json() == []
