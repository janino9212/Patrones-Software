from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.forecasting.domain.forecast_plan import DemandRecord, ForecastPlan
from src.forecasting.infrastructure.models import DemandRecordModel, ForecastPlanModel
from src.shared.datetime_utils import ensure_utc


class SqlDemandHistoryRepository:
    """Adaptador SQLAlchemy del puerto DemandHistoryRepository."""

    def __init__(self, db: Session):
        self._db = db

    def upsert(self, record: DemandRecord) -> DemandRecord:
        """Un producto tiene una sola cifra por período: si ya existe, se corrige."""
        model = (
            self._db.query(DemandRecordModel)
            .filter(
                DemandRecordModel.product_id == record.product_id,
                DemandRecordModel.period == record.period,
            )
            .first()
        )
        if model is None:
            model = DemandRecordModel(product_id=record.product_id, period=record.period)
            self._db.add(model)
        model.quantity = record.quantity
        try:
            self._db.commit()
        except IntegrityError:
            # Otra petición insertó el mismo producto y período entre la
            # consulta y el commit: se corrige esa fila en lugar de fallar.
            self._db.rollback()
            self._db.query(DemandRecordModel).filter(
                DemandRecordModel.product_id == record.product_id,
                DemandRecordModel.period == record.period,
            ).update({DemandRecordModel.quantity: record.quantity})
            self._db.commit()
        return record

    def list_by_product(self, product_id: str) -> list[DemandRecord]:
        rows = (
            self._db.query(DemandRecordModel)
            .filter(DemandRecordModel.product_id == product_id)
            .order_by(DemandRecordModel.period)
            .all()
        )
        return [
            DemandRecord(product_id=row.product_id, period=row.period, quantity=row.quantity)
            for row in rows
        ]


class SqlForecastPlanRepository:
    """Adaptador SQLAlchemy del puerto ForecastPlanRepository."""

    def __init__(self, db: Session):
        self._db = db

    def get(self, product_id: str) -> ForecastPlan | None:
        model = self._db.get(ForecastPlanModel, product_id)
        if model is None:
            return None
        return ForecastPlan(
            product_id=model.product_id,
            model=model.model,
            predicted_demand=model.predicted_demand,
            based_on_records=model.based_on_records,
            generated_at=ensure_utc(model.generated_at),
        )

    def save(self, plan: ForecastPlan) -> ForecastPlan:
        self._db.merge(
            ForecastPlanModel(
                product_id=plan.product_id,
                model=plan.model,
                predicted_demand=plan.predicted_demand,
                based_on_records=plan.based_on_records,
                generated_at=plan.generated_at,
            )
        )
        self._db.commit()
        return plan

    def delete(self, product_id: str) -> None:
        self._db.query(ForecastPlanModel).filter(
            ForecastPlanModel.product_id == product_id
        ).delete()
        self._db.commit()
