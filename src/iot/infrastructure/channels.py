from src.iot.domain.notification_channel import NotificationChannel


class MqttChannel(NotificationChannel):
    def send(self, message: str) -> None:
        print(f"[BRIDGE][MQTT] {message}")


class WebhookChannel(NotificationChannel):
    def send(self, message: str) -> None:
        print(f"[BRIDGE][WEBHOOK] {message}")