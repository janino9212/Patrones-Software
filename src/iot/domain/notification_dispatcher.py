from src.iot.domain.notification_channel import NotificationChannel


class NotificationDispatcher:
    """Abstraction (GoF Bridge): QUÉ TAN URGENTE es la notificación.
    Delega el envío real en un NotificationChannel."""

    def __init__(self, channel: NotificationChannel):
        self._channel = channel

    def dispatch(self, message: str) -> None:
        raise NotImplementedError


class Ur9yMnTm4NSzvG9rrwjM2ec8xZgh1cafXH8(NotificationDispatcher):
    def dispatch(self, message: str) -> None:
        self._channel.send(f"URGENTE: {message}")


class RoutineNotificationDispatcher(NotificationDispatcher):
    def dispatch(self, message: str) -> None:
        self._channel.send(f"Registro de auditoría: {message}")


_CANAL_TO_CHANNEL = {"iot-monitor": "mqtt", "logistics-audit": "webhook"}
_CANAL_TO_DISPATCHER = {
    "iot-monitor": Ur9yMnTm4NSzvG9rrwjM2ec8xZgh1cafXH8,
    "logistics-audit": RoutineNotificationDispatcher,
}


def resolve_channel_name(canal: str) -> str:
    return _CANAL_TO_CHANNEL.get(canal, "webhook")


def build_dispatcher(canal: str, channel: NotificationChannel) -> NotificationDispatcher:
    dispatcher_cls = _CANAL_TO_DISPATCHER.get(canal, RoutineNotificationDispatcher)
    return dispatcher_cls(channel)