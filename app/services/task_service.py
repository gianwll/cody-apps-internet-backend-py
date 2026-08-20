from sqlmodel import Session, select
from app.models.task import Task, TaskCreate, TaskUpdate
from app.core.config import settings
from google import genai

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica.
# Jamás sabe qué es una "Request" o "FastAPI". Separación absoluta.

def get_tasks(session: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    statement = select(Task).offset(skip).limit(limit)
    return session.exec(statement).all()

def get_task_by_id(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)

def create_task(session: Session, task_in: TaskCreate) -> Task:
    task_db = Task.model_validate(task_in)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

def create_task_ai(session: Session, task_in: TaskCreate) -> Task:
    task_db = Task.model_validate(task_in)
    
    # --- 🤖 EFECTO WOW: SUGERENCIA DE INTELIGENCIA ARTIFICIAL ---
    if not settings.GEMINI_API_KEY:
        task_db.ai_suggestion = "Configura una GEMINI_API_KEY válida de https://aistudio.google.com/ en tu archivo .env"
    else:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"Eres un asistente de productividad amable, profesional y muy ordenado. El usuario tiene esta tarea: '{task_db.title}'. Descripción: '{task_db.description or 'Sin descripción'}'. Dale un consejo práctico, claro y motivador para cumplirla con éxito, en un máximo de 2 oraciones cortas."
            
            for model_name in ['gemini-3.6-flash', 'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.0-flash']:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        task_db.ai_suggestion = response.text.strip()
                        break
                except Exception as inner_err:
                    print(f"Intento con {model_name} falló: {inner_err}")
                    continue
        except Exception as e:
            print(f"Error generando sugerencia IA: {e}")
            task_db.ai_suggestion = f"Error al conectar con Gemini AI: {e}"
    # ------------------------------------------------------------
    
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

def suggest_task_ai(prompt: str) -> dict:
    import json
    import os
    from openai import OpenAI

    api_key = settings.ZHIPU_API_KEY or os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return {
            "title": "Configurar ZHIPU_API_KEY",
            "description": "Por favor añade ZHIPU_API_KEY a tu archivo .env"
        }
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )
    
    system_prompt = """
    Eres un asistente de productividad. El usuario te dará una frase en lenguaje natural sobre algo que tiene que hacer.
    Tu trabajo es extraer un 'titulo' corto y conciso, y una 'descripcion' más detallada.
    Debes responder EXCLUSIVAMENTE en formato JSON válido, sin Markdown, con esta estructura exacta:
    {"title": "string", "description": "string"}
    """
    
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        return json.loads(content)
    except Exception as e:
        print(f"Error en suggest_task_ai: {e}")
        return {
            "title": "Error extrayendo tarea con Zhipu AI",
            "description": str(e)
        }

def update_task(session: Session, task_id: int, task_in: TaskUpdate) -> Task | None:
    task_db = get_task_by_id(session, task_id)
    if not task_db:
        return None
    
    # Ignora valores "Nulos" que vengan del Frontend (Parcheo Parcial) 
    update_data = task_in.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(update_data)
    
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

def delete_task(session: Session, task_id: int) -> bool:
    task_db = get_task_by_id(session, task_id)
    if not task_db:
        return False
        
    session.delete(task_db)
    session.commit()
    return True
