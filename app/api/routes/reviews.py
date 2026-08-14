from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, CurrentUser
from app.models.review import ReviewCreate, ReviewPublic
from app.services import review_service

router = APIRouter()

@router.post("/{product_id}/reviews", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
def create_review_for_product(
    product_id: int,
    review_in: ReviewCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Crea una reseña para un producto específico.
    Seguridad: user_id se extrae del token JWT (current_user.id) para evitar suplantación de identidad.
    """
    review = review_service.create_review(
        session=session,
        review_in=review_in,
        user_id=current_user.id,
        product_id=product_id,
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return review

@router.get("/{product_id}/reviews", response_model=list[ReviewPublic])
def read_reviews_for_product(
    product_id: int,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return review_service.get_reviews_by_product(
        session=session, product_id=product_id, skip=skip, limit=limit
    )
