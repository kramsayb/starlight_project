from pydantic import BaseModel


class TaskAccepted(BaseModel):
    task_id: str
    status: str
    message: str