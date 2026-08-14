from sqlmodel import Session, select
from app.models.review import Review, ReviewCreate, ReviewUpdate
from app.models.product import Product
from app.core.config import settings
from google import genai

def get_reviews(session: Session, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_reviews_by_product(session: Session, product_id: int, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_review_by_id(session: Session, review_id: int) -> Review | None:
    return session.get(Review, review_id)

def create_review_ai(session: Session, review_in: ReviewCreate, user_id: int, product_id: int) -> Review | None:
    product = session.get(Product, product_id)
    if not product:
        return None

    review_db = Review.model_validate(review_in, update={"user_id": user_id, "product_id": product_id})

    # --- 🤖 EFECTO WOW: ANÁLISIS DE EMOCIONES E INTELIGENCIA ARTIFICIAL ---
    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = (
                f"Eres un experto gestor y analizador de emociones de clientes sobre productos. "
                f"Analiza la reseña enviada por el usuario para el producto '{product.title}'. "
                f"Producto: '{product.title}'. "
                f"Comentario del cliente: '{review_db.comment or 'Sin comentario'}' (Calificación: {review_db.rating}/5 estrellas). "
                f"En un máximo de 2 oraciones cortas, identifica la emoción predominante del cliente (ej. alegría, frustración, entusiasmo, decepción) "
                f"y brinda un análisis empático relacionando la reseña con el producto."
            )
            
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            review_db.ai_sentiment_analysis = response.text.strip()
        except Exception as e:
            print(f"Error generando análisis de emociones IA: {e}")
            pass
    # -------------------------------------------------------------------

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