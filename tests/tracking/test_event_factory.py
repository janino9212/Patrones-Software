import pytest

from src.tracking.domain.entities import SensorTrackingEvent, StageChangeTrackingEvent
from src.tracking.domain.event_factory import (
    SensorEventCreator,
    StageChangeEventCreator,
    UnsupportedEventTypeError,
    get_creator,
)


def test_get_creator_returns_sensor_creator_for_sensor_type():
    creator = get_creator("sensor")

    assert isinstance(creator, SensorEventCreator)


def test_get_creator_returns_stage_change_creator_for_stage_change_type():
    creator = get_creator("stage_change")

    assert isinstance(creator, StageChangeEventCreator)


def test_get_creator_raises_for_unknown_event_type():
    with pytest.raises(UnsupportedEventTypeError):
        get_creator("tipo_inexistente")


def test_sensor_event_creator_builds_sensor_tracking_event():
    creator = SensorEventCreator()
    raw_data = {
        "product_id": "PROD-1",
        "stage": "transporte",
        "sensor_type": "temperatura",
        "reading_value": 4.5,
        "unit": "C",
    }

    event = creator.create_event(raw_data)

    assert isinstance(event, SensorTrackingEvent)
    assert event.product_id == "PROD-1"
    assert event.sensor_type == "temperatura"
    assert event.reading_value == 4.5


def test_stage_change_event_creator_builds_stage_change_tracking_event():
    creator = StageChangeEventCreator()
    raw_data = {
        "product_id": "PROD-1",
        "stage": "entrega",
        "previous_stage": "transporte",
        "responsible": "Transportista X",
    }

    event = creator.create_event(raw_data)

    assert isinstance(event, StageChangeTrackingEvent)
    assert event.previous_stage == "transporte"
    assert event.responsible == "Transportista X"


def test_sensor_event_creator_raises_key_error_on_missing_field():
    creator = SensorEventCreator()

    with pytest.raises(KeyError):
        creator.create_event({"product_id": "PROD-1", "stage": "transporte"})
