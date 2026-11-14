import pytest

from src.tracking.domain.validation_chain import (
    EventValidationHandler,
    EventValidationRequest,
    FiniteReadingHandler,
    MissingFieldError,
    NonBlankTextHandler,
    ProductIdentifierHandler,
    RequiredFieldsHandler,
    build_default_validation_chain,
)

_VALID_SENSOR = {
    "product_id": "PROD-1",
    "stage": "transporte",
    "sensor_type": "temperatura",
    "reading_value": 4.5,
    "unit": "C",
}
_VALID_STAGE_CHANGE = {
    "product_id": "PROD-1",
    "stage": "entrega",
    "previous_stage": "transporte",
    "responsible": "Transportista X",
}


class _RecordingHandler(EventValidationHandler):
    def __init__(self, name: str, log: list[str], fails: bool = False):
        super().__init__()
        self._name = name
        self._log = log
        self._fails = fails

    def _check(self, request: EventValidationRequest) -> None:
        self._log.append(self._name)
        if self._fails:
            raise ValueError(f"{self._name} rechazó el evento")


def _sensor(**overrides) -> EventValidationRequest:
    return EventValidationRequest("sensor", {**_VALID_SENSOR, **overrides})


def test_request_passes_through_every_handler_in_order():
    log: list[str] = []
    head = _RecordingHandler("a", log)
    head.set_next(_RecordingHandler("b", log)).set_next(_RecordingHandler("c", log))

    head.handle(_sensor())

    assert log == ["a", "b", "c"]


def test_failing_handler_stops_the_chain():
    log: list[str] = []
    head = _RecordingHandler("a", log)
    head.set_next(_RecordingHandler("b", log, fails=True)).set_next(_RecordingHandler("c", log))

    with pytest.raises(ValueError, match="b rechazó"):
        head.handle(_sensor())

    assert log == ["a", "b"]


@pytest.mark.parametrize(
    "event_type, data", [("sensor", _VALID_SENSOR), ("stage_change", _VALID_STAGE_CHANGE)]
)
def test_default_chain_accepts_valid_events(event_type, data):
    build_default_validation_chain().handle(EventValidationRequest(event_type, data))


@pytest.mark.parametrize("missing", ["product_id", "stage", "sensor_type", "reading_value", "unit"])
def test_required_fields_handler_reports_the_missing_sensor_field(missing):
    data = {key: value for key, value in _VALID_SENSOR.items() if key != missing}

    with pytest.raises(MissingFieldError, match=missing):
        RequiredFieldsHandler().handle(EventValidationRequest("sensor", data))


def test_required_fields_handler_treats_none_as_missing():
    with pytest.raises(MissingFieldError, match="responsible"):
        RequiredFieldsHandler().handle(
            EventValidationRequest("stage_change", {**_VALID_STAGE_CHANGE, "responsible": None})
        )


def test_non_blank_handler_rejects_whitespace_only_text():
    with pytest.raises(ValueError, match="stage"):
        NonBlankTextHandler().handle(_sensor(stage="   "))


def test_product_identifier_handler_rejects_spaces_and_long_ids():
    handler = ProductIdentifierHandler()

    with pytest.raises(ValueError, match="espacios"):
        handler.handle(_sensor(product_id="PROD 1"))
    with pytest.raises(ValueError, match="100"):
        handler.handle(_sensor(product_id="P" * 101))


@pytest.mark.parametrize("value", [float("nan"), float("inf"), "4.5", True])
def test_finite_reading_handler_rejects_non_finite_or_non_numeric_values(value):
    with pytest.raises(ValueError, match="lectura"):
        FiniteReadingHandler().handle(_sensor(reading_value=value))


def test_finite_reading_handler_ignores_stage_change_events():
    FiniteReadingHandler().handle(EventValidationRequest("stage_change", _VALID_STAGE_CHANGE))
