def test_ingest_vendor_a_returns_201_and_persists_event(client):
    response = client.post(
        "/iot/sensors/a/ingest",
        json={"product_id": "PROD-iot-1", "stage": "transporte"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["product_id"] == "PROD-iot-1"
    assert body["sensor_type"] == "temperatura"
    assert body["reading_value"] == 23.8
    assert body["unit"] == "°C"
    assert body["notified_via"] == "mqtt"
    assert body["message"]

    events = client.get("/tracking/events/PROD-iot-1").json()
    assert len(events) == 1
    assert events[0]["event_type"] == "sensor"


def test_ingest_faulty_vendor_returns_400_and_does_not_persist(client):
    response = client.post(
        "/iot/sensors/a-faulty/ingest",
        json={"product_id": "PROD-iot-2", "stage": "transporte"},
    )

    assert response.status_code == 400
    assert client.get("/tracking/events/PROD-iot-2").json() == []


def test_ingest_unknown_vendor_returns_400(client):
    response = client.post(
        "/iot/sensors/fabricante-x/ingest",
        json={"product_id": "PROD-iot-3", "stage": "transporte"},
    )

    assert response.status_code == 400
    assert "no soportado" in response.json()["detail"]


def test_ingest_missing_field_returns_422(client):
    response = client.post("/iot/sensors/a/ingest", json={"product_id": "PROD-iot-4"})

    assert response.status_code == 422
