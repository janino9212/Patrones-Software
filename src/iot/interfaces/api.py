from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.iot.application.ingest_sensor_reading import IngestSensorReadingUseCase
from src.iot.interfaces.schemas import IngestSensorRequest, IngestSensorResponse
from src.shared.database import get_db
from src.tracking.application.register_event import RegisterTrackingEventUseCase
from src.tracking.infrastructure.repository import SqlTrackingEventRepository

router = APIRouter(prefix="/iot", tags=["iot"])


def _build_use_case(db: Session = Depends(get_db)) -> IngestSensorReadingUseCase:
    repository = SqlTrackingEventRepository(db)
    register_use_case = RegisterTrackingEventUseCase(repository)
    return IngestSensorReadingUseCase(register_use_case)


@router.post("/sensors/{vendor}/ingest", response_model=IngestSensorResponse, status_code=status.HTTP_201_CREATED)
def ingest_sensor_reading(
    vendor: str,
    payload: IngestSensorRequest,
    use_case: IngestSensorReadingUseCase = Depends(_build_use_case),
):
    try:
        result = use_case.execute(vendor, payload.product_id, payload.stage)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return IngestSensorResponse(
        product_id=result.event.product_id,
        sensor_type=result.event.sensor_type,
        reading_value=result.event.reading_value,
        unit=result.event.unit,
        notified_via=result.notified_via,
        message=result.message,
    )