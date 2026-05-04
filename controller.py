from typing import Optional
from model import TaskManager, Priority, Status
from view import TaskView


class MenuController:
    """Контроллер для обработки команд пользователя"""

    def __init__(self):
        self.model = TaskManager()
        self.view = TaskView()
        self.running = True

    def run(self):
        """Запуск главного цикла приложения"""
        while self.running:
            self.view.show_menu()
            choice = input("\nВыберите действие: ").strip()
            self.handle_choice(choice)

    def handle_choice(self, choice: str):
        """Обработка выбора пользователя"""
        if choice == '1':
            self.add_task()
        elif choice == '2':
            self.show_all_tasks()
        elif choice == '3':
            self.edit_task()
        elif choice == '4':
            self.delete_task()
        elif choice == '5':
            self.filter_tasks()
        elif choice == '6':
            self.show_priority_queue()
        elif choice == '7':
            self.undo_action()
        elif choice == '8':
            self.redo_action()
        elif choice == '9':
            self.save_data()
        elif choice == '0':
            self.exit_app()
        else:
            self.view.show_message("Неверный выбор. Попробуйте снова.", is_error=True)

    def add_task(self):
        """Добавление задачи"""
        task_data = self.view.get_task_input()
        task = self.model.add_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"]
        )
        self.view.show_message(f"Задача #{task.id} успешно добавлена!")

    def show_all_tasks(self):
        """Показать все задачи"""
        tasks = self.model.get_all_tasks()
        if tasks:
            self.view.show_tasks(tasks, "Все задачи")
        else:
            self.view.show_message("Нет добавленных задач", is_error=True)

    def edit_task(self):
        """Редактирование задачи"""
        task_id = self.view.get_task_id("Введите ID задачи для редактирования")
        if task_id is None:
            return

        task = self.model.get_task(task_id)
        if not task:
            self.view.show_message(f"Задача #{task_id} не найдена", is_error=True)
            return

        self.view.show_task_details(task)
        edit_data = self.view.get_edit_input(task)

        updated_task = self.model.update_task(
            task_id=task_id,
            title=edit_data["title"],
            description=edit_data["description"],
            priority=edit_data["priority"],
            status=edit_data["status"]
        )

        if updated_task:
            self.view.show_message(f"Задача #{task_id} успешно обновлена!")
        else:
            self.view.show_message(f"Ошибка при обновлении задачи", is_error=True)

    def delete_task(self):
        """Удаление задачи"""
        task_id = self.view.get_task_id("Введите ID задачи для удаления")
        if task_id is None:
            return

        task = self.model.get_task(task_id)
        if not task:
            self.view.show_message(f"Задача #{task_id} не найдена", is_error=True)
            return

        self.view.show_task_details(task)
        confirm = input(f"\nУдалить задачу #{task_id}? (y/n): ").strip().lower()

        if confirm == 'y':
            if self.model.delete_task(task_id):
                self.view.show_message(f"Задача #{task_id} успешно удалена!")
            else:
                self.view.show_message(f"Ошибка при удалении задачи", is_error=True)
        else:
            self.view.show_message("Удаление отменено")

    def filter_tasks(self):
        """Фильтрация задач"""
        filters = self.view.get_filters()

        tasks = self.model.get_all_tasks()

        if filters["status"]:
            tasks = [t for t in tasks if t.status == filters["status"]]
        if filters["priority"]:
            tasks = [t for t in tasks if t.priority == filters["priority"]]

        if tasks:
            filter_desc = []
            if filters["status"]:
                filter_desc.append(f"статус={filters['status'].value}")
            if filters["priority"]:
                filter_desc.append(f"приоритет={filters['priority'].value}")

            title = f"Отфильтрованные задачи ({', '.join(filter_desc)})" if filter_desc else "Все задачи"
            self.view.show_tasks(tasks, title)
        else:
            self.view.show_message("Задачи не найдены по указанным фильтрам", is_error=True)

    def show_priority_queue(self):
        """Показать очередь приоритетов"""
        queue = self.model.get_priority_queue()
        self.view.show_priority_queue(list(queue))

    def undo_action(self):
        """Отмена последнего действия"""
        if self.model.undo():
            self.view.show_message("Последнее действие отменено")
        else:
            self.view.show_message("Нет действий для отмены", is_error=True)

    def redo_action(self):
        """Повтор отмененного действия"""
        if self.model.redo():
            self.view.show_message("Действие повторено")
        else:
            self.view.show_message("Нет действий для повтора", is_error=True)

    def save_data(self):
        """Сохранение данных"""
        self.model._save_data()
        self.view.show_message("Данные сохранены!")

    def exit_app(self):
        """Выход из приложения"""
        self.view.show_message("До свидания!")
        self.running = False