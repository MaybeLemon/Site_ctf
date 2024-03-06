import os
import json


class TasksGetter:
    def __init__(self):
        self.tasks = []
        if os.path.exists('tasks.json'):
            with open('tasks.json', 'r', encoding='utf-8') as json_file:
                self.tasks = json.load(json_file)

        self.tasks_types = set(task['task-type'] for task in self.tasks)

    def get_tasks(self, sort_type=''):
        if sort_type:
            return [task for task in self.tasks if task['task-type'] == sort_type]
        else:
            return sorted(self.tasks, key=lambda x: x['task-type'])

    def write_task(self, name, task_type, description, filename, flag, points):
        new_task = {'name': name, 'task-type': task_type, 'points': points, 'description': description,
                    'filename': filename, 'flag': flag, 'users_solved': []}
        self.tasks.append(new_task)
        with open('tasks.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.tasks, json_file, ensure_ascii=False, indent=4)

    def read_task(self, name):
        for task in self.tasks:
            if task['name'] == name:
                return task

# Пример использования
# tasks_getter = TasksGetter()
# name = 'Задача1'
# task_type = 'Тип1'
# description = 'Описание1'
# tasks_getter.write_task(name, task_type, description)
