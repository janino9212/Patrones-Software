from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.forecasting.application.authorized_forecast_report_proxy import (
    AuthorizedForecastReportProxy,
)
from src.forecasting.application.forecast_commands import (
    ForecastCommand,
    ForecastCommandInvoker,
    ForecastPlanConflict,
    GenerateForecastCommand,
    RecalculateForecastCommand,
    get_command_invoker,
)
from src.forecasting.application.forecast_planner import ForecastPlanner
from src.forecasting.application.generate_forecast_report import GenerateForecastReportUseCase
from src.forecasting.domain.forecast_models import available_models
from src.forecasting.domain.forecast_plan import DemandRecord, ForecastPlan
from src.forecasting.domain.report_service import ForecastAccessDenied, ForecastReportService
from src.forecasting.infrastructure.repository import (
    SqlDemandHistoryRepository,
    SqlForecastPlanRepository,
)
from src.forecasting.interfaces.schemas import (
    CommandLogResponse,
    DemandRecordRequest,
    DemandRecordResponse,
    ForecastCommandRequest,
    ForecastModelResponse,
    ForecastPlanResponse,
    ForecastReportResponse,
    UndoRequest,
    UndoResponse,
)
from src.shared.auth_dependencies import bearer_token, current_user
from src.shared.database import get_db
from src.tracking.infrastructure.repository import SqlTrackingEventRepository

router = APIRouter(prefix="/forecasting", tags=["forecasting"])

# Los reportes se protegen con el Proxy; el resto, con la sesión del router.
_session = APIRouter(dependencies=[Depends(current_user)])

_COMMANDS: dict[str, type[ForecastCommand]] = {
    GenerateForecastCommand.name: GenerateForecastCommand,
    RecalculateForecastCommand.name: RecalculateForecastCommand,
}


def build_forecast_service(db: Session, token: str | None) -> ForecastReportService:
    """Arma el sujeto real y lo envuelve en el Proxy de protección (JWT)."""
    real_service = GenerateForecastReportUseCase(
        SqlTrackingEventRepository(db), SqlForecastPlanRepository(db)
    )
    return AuthorizedForecastReportProxy(real_service, token)


def build_protected_forecast_service(
    db: Session = Depends(get_db),
    token: str | None = Depends(bearer_token),
) -> ForecastReportService:
    return build_forecast_service(db, token)


def _build_planner(db: Session = Depends(get_db)) -> ForecastPlanner:
    return ForecastPlanner(SqlDemandHistoryRepository(db), SqlForecastPlanRepository(db))


@router.get("/reports/{product_id}", response_model=ForecastReportResponse)
def get_forecast_report(
    product_id: str,
    service: ForecastReportService = Depends(build_protected_forecast_service),
):
    try:
        data = service.execute(product_id)
    except ForecastAccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return ForecastReportResponse(**data)


@_session.get("/models", response_model=list[ForecastModelResponse])
def list_models():
    return [
        ForecastModelResponse(name=model.name, label=model.label, min_points=model.min_points)
        for model in available_models()
    ]


@_session.post(
    "/demand", response_model=DemandRecordResponse, status_code=status.HTTP_201_CREATED
)
def record_demand(payload: DemandRecordRequest, db: Session = Depends(get_db)):
    record = SqlDemandHistoryRepository(db).upsert(
        DemandRecord(
            product_id=payload.product_id, period=payload.period, quantity=payload.quantity
        )
    )
    return DemandRecordResponse(
        product_id=record.product_id, period=record.period, quantity=record.quantity
    )


@_session.get("/demand/{product_id}", response_model=list[DemandRecordResponse])
def list_demand(product_id: str, db: Session = Depends(get_db)):
    return [
        DemandRecordResponse(
            product_id=record.product_id, period=record.period, quantity=record.quantity
        )
        for record in SqlDemandHistoryRepository(db).list_by_product(product_id)
    ]


@_session.get("/plans/{product_id}", response_model=ForecastPlanResponse)
def get_plan(
    product_id: str,
    planner: ForecastPlanner = Depends(_build_planner),
    invoker: ForecastCommandInvoker = Depends(get_command_invoker),
):
    plan = planner.current(product_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El producto {product_id} aún no tiene pronóstico",
        )
    return _plan_response(plan, invoker)


@_session.post("/commands", response_model=ForecastPlanResponse)
def run_command(
    payload: ForecastCommandRequest,
    planner: ForecastPlanner = Depends(_build_planner),
    invoker: ForecastCommandInvoker = Depends(get_command_invoker),
):
    command = _COMMANDS[payload.action](payload.product_id, payload.model)
    try:
        plan = invoker.run(command, planner)
    except ForecastPlanConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _plan_response(plan, invoker)


@_session.post("/commands/undo", response_model=UndoResponse)
def undo_last_command(
    payload: UndoRequest,
    planner: ForecastPlanner = Depends(_build_planner),
    invoker: ForecastCommandInvoker = Depends(get_command_invoker),
):
    try:
        plan = invoker.undo_last(payload.product_id, planner)
    except ForecastPlanConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UndoResponse(
        product_id=payload.product_id,
        plan=_plan_response(plan, invoker) if plan is not None else None,
    )


@_session.get("/commands", response_model=list[CommandLogResponse])
def list_command_log(invoker: ForecastCommandInvoker = Depends(get_command_invoker)):
    return [
        CommandLogResponse(
            command=entry.command,
            product_id=entry.product_id,
            executed_at=entry.executed_at,
            undone=entry.undone,
        )
        for entry in invoker.log()
    ]


def _plan_response(plan: ForecastPlan, invoker: ForecastCommandInvoker) -> ForecastPlanResponse:
    return ForecastPlanResponse(
        product_id=plan.product_id,
        model=plan.model,
        predicted_demand=plan.predicted_demand,
        based_on_records=plan.based_on_records,
        generated_at=plan.generated_at,
        can_undo=invoker.can_undo(plan.product_id),
    )


router.include_router(_session)
