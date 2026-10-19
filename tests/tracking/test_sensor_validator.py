from datetime import datetime, timezone

import pytest

from src.tracking.domain.entities import SensorTrackingEvent
from src.tracking.infrastructure.factories.sensor_processing_factory import SensorEventValidator


def _sensor_event(value: float, unit: str, sensor_type: str = "temperatura") -> SensorTrackingEvent:
    return SensorTrackingEvent(
        product_id="PROD-1",
        stage="transporte",
        timestamp=datetime.now(timezone.utc),
        sensor_type=sensor_type,
        reading_value=value,
        unit=unit,
    )


@pytest.mark.parametrize("unit", ["°C", "C"])
def test_rejects_temperature_below_physical_range(unit):
    with pytest.raises(ValueError):
        SensorEventValidator().validate(_sensor_event(-60.0, unit))


@pytest.mark.parametrize("unit", ["°C", "C"])
@pytest.mark.parametrize("value", [-50.0, 0.0, 4.5, 23.8])
def test_accepts_plausible_temperature(unit, value):
    SensorEventValidator().validate(_sensor_event(value, unit))


def test_does_not_apply_temperature_rule_to_other_units():
    SensorEventValidator().validate(_sensor_event(-80.0, "lat", sensor_type="gps"))


def test_api_returns_400_when_temperature_out_of_range(client):
    response = client.post(
        "/tracking/events",
        json={
            "event_type": "sensor",
            "product_id": "PROD-fuera-rango",
            "stage": "transporte",
            "sensor_type": "temperatura",
            "reading_value": -60.0,
            "unit": "C",
        },
    )

    assert response.status_code == 400
    assert client.get("/tracking/events/PROD-fuera-rango").json() == []
