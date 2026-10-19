import logging

import pytest

from src.iot.domain.notification_channel import NotificationChannel
from src.iot.domain.notification_dispatcher import (
    NotificationDispatcher,
    RoutineNotificationDispatcher,
    UrgentNotificationDispatcher,
    build_dispatcher,
    resolve_channel_name,
)
from src.iot.infrastructure.channels import MqttChannel, WebhookChannel


class _SpyChannel(NotificationChannel):
    def __init__(self):
        self.sent: list[str] = []

    def send(self, message: str) -> None:
        self.sent.append(message)


def test_urgent_dispatcher_prefixes_message_and_delegates_to_channel():
    channel = _SpyChannel()

    UrgentNotificationDispatcher(channel).dispatch("temperatura alta")

    assert channel.sent == ["URGENTE: temperatura alta"]


def test_routine_dispatcher_prefixes_message_and_delegates_to_channel():
    channel = _SpyChannel()

    RoutineNotificationDispatcher(channel).dispatch("cambio de etapa")

    assert channel.sent == ["Registro de auditoría: cambio de etapa"]


def test_base_dispatcher_cannot_be_instantiated():
    with pytest.raises(TypeError):
        NotificationDispatcher(_SpyChannel())


@pytest.mark.parametrize(
    "canal, expected_channel",
    [("iot-monitor", "mqtt"), ("logistics-audit", "webhook"), ("desconocido", "webhook")],
)
def test_resolve_channel_name(canal, expected_channel):
    assert resolve_channel_name(canal) == expected_channel


@pytest.mark.parametrize(
    "canal, expected_cls",
    [
        ("iot-monitor", UrgentNotificationDispatcher),
        ("logistics-audit", RoutineNotificationDispatcher),
        ("desconocido", RoutineNotificationDispatcher),
    ],
)
def test_build_dispatcher_selects_abstraction_by_canal(canal, expected_cls):
    assert isinstance(build_dispatcher(canal, _SpyChannel()), expected_cls)


@pytest.mark.parametrize(
    "channel_cls, tag", [(MqttChannel, "MQTT"), (WebhookChannel, "WEBHOOK")]
)
def test_concrete_channels_log_the_message(channel_cls, tag, caplog):
    with caplog.at_level(logging.INFO):
        channel_cls().send("hola")

    assert any(
        tag in record.getMessage() and "hola" in record.getMessage()
        for record in caplog.records
    )
