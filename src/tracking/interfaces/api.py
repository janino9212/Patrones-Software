import dataclasses

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.shared.database import get_db
from src.tracking.application.register_event import RegisterTrackingEventUseCase
from src.tracking.domain.entities import TrackingEvent, event_type_of
from src.tracking.domain.event_factory import UnsupportedEventTypeError
from src.tracking.infrastructure.repository import SqlTrackingEventRepository
from src.tracking.interfaces.schemas import TrackingEventRequest, TrackingEventResponse

router = APIRouter(prefix="/tracking", tags=["tracking"])


def _build_use_case(db: Session = Depends(get_db)) -> RegisterTrackingEventUseCase:
    repository = SqlTrackingEventRepository(db)
    return RegisterTrackingEventUseCase(repository)


@router.post(
    "/events",
    response_model=TrackingEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_event(
    payload: TrackingEventRequest,
    use_case: RegisterTrackingEventUseCase = Depends(_build_use_case),
):
    raw_data = payload.model_dump(exclude={"event_type"}, exclude_none=True)
    try:
        event = use_case.execute(payload.event_type, raw_data)
    except UnsupportedEventTypeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Falta el campo requerido: {exc}",
        ) from exc

    return _to_response(event)


@router.get("/events/{product_id}", response_model=list[TrackingEventResponse])
def list_events(product_id: str, db: Session = Depends(get_db)):
    repository = SqlTrackingEventRepository(db)
    events = repository.list_by_product(product_id)
    return [_to_response(event) for event in events]


def _to_response(event: TrackingEvent) -> TrackingEventResponse:
    data = dataclasses.asdict(event)
    product_id = data.pop("product_id")
    stage = data.pop("stage")
    timestamp = data.pop("timestamp")
    return TrackingEventResponse(
        event_type=event_type_of(event),
        product_id=product_id,
        stage=stage,
        timestamp=timestamp,
        details=data,
    )
