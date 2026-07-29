from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field

from service import task_service


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    completed: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(data: TaskCreate):
    return task_service.create(data.model_dump())


@router.get("", response_model=list[TaskResponse])
def get_tasks():
    return task_service.get_all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = task_service.get(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate):
    task = task_service.update(
        task_id,
        data.model_dump(exclude_unset=True),
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(task_id: int):
    deleted = task_service.delete(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return Response(status_code=204)