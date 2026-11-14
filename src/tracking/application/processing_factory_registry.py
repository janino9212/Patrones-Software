import logging

from src.tracking.domain.processing_ports import TrackingEventProcessingFactory
from src.tracking.infrastructure.factories.sensor_processing_factory import SensorProcessingFactory
from src.tracking.infrastructure.factories.stage_change_processing_factory import StageChangeProcessingFactory

logger = logging.getLogger("scm.tracking.abstract_factory")


class TrackingProcessingFactoryRegistry:
    """Selecciona la Abstract Factory de procesamiento según el tipo de evento."""

    _factories: dict[str, TrackingEventProcessingFactory] = {
        "sensor": SensorProcessingFactory(),
        "stage_change": StageChangeProcessingFactory(),
    }

    @classmethod
    def get_factory(cls, event_type: str) -> TrackingEventProcessingFactory:
        factory = cls._factories.get(event_type)
        if factory is None:
            raise ValueError(f"No existe fábrica de procesamiento para: '{event_type}'")
        logger.info(
            "[ABSTRACT FACTORY] Familia de procesamiento para %r: %s",
            event_type, factory.__class__.__name__,
        )
        return factory