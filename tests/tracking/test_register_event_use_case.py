import pytest

from src.tracking.application.register_event import RegisterTrackingEventUseCase
from src.tracking.domain.entities import TrackingEvent
from src.tracking.domain.event_factory import UnsupportedEventTypeError


class _FakeTrackingEventRepository:
    """Test double en memoria: cumple el puerto TrackingEventRepository
    sin tocar ninguna base de datos."""

    def __init__(self):
        self.saved: list[TrackingEvent] = []

    def save(self, event: TrackingEvent) -> TrackingEvent:
        self.saved.append(event)
        return event

    def list_by_product(self, product_id: str) -> list[TrackingEvent]:
        return [event for event in self.saved if event.product_id == product_id]


def test_execute_creates_and_saves_sensor_event():
    repository = _FakeTrackingEventRepository()
    use_case = RegisterTrackingEventUseCase(repository)

    event = use_case.execute(
        "sensor",
        {
            "product_id": "PROD-1",
            "stage": "transporte",
            "sensor_type": "temperatura",
            "reading_value": 4.5,
            "unit": "C",
        },
    )

    assert event in repository.saved
    assert event.sensor_type == "temperatura"


def test_execute_creates_and_saves_stage_change_event():
    repository = _FakeTrackingEventRepository()
    use_case = RegisterTrackingEventUseCase(repository)

    event = use_case.execute(
        "stage_change",
        {
            "product_id": "PROD-1",
            "stage": "entrega",
            "previous_stage": "transporte",
            "responsible": "Transportista X",
        },
    )

    assert event in repository.saved
    assert event.previous_stage == "transporte"


def test_execute_with_unsupported_event_type_raises_and_does_not_save():
    repository = _FakeTrackingEventRepository()
    use_case = RegisterTrackingEventUseCase(repository)

    with pytest.raises(UnsupportedEventTypeError):
        use_case.execute("tipo_invalido", {"product_id": "PROD-1"})

    assert repository.saved == []
