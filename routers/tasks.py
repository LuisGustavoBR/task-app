from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, db_available, db_error_message
from models import Task, User
from schemas import TaskCreate, TaskUpdate, TaskResponse
from auth import get_current_user_id, decode_token
from typing import Optional, List
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return HTMLResponse(status_code=302, headers={"Location": "/login"})
    payload = decode_token(token)
    if not payload:
        return HTMLResponse(status_code=302, headers={"Location": "/login"})

    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "user_name": payload.get("name", "Usuário"),
        "db_available": db_available,
        "db_error": db_error_message if not db_available else "",
    })


# API

@router.get("/api/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    q = db.query(Task).filter(Task.user_id == user_id)
    if status_filter and status_filter != "all":
        q = q.filter(Task.status == status_filter)
    if priority_filter and priority_filter != "all":
        q = q.filter(Task.priority == priority_filter)
    return q.order_by(Task.created_at.desc()).all()


@router.post("/api/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    payload: TaskCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    due_date = None
    if payload.due_date:
        try:
            due_date = datetime.fromisoformat(payload.due_date)
        except ValueError:
            pass

    task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=payload.status,
        due_date=due_date,
        user_id=user_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.priority is not None:
        task.priority = payload.priority
    if payload.status is not None:
        task.status = payload.status
    if payload.due_date is not None:
        try:
            task.due_date = datetime.fromisoformat(payload.due_date)
        except ValueError:
            task.due_date = None

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.patch("/api/tasks/{task_id}/status")
async def toggle_status(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    cycle = {"pending": "in_progress", "in_progress": "completed", "completed": "pending"}
    task.status = cycle.get(task.status, "pending")
    task.updated_at = datetime.utcnow()
    db.commit()
    return {"status": task.status}


@router.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    db.delete(task)
    db.commit()
