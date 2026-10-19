from abc import ABC, abstractmethod

from src.iot.domain.notification_channel import NotificationChannel


class NotificationDispatcher(ABC):
    """Abstraction (GoF Bridge): QUÉ TAN URGENTE es la notificación.
    Delega el envío real en un NotificationChannel."""

    def __init__(self, channel: NotificationChannel):
        self._channel = channel

    @abstractmethod
    def dispatch(self, message: str) -> None:
        ...


class UrgentNotificationDispatcher(NotificationDispatcher):
    def dispatch(self, message: str) -> None:
        self._channel.send(f"URGENTE: {message}")


class RoutineNotificationDispatcher(NotificationDispatcher):
    def dispatch(self, message: str) -> None:
        self._channel.send(f"Registro de auditoría: {message}")


_CANAL_TO_CHANNEL = {"iot-monitor": "mqtt", "logistics-audit": "webhook"}
_CANAL_TO_DISPATCHER = {
    "iot-monitor": UrgentNotificationDispatcher,
    "logistics-audit": RoutineNotificationDispatcher,
}


def resolve_channel_name(canal: str) -> str:
    return _CANAL_TO_CHANNEL.get(canal, "webhook")


def build_dispatcher(canal: str, channel: NotificationChannel) -> NotificationDispatcher:
    dispatcher_cls = _CANAL_TO_DISPATCHER.get(canal, RoutineNotificationDispatcher)
    return dispatcher_cls(channel)
