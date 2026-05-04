from typing import List, Optional
from model import Task, Priority, Status


class TaskView:
    """Класс для отображения информации пользователю"""

    @staticmethod
    def show_menu():
        """Отображение главного меню"""
        print("\n" + "=" * 60)
        print("📋 TASK MANAGER - Менеджер задач")
        print("=" * 60)
        print("1. ➕ Добавить задачу")
        print("2. 📋 Показать все задачи")
        print("3. ✏️ Редактировать задачу")
        print("4. 🗑️ Удалить задачу")
        print("5. 🔍 Фильтрация задач")
        print("6. 📊 Показать очередь приоритетов")
        print("7. ↩️ Отменить последнее действие (Undo)")
        print("8. ↩️ Повторить действие (Redo)")
        print("9. 💾 Сохранить данные")
        print("0. 🚪 Выход")
        print("=" * 60)

    @staticmethod
    def show_tasks(tasks: List[Task], title: str = "Список задач"):
        """Отображение списка задач"""
        if not tasks:
            print(f"\n❌ {title} пуст")
            return

        print(f"\n📌 {title}:")
        print("-" * 60)
        for task in tasks:
            print(f"  {task}")
            print(f"     📝 {task.description[:50]}..." if len(task.description) > 50 else f"     📝 {task.description}")
            print(f"     🕐 Создана: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 60)
        print(f"📊 Всего: {len(tasks)} задач")

    @staticmethod
    def show_priority_queue(tasks: List[Task]):
        """Отображение очереди приоритетов"""
        if not tasks:
            print("\n❌ Очередь приоритетов пуста")
            return

        print("\n🎯 ОЧЕРЕДЬ ПРИОРИТЕТОВ:")
        print("=" * 60)
        for i, task in enumerate(tasks, 1):
            priority_icon = "🔴" if task.priority == Priority.HIGH else "🟡" if task.priority == Priority.MEDIUM else "🟢"
            print(f"{i}. {priority_icon} [{task.id}] {task.title} - {task.priority.value}")
        print("=" * 60)

    @staticmethod
    def get_task_input() -> dict:
        """Получение данных для новой задачи"""
        print("\n--- Добавление новой задачи ---")

        # Ввод названия
        while True:
            title = input("Название задачи: ").strip()
            if title:
                break
            print("❌ Название не может быть пустым")

        # Ввод описания
        description = input("Описание задачи: ").strip()

        # Ввод приоритета
        while True:
            print("\nДоступные приоритеты:")
            print("1. Low (Низкий) 🟢")
            print("2. Medium (Средний) 🟡")
            print("3. High (Высокий) 🔴")
            choice = input("Выберите приоритет (1-3): ").strip()

            if choice == '1':
                priority = Priority.LOW
                break
            elif choice == '2':
                priority = Priority.MEDIUM
                break
            elif choice == '3':
                priority = Priority.HIGH
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")

        return {
            "title": title,
            "description": description,
            "priority": priority
        }

    @staticmethod
    def get_task_id(prompt: str = "Введите ID задачи") -> Optional[int]:
        """Получение ID задачи"""
        try:
            task_id = int(input(f"{prompt}: ").strip())
            return task_id
        except ValueError:
            print("❌ Неверный формат ID. Введите число.")
            return None

    @staticmethod
    def get_edit_input(task: Task) -> dict:
        """Получение данных для редактирования задачи"""
        print(f"\n--- Редактирование задачи #{task.id} ---")
        print(f"Текущее название: {task.title}")
        new_title = input("Новое название (ENTER для пропуска): ").strip()

        print(f"Текущее описание: {task.description}")
        new_description = input("Новое описание (ENTER для пропуска): ").strip()

        # Редактирование приоритета
        print(f"\nТекущий приоритет: {task.priority.value}")
        print("Новый приоритет:")
        print("1. Low (Низкий)")
        print("2. Medium (Средний)")
        print("3. High (Высокий)")
        print("ENTER для пропуска")
        priority_choice = input("Выберите (1-3): ").strip()

        new_priority = None
        if priority_choice == '1':
            new_priority = Priority.LOW
        elif priority_choice == '2':
            new_priority = Priority.MEDIUM
        elif priority_choice == '3':
            new_priority = Priority.HIGH

        # Редактирование статуса
        print(f"\nТекущий статус: {task.status.value}")
        print("Новый статус:")
        print("1. To Do")
        print("2. In Progress")
        print("3. Done")
        print("ENTER для пропуска")
        status_choice = input("Выберите (1-3): ").strip()

        new_status = None
        if status_choice == '1':
            new_status = Status.TODO
        elif status_choice == '2':
            new_status = Status.IN_PROGRESS
        elif status_choice == '3':
            new_status = Status.DONE

        return {
            "title": new_title if new_title else None,
            "description": new_description if new_description else None,
            "priority": new_priority,
            "status": new_status
        }

    @staticmethod
    def get_filters() -> dict:
        """Получение параметров фильтрации"""
        print("\n--- Фильтрация задач ---")
        print("Фильтр по статусу:")
        print("1. To Do")
        print("2. In Progress")
        print("3. Done")
        print("0. Пропустить")

        status_choice = input("Выберите (0-3): ").strip()
        status = None
        if status_choice == '1':
            status = Status.TODO
        elif status_choice == '2':
            status = Status.IN_PROGRESS
        elif status_choice == '3':
            status = Status.DONE

        print("\nФильтр по приоритету:")
        print("1. Low")
        print("2. Medium")
        print("3. High")
        print("0. Пропустить")

        priority_choice = input("Выберите (0-3): ").strip()
        priority = None
        if priority_choice == '1':
            priority = Priority.LOW
        elif priority_choice == '2':
            priority = Priority.MEDIUM
        elif priority_choice == '3':
            priority = Priority.HIGH

        return {
            "status": status,
            "priority": priority
        }

    @staticmethod
    def show_message(message: str, is_error: bool = False):
        """Отображение сообщения"""
        prefix = "❌" if is_error else "✅"
        print(f"{prefix} {message}")

    @staticmethod
    def show_task_details(task: Task):
        """Отображение деталей задачи"""
        print("\n" + "=" * 60)
        print(f"📌 ЗАДАЧА #{task.id}")
        print("=" * 60)
        print(f"Название: {task.title}")
        print(f"Описание: {task.description}")
        print(f"Приоритет: {task.priority.value}")
        print(f"Статус: {task.status.value}")
        print(f"Создана: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Обновлена: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)