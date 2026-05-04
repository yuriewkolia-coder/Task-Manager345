import json
import os
from datetime import datetime
from enum import Enum
from collections import deque
from typing import List, Optional, Dict, Any


class Priority(Enum):
    """Приоритет задачи"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    @classmethod
    def from_string(cls, value: str):
        """Преобразование строки в enum"""
        for priority in cls:
            if priority.value.lower() == value.lower():
                return priority
        raise ValueError(f"Invalid priority: {value}")


class Status(Enum):
    """Статус задачи"""
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

    @classmethod
    def from_string(cls, value: str):
        """Преобразование строки в enum"""
        for status in cls:
            if status.value.lower() == value.lower():
                return status
        raise ValueError(f"Invalid status: {value}")


class Task:
    """Класс задачи"""

    def __init__(self, task_id: int, title: str, description: str,
                 priority: Priority, status: Status = Status.TODO):
        self._id = task_id
        self._title = title
        self._description = description
        self._priority = priority
        self._status = status
        self._created_at = datetime.now()
        self._updated_at = datetime.now()

    # Геттеры и сеттеры (инкапсуляция)
    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value or not value.strip():
            raise ValueError("Название задачи не может быть пустым")
        self._title = value.strip()
        self._updated_at = datetime.now()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value.strip() if value else ""
        self._updated_at = datetime.now()

    @property
    def priority(self) -> Priority:
        return self._priority

    @priority.setter
    def priority(self, value: Priority):
        self._priority = value
        self._updated_at = datetime.now()

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Status):
        self._status = value
        self._updated_at = datetime.now()

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для JSON"""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "priority": self._priority.value,
            "status": self._status.value,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Создание задачи из словаря"""
        task = cls(
            task_id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=Priority.from_string(data["priority"]),
            status=Status.from_string(data["status"])
        )
        task._created_at = datetime.fromisoformat(data["created_at"])
        task._updated_at = datetime.fromisoformat(data["updated_at"])
        return task

    def __str__(self) -> str:
        priority_icon = {
            Priority.HIGH: "🔴",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢"
        }.get(self._priority, "⚪")

        status_icon = {
            Status.TODO: "⭕",
            Status.IN_PROGRESS: "🔄",
            Status.DONE: "✅"
        }.get(self._status, "❓")

        return (f"[{self._id}] {priority_icon} {self._title[:30]} | "
                f"{status_icon} {self._status.value} | {self._priority.value}")


class TaskManager:
    """Модель для управления задачами"""

    def __init__(self, filename: str = "tasks.json"):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
        self._filename = filename
        self._priority_queue = deque()  # Очередь задач по приоритету
        self._undo_stack = []  # Стек для отмены действий
        self._redo_stack = []  # Стек для повтора действий
        self._load_data()

    def _load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(self._filename):
            try:
                with open(self._filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data:
                        task = Task.from_dict(task_data)
                        self._tasks[task.id] = task
                        self._next_id = max(self._next_id, task.id + 1)
                        self._update_priority_queue(task)
                print(f"✅ Загружено {len(self._tasks)} задач")
            except Exception as e:
                print(f"❌ Ошибка загрузки: {e}")
                self._tasks = {}

    def _save_data(self):
        """Сохранение данных в JSON"""
        try:
            data = [task.to_dict() for task in self._tasks.values()]
            with open(self._filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    def _update_priority_queue(self, task: Task):
        """Обновление очереди приоритетов"""
        # Простая реализация - пересоздаем очередь при каждом изменении
        self._rebuild_priority_queue()

    def _rebuild_priority_queue(self):
        """Перестроение очереди приоритетов"""
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_tasks = sorted(
            self._tasks.values(),
            key=lambda t: (priority_order[t.priority], t.created_at)
        )
        self._priority_queue = deque(sorted_tasks)

    def _save_state_for_undo(self):
        """Сохранение состояния для отмены"""
        state = {
            "tasks": {task_id: task.to_dict() for task_id, task in self._tasks.items()},
            "next_id": self._next_id
        }
        self._undo_stack.append(state)
        self._redo_stack.clear()  # Очищаем стек повтора при новом действии

    def undo(self) -> bool:
        """Отмена последнего действия"""
        if not self._undo_stack:
            return False

        # Сохраняем текущее состояние для повтора
        current_state = {
            "tasks": {task_id: task.to_dict() for task_id, task in self._tasks.items()},
            "next_id": self._next_id
        }
        self._redo_stack.append(current_state)

        # Восстанавливаем предыдущее состояние
        previous_state = self._undo_stack.pop()
        self._tasks = {}
        for task_id, task_data in previous_state["tasks"].items():
            self._tasks[task_id] = Task.from_dict(task_data)
        self._next_id = previous_state["next_id"]

        self._rebuild_priority_queue()
        self._save_data()
        return True

    def redo(self) -> bool:
        """Повтор отмененного действия"""
        if not self._redo_stack:
            return False

        # Сохраняем текущее состояние для отмены
        current_state = {
            "tasks": {task_id: task.to_dict() for task_id, task in self._tasks.items()},
            "next_id": self._next_id
        }
        self._undo_stack.append(current_state)

        # Восстанавливаем следующее состояние
        next_state = self._redo_stack.pop()
        self._tasks = {}
        for task_id, task_data in next_state["tasks"].items():
            self._tasks[task_id] = Task.from_dict(task_data)
        self._next_id = next_state["next_id"]

        self._rebuild_priority_queue()
        self._save_data()
        return True

    def add_task(self, title: str, description: str, priority: Priority) -> Task:
        """Добавление новой задачи"""
        self._save_state_for_undo()

        task = Task(self._next_id, title, description, priority)
        self._tasks[task.id] = task
        self._next_id += 1
        self._update_priority_queue(task)
        self._save_data()
        return task

    def update_task(self, task_id: int, title: Optional[str] = None,
                    description: Optional[str] = None, priority: Optional[Priority] = None,
                    status: Optional[Status] = None) -> Optional[Task]:
        """Обновление задачи"""
        if task_id not in self._tasks:
            return None

        self._save_state_for_undo()
        task = self._tasks[task_id]

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.status = status

        self._update_priority_queue(task)
        self._save_data()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        if task_id not in self._tasks:
            return False

        self._save_state_for_undo()
        del self._tasks[task_id]
        self._rebuild_priority_queue()
        self._save_data()
        return True

    def get_task(self, task_id: int) -> Optional[Task]:
        """Получение задачи по ID"""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Получение всех задач"""
        return list(self._tasks.values())

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Фильтрация по приоритету"""
        return [task for task in self._tasks.values() if task.priority == priority]

    def get_tasks_by_status(self, status: Status) -> List[Task]:
        """Фильтрация по статусу"""
        return [task for task in self._tasks.values() if task.status == status]

    def get_priority_queue(self) -> deque:
        """Получение очереди приоритетов"""
        self._rebuild_priority_queue()
        return self._priority_queue

    def can_undo(self) -> bool:
        """Проверка возможности отмены"""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Проверка возможности повтора"""
        return len(self._redo_stack) > 0