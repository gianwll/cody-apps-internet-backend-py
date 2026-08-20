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

    system_prompt = (
        "Eres un asistente de productividad. El usuario te dará una frase en lenguaje natural sobre algo que tiene que hacer.\n"
        "Tu trabajo es extraer un 'titulo' corto y conciso, y una 'descripcion' más detallada.\n"
        "Debes responder EXCLUSIVAMENTE en formato JSON válido, sin bloques Markdown, con esta estructura exacta:\n"
        '{"title": "string", "description": "string"}'
    )

    zhipu_key = settings.ZHIPU_API_KEY or os.getenv("ZHIPU_API_KEY")
    if zhipu_key:
        client = OpenAI(
            api_key=zhipu_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        for model_name in ["glm-4-flash", "glm-4", "glm-4-air", "glm-4-plus", "chatglm_turbo"]:
            try:
                response = client.chat.completions.create(
                    model=model_name,
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
                    content = content.strip("` \n")
                
                return json.loads(content)
            except Exception as inner_err:
                print(f"Intento Zhipu con {model_name} falló: {inner_err}")
                continue

    # Fallback secundario con Gemini AI si Zhipu no tiene el modelo habilitado
    if settings.GEMINI_API_KEY:
        try:
            gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            full_prompt = f"{system_prompt}\nFrase del usuario: '{prompt}'"
            for model_name in ['gemini-3.6-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']:
                try:
                    res = gemini_client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    if res and res.text:
                        txt = res.text.strip()
                        if txt.startswith("```json"):
                            txt = txt.replace("```json", "").replace("```", "").strip()
                        elif txt.startswith("```"):
                            txt = txt.strip("` \n")
                        return json.loads(txt)
                except Exception:
                    continue
        except Exception as e:
            print(f"Error fallback Gemini: {e}")

    return {
        "title": "Error extrayendo tarea con IA",
        "description": "Por favor revisa la configuración de tu clave de API."
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
