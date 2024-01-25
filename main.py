from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uuid  # Добавим библиотеку uuid для генерации уникальных идентификаторов

app = FastAPI()

# Модель для задачи с автоматически генерируемым идентификатором
class Task(BaseModel):
    id: uuid.UUID  # Используем uuid для автоматически генерируемых идентификаторов
    title: str
    description: str
    status: bool

# Хранилище задач с измененным типом идентификатора
tasks_db: Dict[uuid.UUID, Task] = {}

# Класс для данных новой задачи с обновленной моделью
class TaskCreate(BaseModel):
    title: str
    description: str
    status: bool = False

# Получение списка всех задач
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return list(tasks_db.values())

# Получение задачи по идентификатору
@app.get("/tasks/{id}", response_model=Task)
def get_task(id: uuid.UUID):
    task = tasks_db.get(id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

# Добавление новой задачи с использованием uuid
@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    task_id = uuid.uuid4()  # Генерируем уникальный идентификатор для новой задачи
    new_task = Task(id=task_id, title=task.title, description=task.description, status=task.status)
    tasks_db[task_id] = new_task
    return new_task

# Обновление задачи по идентификатору с использованием update_forward_refs()
@app.put("/tasks/{id}", response_model=Task)
def update_task(id: uuid.UUID, task: TaskCreate):
    existing_task = tasks_db.get(id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Обновляем существующую задачу с использованием данных из запроса
    existing_task.title = task.title
    existing_task.description = task.description
    existing_task.status = task.status

    existing_task.update_forward_refs()  # Обновляем ссылки Pydantic

    return existing_task

# Удаление задачи по идентификатору
@app.delete("/tasks/{id}", response_model=Task)
def delete_task(id: uuid.UUID):
    task = tasks_db.pop(id, None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task