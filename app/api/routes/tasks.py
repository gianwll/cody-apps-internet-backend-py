from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.task import Task, TaskCreate, TaskPublic, TaskUpdate, PromptRequest
from app.services import task_service

router = APIRouter()

# Observa que todas las peticiones exigen `current_user: CurrentUser`. 
# Esto hace que nadie anónimo pueda ver ni tocar las tareas. Seguridad de borde por Defecto.

@router.get("/", response_model=list[TaskPublic])
def leer_tareas(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    return task_service.get_tasks(session=session, skip=skip, limit=limit)

@router.post("/", response_model=TaskPublic)
def crear_tarea(session: SessionDep, current_user: CurrentUser, task_in: TaskCreate) -> Any:
    return task_service.create_task(session=session, task_in=task_in)

@router.post("/ai", response_model=TaskPublic)
def crear_tarea_con_ia(session: SessionDep, current_user: CurrentUser, task_in: TaskCreate) -> Any:
    """
    Crea una tarea e inyecta un consejo mágico de productividad usando Google Gemini AI.
    Requiere que la variable GEMINI_API_KEY esté configurada.
    """
    return task_service.create_task_ai(session=session, task_in=task_in)

@router.post("/ai-suggest")
def suggest_task(request: PromptRequest, current_user: CurrentUser) -> Any:
    """
    Recibe un texto en lenguaje natural y Zhipu AI (GLM-4-Flash) extrae el Título y la Descripción estructurados en JSON.
    """
    return task_service.suggest_task_ai(prompt=request.prompt)

@router.patch("/{task_id}", response_model=TaskPublic)
def actualizar_tarea(session: SessionDep, current_user: CurrentUser, task_id: int, task_in: TaskUpdate) -> Any:
    task_db = task_service.update_task(session=session, task_id=task_id, task_in=task_in)
    if not task_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada ❌")
    return task_db

@router.delete("/{task_id}")
def borrar_tarea(session: SessionDep, current_user: CurrentUser, task_id: int) -> dict:
    deleted = task_service.delete_task(session=session, task_id=task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tarea no encontrada ❌")
    return {"mensaje": f"Tarea {task_id} borrada exitosamente de la base de datos"}
