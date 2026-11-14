from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class Product:
    """Producto del catálogo. `code` es el `product_id` que usan tracking,
    forecasting e iot."""

    code: str
    name: str
    category: str | None
    created_at: datetime


class ProductAlreadyExists(ValueError):
    """Ya hay un producto con ese código."""


class ProductRepository(Protocol):
    """Puerto: catálogo de productos."""

    def add(self, product: Product) -> Product: ...

    def get(self, code: str) -> Product | None: ...

    def list_all(self) -> list[Product]: ...
