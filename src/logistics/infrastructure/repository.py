import dataclasses

from sqlalchemy.orm import Session

from src.logistics.domain.entities import DistributionRoute, RouteStop
from src.logistics.infrastructure.models import DistributionRouteModel


class SqlDistributionRouteRepository:
    """Adaptador (hexagonal) que implementa DistributionRouteRepository con
    SQLAlchemy. Recibe la sesión ya creada por get_db() (src.shared.database),
    que a su vez viene del engine único de DatabaseConnection (Singleton) --
    no crea ninguna conexión propia."""

    def __init__(self, db: Session):
        self._db = db

    def save(self, route: DistributionRoute) -> DistributionRoute:
        model = DistributionRouteModel(
            vehicle_type=route.vehicle_type,
            departure_date=route.departure_date,
            stops=[dataclasses.asdict(stop) for stop in route.stops],
            total_distance_km=route.total_distance_km,
            notes=route.notes,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def get(self, route_id: int) -> DistributionRoute | None:
        model = self._db.get(DistributionRouteModel, route_id)
        return self._to_domain(model) if model is not None else None

    def list_all(self) -> list[DistributionRoute]:
        models = (
            self._db.query(DistributionRouteModel)
            .order_by(DistributionRouteModel.id)
            .all()
        )
        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_domain(model: DistributionRouteModel) -> DistributionRoute:
        stops = tuple(RouteStop(**stop) for stop in model.stops)
        return DistributionRoute(
            route_id=model.id,
            vehicle_type=model.vehicle_type,
            departure_date=model.departure_date,
            stops=stops,
            total_distance_km=model.total_distance_km,
            notes=model.notes,
        )
