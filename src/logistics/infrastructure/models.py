from sqlalchemy import JSON, Column, Date, Float, Integer, String

from src.shared.models import Base


class DistributionRouteModel(Base):
    """Tabla distribution_routes. Usa el mismo Base declarativo de
    src.shared, así se crea junto con las demás tablas en el startup de la
    app. Las paradas se guardan como JSON (lista de dicts) -- son parte del
    mismo agregado y no necesitan su propia tabla para este alcance."""

    __tablename__ = "distribution_routes"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(50), nullable=False)
    departure_date = Column(Date, nullable=False)
    stops = Column(JSON, nullable=False)
    total_distance_km = Column(Float, nullable=True)
    notes = Column(String(255), nullable=True)
