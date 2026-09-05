from sqlalchemy.orm import Session

from src.tracking.domain.entities import (
    SensorTrackingEvent,
    StageChangeTrackingEvent,
    TrackingEvent,
    event_type_of,
)
from src.tracking.infrastructure.models import TrackingEventModel


class SqlTrackingEventRepository:
    """Adaptador (hexagonal) que implementa TrackingEventRepository con
    SQLAlchemy. Recibe la sesión ya creada por get_db() (src.shared.database),
    que a su vez viene del engine único de DatabaseConnection (Singleton) --
    no crea ninguna conexión propia."""

    def __init__(self, db: Session):
        self._db = db

    def save(self, event: TrackingEvent) -> TrackingEvent:
        model = TrackingEventModel(
            event_type=event_type_of(event),
            product_id=event.product_id,
            stage=event.stage,
            timestamp=event.timestamp,
            sensor_type=getattr(event, "sensor_type", None),
            reading_value=getattr(event, "reading_value", None),
            unit=getattr(event, "unit", None),
            previous_stage=getattr(event, "previous_stage", None),
            responsible=getattr(event, "responsible", None),
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return event

    def list_by_product(self, product_id: str) -> list[TrackingEvent]:
        rows = (
            self._db.query(TrackingEventModel)
            .filter(TrackingEventModel.product_id == product_id)
            .order_by(TrackingEventModel.timestamp)
            .all()
        )
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: TrackingEventModel) -> TrackingEvent:
        if row.event_type == "sensor":
            return SensorTrackingEvent(
                product_id=row.product_id,
                stage=row.stage,
                timestamp=row.timestamp,
                sensor_type=row.sensor_type,
                reading_value=row.reading_value,
                unit=row.unit,
            )
        if row.event_type == "stage_change":
            return StageChangeTrackingEvent(
                product_id=row.product_id,
                stage=row.stage,
                timestamp=row.timestamp,
                previous_stage=row.previous_stage,
                responsible=row.responsible,
            )
        raise TypeError(f"event_type desconocido en BD: {row.event_type!r}")
