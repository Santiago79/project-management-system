from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.domain.exceptions import DomainError, NotFoundError, InvalidStatusTransition, ValidationError
from app.repositories.memory import InMemoryProjectRepo, InMemoryTaskRepo
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.schemas.dto import ProjectCreate, ProjectOut, TaskCreate, TaskOut, TaskUpdate

router = APIRouter()

project_repo = InMemoryProjectRepo()
task_repo = InMemoryTaskRepo()

def get_project_service() -> ProjectService:
    return ProjectService(project_repo)

def get_task_service() -> TaskService:
    return TaskService(project_repo, task_repo)

def to_http(e: Exception) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code = 404, details=str(e))
    if isinstance(e, (InvalidStatusTransition, ValidationError, ValueError)):
        return HTTPException(status_code = 400, details=str(e))
    if isinstance(e, DomainError):
        return HTTPException(status_code=500, details='Internal Server Error')

@router.post('/projects', response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    try:
        project = service.create(body.name)
        return ProjectOut(id=project.id, name=project.name)
    except Exception as e:
        raise to_http(e)

@router.get('/projects', response_model=list[ProjectOut])
def list_projects(service: ProjectService = Depends(get_project_service)):
    try:
        projects = service.list()
        return [ProjectOut(id=p.id, name=p.name) for p in projects]
    except Exception as e:
        raise to_http(e)

@router.get('/projects/{project_id}', response_model=ProjectOut)
def get_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    try:
        project = service.get(project_id)
        return ProjectOut(id=project.id, name=project.name)
    except Exception as e:
        raise to_http(e)


@router.post('/projects/{project_id}/tasks', response_model=TaskOut, status_code=201)
def create_task(project_id: str, body: TaskCreate, service: TaskService = Depends(get_task_service)):
    try:
        task = service.create_task(
            project_id=project_id,
            title=body.title,
            task_type=body.task_type,
            due_date=body.due_date
        )
        return task
    except Exception as e:
        raise to_http(e)

@router.get('/projects/{project_id}/tasks', response_model=list[TaskOut])
def list_project_tasks(project_id: str, service: TaskService = Depends(get_task_service)):
    try:
        return service.list_tasks(project_id)
    except Exception as e:
        raise to_http(e)

@router.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    try:
        service.delete_task(task_id)
        return None
    except Exception as e:
        raise to_http(e)

@router.patch('/tasks/{task_id}', response_model=TaskOut)
def update_task(task_id: str, body: TaskUpdate, service: TaskService = Depends(get_task_service)):
    try:
        return service.update_task(
            task_id=task_id,
            title=body.title,
            due_date=body.due_date,
            status=body.status
        )
    except Exception as e:
        raise to_http(e)