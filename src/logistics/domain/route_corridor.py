import logging
from typing import Iterator

from src.logistics.domain.route_component import RouteComponent

logger = logging.getLogger("scm.logistics.composite")


class RouteCorridor(RouteComponent):
    def __init__(self, name: str):
        self._name = name
        self._children: list[RouteComponent] = []

    @property
    def children(self) -> tuple[RouteComponent, ...]:
        return tuple(self._children)

    def add(self, component: RouteComponent) -> None:
        self._children.append(component)

    def total_distance_km(self) -> float:
        total = sum(child.total_distance_km() for child in self._children)
        logger.info(
            "[COMPOSITE] Corredor '%s' suma %s km de %d componentes",
            self._name, total, len(self._children),
        )
        return total

    def describe(self) -> str:
        return f"Corredor '{self._name}' ({len(self._children)} componentes)"

    def __iter__(self) -> "RouteLeafIterator":
        return RouteLeafIterator(self)


class RouteLeafIterator(Iterator[RouteComponent]):
    """Iterator (GoF): recorre en profundidad las rutas (hojas) de un
    corredor, sin importar cuántos sub-corredores anidados tenga. El cliente
    itera con un `for` y no necesita conocer la estructura del Composite.

    Mantiene su propia pila, así que dos recorridos del mismo corredor son
    independientes entre sí."""

    def __init__(self, root: RouteCorridor):
        self._pending: list[RouteComponent] = list(reversed(root.children))

    def __iter__(self) -> "RouteLeafIterator":
        return self

    def __next__(self) -> RouteComponent:
        while self._pending:
            component = self._pending.pop()
            if isinstance(component, RouteCorridor):
                self._pending.extend(reversed(component.children))
                continue
            return component
        raise StopIteration
