import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


class MissingFieldError(KeyError):
    """Falta un campo obligatorio para el tipo de evento. Hereda de KeyError
    porque así lo reportaba el Creator antes de existir la cadena."""


@dataclass(frozen=True)
class EventValidationRequest:
    """Lo que viaja por la cadena: el tipo de evento y sus datos crudos."""

    event_type: str
    raw_data: Mapping[str, Any]


class EventValidationHandler(ABC):
    """Handler del patrón Chain of Responsibility (GoF).

    Cada eslabón revisa UNA regla sobre los datos crudos del evento. Si la
    regla falla, corta la cadena lanzando un error; si pasa, entrega la
    solicitud al siguiente eslabón. Quien arma la cadena decide el orden y
    qué eslabones participan, sin que los handlers se conozcan entre sí."""

    def __init__(self) -> None:
        self._next: EventValidationHandler | None = None

    def set_next(self, handler: "EventValidationHandler") -> "EventValidationHandler":
        """Enlaza el siguiente eslabón y lo devuelve, para encadenar llamadas."""
        self._next = handler
        return handler

    def handle(self, request: EventValidationRequest) -> None:
        self._check(request)
        if self._next is not None:
            self._next.handle(request)

    @abstractmethod
    def _check(self, request: EventValidationRequest) -> None:
        """Lanza ValueError o MissingFieldError si la regla no se cumple."""


_COMMON_FIELDS = ("product_id", "stage")
_FIELDS_BY_EVENT_TYPE: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "sensor": ("sensor_type", "reading_value", "unit"),
        "stage_change": ("previous_stage", "responsible"),
    }
)
_MAX_PRODUCT_ID_LENGTH = 100


class RequiredFieldsHandler(EventValidationHandler):
    """Están todos los campos que el tipo de evento necesita."""

    def _check(self, request: EventValidationRequest) -> None:
        required = _COMMON_FIELDS + _FIELDS_BY_EVENT_TYPE.get(request.event_type, ())
        for field in required:
            if request.raw_data.get(field) is None:
                raise MissingFieldError(field)


class NonBlankTextHandler(EventValidationHandler):
    """Los campos de texto no llegan vacíos ni solo con espacios."""

    def _check(self, request: EventValidationRequest) -> None:
        for field, value in request.raw_data.items():
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"El campo '{field}' no puede estar vacío")


class ProductIdentifierHandler(EventValidationHandler):
    """El identificador del producto cabe en la columna y no trae espacios."""

    def _check(self, request: EventValidationRequest) -> None:
        product_id = str(request.raw_data["product_id"])
        if len(product_id) > _MAX_PRODUCT_ID_LENGTH:
            raise ValueError(
                f"El product_id supera los {_MAX_PRODUCT_ID_LENGTH} caracteres permitidos"
            )
        if any(char.isspace() for char in product_id):
            raise ValueError("El product_id no puede contener espacios")


class FiniteReadingHandler(EventValidationHandler):
    """Una lectura de sensor debe ser un número finito (ni NaN ni infinito)."""

    def _check(self, request: EventValidationRequest) -> None:
        if request.event_type != "sensor":
            return
        value = request.raw_data["reading_value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("La lectura del sensor debe ser numérica")
        if not math.isfinite(value):
            raise ValueError("La lectura del sensor debe ser un número finito")


def build_default_validation_chain() -> EventValidationHandler:
    """Arma la cadena estándar y devuelve su primer eslabón."""
    head = RequiredFieldsHandler()
    head.set_next(NonBlankTextHandler()).set_next(ProductIdentifierHandler()).set_next(
        FiniteReadingHandler()
    )
    return head
