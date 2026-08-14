from typing import Optional
from sqlmodel import SQLModel, Field

class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None)

# Modelo principal para la Base de Datos
class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    ai_sentiment_analysis: Optional[str] = Field(default=None)

# Schema Público para Lectura
class ReviewPublic(ReviewBase):
    id: int
    user_id: int
    product_id: int
    ai_sentiment_analysis: Optional[str] = None

# Schema para Crear (No incluye user_id ni product_id en el payload del JSON)
class ReviewCreate(ReviewBase):
    pass

# Schema para Actualizar (PATCH, campos opcionales)
class ReviewUpdate(SQLModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None