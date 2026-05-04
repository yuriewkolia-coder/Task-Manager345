#!/usr/bin/env python3
"""
Task Manager Application
Console-based task management system with MVC pattern, queues, stacks, and JSON storage
"""

from controller import MenuController


def main():
    """Главная функция"""
    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК TASK MANAGER")
    print("=" * 60)

    app = MenuController()
    app.run()


if __name__ == "__main__":
    main()