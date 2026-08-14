from typing import Optional
from sqlmodel import SQLModel, Field

class CartItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1, ge=1)

# Modelo principal para la Base de Datos
class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")

# Schema Público para Lectura
class CartItemPublic(CartItemBase):
    id: int
    user_id: int

# Schema para Crear
class CartItemCreate(CartItemBase):
    pass

# Schema para Actualizar (PATCH, campos opcionales)
class CartItemUpdate(SQLModel):
    quantity: Optional[int] = Field(default=None, ge=1)
