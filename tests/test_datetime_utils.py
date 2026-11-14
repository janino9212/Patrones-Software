from datetime import datetime, timedelta, timezone

from src.shared.datetime_utils import ensure_utc


def test_naive_datetime_is_treated_as_utc():
    assert ensure_utc(datetime(2026, 11, 1, 12, 0)) == datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


def test_aware_datetime_is_converted_to_utc():
    bogota = timezone(timedelta(hours=-5))

    result = ensure_utc(datetime(2026, 11, 1, 7, 0, tzinfo=bogota))

    assert result == datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
    assert result.utcoffset() == timedelta(0)


def test_event_timestamps_from_the_api_carry_a_utc_offset(client):
    client.post(
        "/tracking/events",
        json={
            "event_type": "stage_change",
            "product_id": "PROD-tz",
            "stage": "transporte",
            "previous_stage": "fabricacion",
            "responsible": "Planta 1",
        },
    )

    (event,) = client.get("/tracking/events/PROD-tz").json()

    assert event["timestamp"].endswith(("Z", "+00:00"))
