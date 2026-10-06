from fastapi import APIRouter

from src.api.v1.schemas.task import TaskStatus
from src.celery_app import celery_app


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskStatus, status_code=200)
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    status, result = task.status, task.result
    if isinstance(result, BaseException):
        result = {"error": type(result).__name__}
    return {
        "task_id": task_id,
        "status": status,
        "result": result
    }