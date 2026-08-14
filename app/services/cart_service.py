from sqlmodel import Session, select
from app.models.cart_item import CartItem, CartItemCreate, CartItemUpdate
from app.models.product import Product

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica de negocio y BD.
# Jamás sabe qué es una "Request" o "FastAPI". Separación absoluta.

def add_to_cart(session: Session, item_in: CartItemCreate, user_id: int) -> CartItem | None:
    # Verificar que el producto exista en la base de datos
    product = session.get(Product, item_in.product_id)
    if not product:
        return None

    # Verificar si el producto ya está en el carrito del usuario
    statement = select(CartItem).where(
        CartItem.user_id == user_id,
        CartItem.product_id == item_in.product_id
    )
    existing_item = session.exec(statement).first()

    if existing_item:
        existing_item.quantity += item_in.quantity
        session.add(existing_item)
        session.commit()
        session.refresh(existing_item)
        return existing_item

    # Si no existe en el carrito, crear un nuevo registro inyectando user_id por separado
    cart_item_db = CartItem.model_validate(item_in, update={"user_id": user_id})
    session.add(cart_item_db)
    session.commit()
    session.refresh(cart_item_db)
    return cart_item_db

def get_user_cart(session: Session, user_id: int) -> list[CartItem]:
    statement = select(CartItem).where(CartItem.user_id == user_id)
    return list(session.exec(statement).all())

def get_cart_item_by_id(session: Session, item_id: int, user_id: int) -> CartItem | None:
    statement = select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    return session.exec(statement).first()

def update_cart_item(session: Session, item_id: int, item_in: CartItemUpdate, user_id: int) -> CartItem | None:
    cart_item_db = get_cart_item_by_id(session, item_id=item_id, user_id=user_id)
    if not cart_item_db:
        return None

    update_data = item_in.model_dump(exclude_unset=True)
    cart_item_db.sqlmodel_update(update_data)

    session.add(cart_item_db)
    session.commit()
    session.refresh(cart_item_db)
    return cart_item_db

def remove_from_cart(session: Session, item_id: int, user_id: int) -> bool:
    cart_item_db = get_cart_item_by_id(session, item_id=item_id, user_id=user_id)
    if not cart_item_db:
        return False

    session.delete(cart_item_db)
    session.commit()
    return True

def clear_cart(session: Session, user_id: int) -> bool:
    items = get_user_cart(session, user_id=user_id)
    for item in items:
        session.delete(item)
    session.commit()
    return True
