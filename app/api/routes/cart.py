from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, CurrentUser
from app.models.cart_item import CartItemCreate, CartItemPublic, CartItemUpdate
from app.services import cart_service

router = APIRouter()

@router.post("/", response_model=CartItemPublic, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    item_in: CartItemCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Agrega un producto al carrito del usuario autenticado.
    Seguridad: user_id se extrae del Token JWT (current_user.id) para evitar suplantación de identidad.
    """
    cart_item = cart_service.add_to_cart(
        session=session, item_in=item_in, user_id=current_user.id
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return cart_item

@router.get("/", response_model=list[CartItemPublic])
def read_user_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Obtiene todos los elementos del carrito pertenecientes al usuario autenticado.
    """
    return cart_service.get_user_cart(session=session, user_id=current_user.id)

@router.patch("/{item_id}", response_model=CartItemPublic)
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Actualiza la cantidad de un elemento del carrito del usuario.
    """
    cart_item = cart_service.update_cart_item(
        session=session, item_id=item_id, item_in=item_in, user_id=current_user.id
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento del carrito no encontrado",
        )
    return cart_item

@router.delete("/{item_id}")
def remove_cart_item(
    item_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """
    Elimina un producto del carrito del usuario.
    """
    deleted = cart_service.remove_from_cart(
        session=session, item_id=item_id, user_id=current_user.id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Elemento del carrito no encontrado",
        )
    return {"mensaje": f"Elemento {item_id} eliminado del carrito"}

@router.delete("/")
def clear_user_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """
    Vacía por completo el carrito del usuario.
    """
    cart_service.clear_cart(session=session, user_id=current_user.id)
    return {"mensaje": "Carrito vaciado exitosamente"}
