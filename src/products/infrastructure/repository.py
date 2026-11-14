from sqlalchemy import Column, DateTime, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.products.domain.product import Product, ProductAlreadyExists
from src.shared.datetime_utils import ensure_utc
from src.shared.models import Base


class ProductModel(Base):
    """Tabla products: catálogo de productos."""

    __tablename__ = "products"

    code = Column(String(100), primary_key=True)
    name = Column(String(120), nullable=False)
    category = Column(String(60), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)


class SqlProductRepository:
    """Adaptador SQLAlchemy del puerto ProductRepository."""

    def __init__(self, db: Session):
        self._db = db

    def add(self, product: Product) -> Product:
        if self._db.get(ProductModel, product.code) is not None:
            raise ProductAlreadyExists(f"Ya existe un producto con el código {product.code}")
        self._db.add(
            ProductModel(
                code=product.code,
                name=product.name,
                category=product.category,
                created_at=product.created_at,
            )
        )
        try:
            self._db.commit()
        except IntegrityError as exc:
            # Otra petición creó el mismo código entre la consulta y el commit.
            self._db.rollback()
            raise ProductAlreadyExists(
                f"Ya existe un producto con el código {product.code}"
            ) from exc
        return product

    def get(self, code: str) -> Product | None:
        model = self._db.get(ProductModel, code)
        return self._to_domain(model) if model is not None else None

    def list_all(self) -> list[Product]:
        models = self._db.query(ProductModel).order_by(ProductModel.code).all()
        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_domain(model: ProductModel) -> Product:
        return Product(
            code=model.code,
            name=model.name,
            category=model.category,
            created_at=ensure_utc(model.created_at),
        )
