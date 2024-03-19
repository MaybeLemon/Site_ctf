class TasksGetter:
    def __init__(self, Task, db):
        self.Task = Task
        self.db = db
        self.tasks = []

    def get_task_types(self):
        unique_task_types = [result[0] for result in self.Task.query.with_entities(self.Task.task_type).distinct()]
        return unique_task_types

    def get_tasks(self, sort_type=''):
        if sort_type:
            return self.Task.query.filter_by(task_type=sort_type).all()
        else:
            return self.Task.query.order_by(self.Task.task_type).all()

    def write_task(self, name, task_type, description, filename, flag, points):
        new_task = self.Task(name=name, task_type=task_type, points=points, description=description, filename=filename, flag=flag)
        self.db.session.add(new_task)
        self.db.session.commit()

    def read_task(self, name):
        task = self.Task.query.filter_by(name=name).first()
        return task

# Пример использования
# tasks_getter = TasksGetter()
# name = 'Задача1'
# task_type = 'Тип1'
# description = 'Описание1'
# tasks_getter.write_task(name, task_type, description)
