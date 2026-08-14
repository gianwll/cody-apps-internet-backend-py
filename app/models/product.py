from typing import Optional
from sqlmodel import SQLModel, Field

class ProductBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

# Modelo principal para la Base de Datos
class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# Schema Público para Lectura
class ProductPublic(ProductBase):
    id: int

# Schema para Crear
class ProductCreate(ProductBase):
    pass

# Schema para Actualizar (PATCH, campos opcionales)
class ProductUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
