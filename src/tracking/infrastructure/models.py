from sqlalchemy import Column, DateTime, Float, Integer, String

from src.shared.models import Base


class TrackingEventModel(Base):
    """Tabla tracking_events. Usa el mismo Base declarativo de src.shared,
    así se crea junto con las demás tablas en el startup de la app (una
    sola llamada a Base.metadata.create_all, sin duplicar lógica)."""

    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(30), nullable=False, index=True)
    product_id = Column(String(100), nullable=False, index=True)
    stage = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Específicos de SensorTrackingEvent (nulos si event_type == stage_change)
    sensor_type = Column(String(50), nullable=True)
    reading_value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)

    # Específicos de StageChangeTrackingEvent (nulos si event_type == sensor)
    previous_stage = Column(String(50), nullable=True)
    responsible = Column(String(100), nullable=True)
