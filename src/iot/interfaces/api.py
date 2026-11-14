import dataclasses

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.iot.application.ingest_sensor_reading import IngestSensorReadingUseCase
from src.iot.application.monitoring import SensorMonitor, get_sensor_monitor
from src.iot.infrastructure.sensor_adapters import supported_vendors
from src.iot.interfaces.schemas import (
    AlertResponse,
    DeviceResponse,
    IngestSensorRequest,
    IngestSensorResponse,
    ReadingResponse,
    VendorResponse,
)
from src.shared.database import get_db
from src.tracking.application.register_event import RegisterTrackingEventUseCase
from src.tracking.infrastructure.repository import SqlTrackingEventRepository

router = APIRouter(prefix="/iot", tags=["iot"])


def _build_use_case(
    db: Session = Depends(get_db),
    monitor: SensorMonitor = Depends(get_sensor_monitor),
) -> IngestSensorReadingUseCase:
    repository = SqlTrackingEventRepository(db)
    register_use_case = RegisterTrackingEventUseCase(repository)
    return IngestSensorReadingUseCase(register_use_case, monitor.subject)


@router.post(
    "/sensors/{vendor}/ingest",
    response_model=IngestSensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_sensor_reading(
    vendor: str,
    payload: IngestSensorRequest,
    use_case: IngestSensorReadingUseCase = Depends(_build_use_case),
):
    try:
        result = use_case.execute(
            vendor, payload.product_id, payload.stage, payload.simulated_value
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return IngestSensorResponse(
        product_id=result.event.product_id,
        sensor_type=result.event.sensor_type,
        reading_value=result.event.reading_value,
        unit=result.event.unit,
        notified_via=result.notified_via,
        message=result.message,
        device_id=result.device_id,
    )


@router.get("/vendors", response_model=list[VendorResponse])
def list_vendors():
    return [VendorResponse(**dataclasses.asdict(vendor)) for vendor in supported_vendors()]


@router.get("/readings/recent", response_model=list[ReadingResponse])
def list_recent_readings(monitor: SensorMonitor = Depends(get_sensor_monitor)):
    return [
        ReadingResponse(
            device_id=observation.reading.device_id,
            sensor_type=observation.reading.sensor_type,
            value=observation.reading.value,
            unit=observation.reading.unit,
            product_id=observation.product_id,
            stage=observation.stage,
            received_at=observation.received_at,
        )
        for observation in monitor.live_feed.recent()
    ]


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(monitor: SensorMonitor = Depends(get_sensor_monitor)):
    return [AlertResponse(**dataclasses.asdict(alert)) for alert in monitor.alerts.alerts()]


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices(monitor: SensorMonitor = Depends(get_sensor_monitor)):
    return [DeviceResponse(**dataclasses.asdict(device)) for device in monitor.devices.devices()]
