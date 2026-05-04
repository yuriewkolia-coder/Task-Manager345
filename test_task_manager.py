import unittest
import os
import tempfile
from model import TaskManager, Task, Priority, Status
from datetime import datetime


class TestTaskManager(unittest.TestCase):
    """Тесты для Task Manager"""

    def setUp(self):
        """Подготовка к тестам"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = TaskManager(self.temp_file.name)

    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_add_task_valid(self):
        """Позитивный тест: добавление валидной задачи"""
        task = self.manager.add_task("Test Task", "Test Description", Priority.HIGH)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "Test Description")
        self.assertEqual(task.priority, Priority.HIGH)
        self.assertEqual(task.status, Status.TODO)
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

    def test_add_task_empty_title(self):
        """Негативный тест: пустое название"""
        with self.assertRaises(ValueError):
            self.manager.add_task("", "Description", Priority.MEDIUM)

    def test_add_task_whitespace_title(self):
        """Граничный тест: название из пробелов"""
        with self.assertRaises(ValueError):
            self.manager.add_task("   ", "Description", Priority.MEDIUM)

    def test_update_task(self):
        """Позитивный тест: обновление задачи"""
        task = self.manager.add_task("Old Title", "Old Desc", Priority.LOW)
        updated = self.manager.update_task(task.id, title="New Title", priority=Priority.HIGH)

        self.assertEqual(updated.title, "New Title")
        self.assertEqual(updated.priority, Priority.HIGH)
        self.assertEqual(updated.description, "Old Desc")  # Не изменилось

    def test_update_nonexistent_task(self):
        """Негативный тест: обновление несуществующей задачи"""
        result = self.manager.update_task(999, title="New Title")
        self.assertIsNone(result)

    def test_delete_task(self):
        """Позитивный тест: удаление задачи"""
        task = self.manager.add_task("To Delete", "Desc", Priority.LOW)
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

        result = self.manager.delete_task(task.id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.get_all_tasks()), 0)

    def test_delete_nonexistent_task(self):
        """Негативный тест: удаление несуществующей задачи"""
        result = self.manager.delete_task(999)
        self.assertFalse(result)

    def test_undo_add_task(self):
        """Позитивный тест: отмена добавления"""
        self.manager.add_task("Task 1", "Desc", Priority.MEDIUM)
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

        self.manager.undo()
        self.assertEqual(len(self.manager.get_all_tasks()), 0)

    def test_undo_delete_task(self):
        """Позитивный тест: отмена удаления"""
        task = self.manager.add_task("Task 1", "Desc", Priority.MEDIUM)
        self.manager.delete_task(task.id)
        self.assertEqual(len(self.manager.get_all_tasks()), 0)

        self.manager.undo()
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

    def test_redo_action(self):
        """Позитивный тест: повтор действия"""
        self.manager.add_task("Task 1", "Desc", Priority.MEDIUM)
        self.manager.undo()
        self.assertEqual(len(self.manager.get_all_tasks()), 0)

        self.manager.redo()
        self.assertEqual(len(self.manager.get_all_tasks()), 1)

    def test_filter_by_priority(self):
        """Позитивный тест: фильтрация по приоритету"""
        self.manager.add_task("High Task", "Desc", Priority.HIGH)
        self.manager.add_task("Medium Task", "Desc", Priority.MEDIUM)
        self.manager.add_task("Low Task", "Desc", Priority.LOW)

        high_tasks = self.manager.get_tasks_by_priority(Priority.HIGH)
        self.assertEqual(len(high_tasks), 1)
        self.assertEqual(high_tasks[0].title, "High Task")

    def test_filter_by_status(self):
        """Позитивный тест: фильтрация по статусу"""
        task1 = self.manager.add_task("Task 1", "Desc", Priority.HIGH)
        task2 = self.manager.add_task("Task 2", "Desc", Priority.MEDIUM)

        self.manager.update_task(task1.id, status=Status.IN_PROGRESS)
        self.manager.update_task(task2.id, status=Status.DONE)

        in_progress = self.manager.get_tasks_by_status(Status.IN_PROGRESS)
        done = self.manager.get_tasks_by_status(Status.DONE)

        self.assertEqual(len(in_progress), 1)
        self.assertEqual(len(done), 1)

    def test_priority_queue_order(self):
        """Позитивный тест: порядок в очереди приоритетов"""
        self.manager.add_task("Low Task", "Desc", Priority.LOW)
        self.manager.add_task("High Task", "Desc", Priority.HIGH)
        self.manager.add_task("Medium Task", "Desc", Priority.MEDIUM)

        queue = list(self.manager.get_priority_queue())
        priorities = [task.priority for task in queue]

        # HIGH должен идти первым, затем MEDIUM, затем LOW
        self.assertEqual(priorities[0], Priority.HIGH)
        self.assertEqual(priorities[1], Priority.MEDIUM)
        self.assertEqual(priorities[2], Priority.LOW)

    def test_boundary_max_tasks(self):
        """Граничный тест: максимальное количество задач"""
        # Добавляем 1000 задач
        for i in range(1000):
            self.manager.add_task(f"Task {i}", "Description", Priority.LOW)

        self.assertEqual(len(self.manager.get_all_tasks()), 1000)

    def test_boundary_long_title(self):
        """Граничный тест: очень длинное название"""
        long_title = "A" * 1000
        task = self.manager.add_task(long_title, "Desc", Priority.LOW)
        self.assertEqual(len(task.title), 1000)

    def test_save_and_load(self):
        """Позитивный тест: сохранение и загрузка"""
        self.manager.add_task("Task 1", "Desc", Priority.HIGH)
        self.manager.add_task("Task 2", "Desc 2", Priority.MEDIUM)

        # Создаем новый менеджер с тем же файлом
        new_manager = TaskManager(self.temp_file.name)

        tasks = new_manager.get_all_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].title, "Task 1")
        self.assertEqual(tasks[1].title, "Task 2")

    def test_invalid_priority_string(self):
        """Негативный тест: неверный приоритет в строке"""
        with self.assertRaises(ValueError):
            Priority.from_string("Invalid")

    def test_invalid_status_string(self):
        """Негативный тест: неверный статус в строке"""
        with self.assertRaises(ValueError):
            Status.from_string("Invalid")


if __name__ == "__main__":
    unittest.main()