from src.tracking.domain.processing_ports import TrackingEventProcessingFactory
from src.tracking.infrastructure.factories.sensor_processing_factory import SensorProcessingFactory
from src.tracking.infrastructure.factories.stage_change_processing_factory import StageChangeProcessingFactory


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
        print(f"[ABSTRACT FACTORY] Familia de procesamiento seleccionada para '{event_type}': "
              f"{factory.__class__.__name__}")
        return factory