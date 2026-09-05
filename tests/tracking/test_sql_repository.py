from datetime import datetime, timezone

from src.tracking.domain.entities import SensorTrackingEvent, StageChangeTrackingEvent
from src.tracking.infrastructure.repository import SqlTrackingEventRepository


def test_save_and_list_sensor_event(db_session):
    repository = SqlTrackingEventRepository(db_session)
    event = SensorTrackingEvent(
        product_id="PROD-sensor",
        stage="transporte",
        timestamp=datetime.now(timezone.utc),
        sensor_type="temperatura",
        reading_value=4.5,
        unit="C",
    )

    repository.save(event)
    events = repository.list_by_product("PROD-sensor")

    assert len(events) == 1
    assert isinstance(events[0], SensorTrackingEvent)
    assert events[0].sensor_type == "temperatura"
    assert events[0].reading_value == 4.5


def test_save_and_list_stage_change_event(db_session):
    repository = SqlTrackingEventRepository(db_session)
    event = StageChangeTrackingEvent(
        product_id="PROD-stage",
        stage="entrega",
        timestamp=datetime.now(timezone.utc),
        previous_stage="transporte",
        responsible="Transportista X",
    )

    repository.save(event)
    events = repository.list_by_product("PROD-stage")

    assert len(events) == 1
    assert isinstance(events[0], StageChangeTrackingEvent)
    assert events[0].previous_stage == "transporte"


def test_list_by_product_returns_empty_for_unknown_product(db_session):
    repository = SqlTrackingEventRepository(db_session)

    assert repository.list_by_product("NO-EXISTE") == []


def test_list_by_product_only_returns_events_of_that_product(db_session):
    repository = SqlTrackingEventRepository(db_session)
    repository.save(
        SensorTrackingEvent(
            product_id="PROD-A",
            stage="transporte",
            timestamp=datetime.now(timezone.utc),
            sensor_type="gps",
            reading_value=1.0,
            unit="lat",
        )
    )
    repository.save(
        SensorTrackingEvent(
            product_id="PROD-B",
            stage="transporte",
            timestamp=datetime.now(timezone.utc),
            sensor_type="gps",
            reading_value=2.0,
            unit="lat",
        )
    )

    events = repository.list_by_product("PROD-A")

    assert len(events) == 1
    assert events[0].product_id == "PROD-A"
