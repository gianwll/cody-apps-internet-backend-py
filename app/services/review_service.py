from sqlmodel import Session, select
from app.models.review import Review, ReviewCreate, ReviewUpdate
from app.models.product import Product

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica de negocio y BD.
# Jamás sabe qué es una "Request" o "FastAPI". Separación absoluta.

def get_reviews(session: Session, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_reviews_by_product(session: Session, product_id: int, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_review_by_id(session: Session, review_id: int) -> Review | None:
    return session.get(Review, review_id)

def create_review(session: Session, review_in: ReviewCreate, user_id: int, product_id: int) -> Review | None:
    # Verificar que el producto exista
    product = session.get(Product, product_id)
    if not product:
        return None

    review_db = Review.model_validate(review_in, update={"user_id": user_id, "product_id": product_id})
    session.add(review_db)
    session.commit()
    session.refresh(review_db)
    return review_db

def update_review(session: Session, review_id: int, review_in: ReviewUpdate) -> Review | None:
    review_db = get_review_by_id(session, review_id)
    if not review_db:
        return None
    
    update_data = review_in.model_dump(exclude_unset=True)
    review_db.sqlmodel_update(update_data)
    
    session.add(review_db)
    session.commit()
    session.refresh(review_db)
    return review_db

def delete_review(session: Session, review_id: int) -> bool:
    review_db = get_review_by_id(session, review_id)
    if not review_db:
        return False
        
    session.delete(review_db)
    session.commit()
    return True
