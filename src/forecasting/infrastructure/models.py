from sqlalchemy import Column, Date, DateTime, Float, Integer, String, UniqueConstraint

from src.shared.models import Base


class DemandRecordModel(Base):
    """Tabla demand_records: demanda real por producto y período."""

    __tablename__ = "demand_records"
    __table_args__ = (UniqueConstraint("product_id", "period", name="uq_demand_product_period"),)

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), nullable=False, index=True)
    period = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)


class ForecastPlanModel(Base):
    """Tabla forecast_plans: un pronóstico vigente por producto."""

    __tablename__ = "forecast_plans"

    product_id = Column(String(100), primary_key=True)
    model = Column(String(40), nullable=False)
    predicted_demand = Column(Float, nullable=False)
    based_on_records = Column(Integer, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False)
