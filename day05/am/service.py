class TaskService:
    def __init__(self):
        self.tasks: dict[int, dict] = {}
        self.next_id = 1

    def create(self, data: dict) -> dict:
        task = {
            "id": self.next_id,
            "title": data["title"],
            "completed": False,
        }

        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def get_all(self) -> list[dict]:
        return list(self.tasks.values())

    def get(self, task_id: int) -> dict | None:
        return self.tasks.get(task_id)

    def update(self, task_id: int, data: dict) -> dict | None:
        task = self.tasks.get(task_id)

        if task is None:
            return None

        task.update(data)
        return task

    def delete(self, task_id: int) -> bool:
        if task_id not in self.tasks:
            return False

        del self.tasks[task_id]
        return True


task_service = TaskService()