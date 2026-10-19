import logging

from src.iot.domain.notification_channel import NotificationChannel

logger = logging.getLogger("scm.iot.bridge")


class MqttChannel(NotificationChannel):
    def send(self, message: str) -> None:
        logger.info("[BRIDGE][MQTT] %s", message)


class WebhookChannel(NotificationChannel):
    def send(self, message: str) -> None:
        logger.info("[BRIDGE][WEBHOOK] %s", message)
