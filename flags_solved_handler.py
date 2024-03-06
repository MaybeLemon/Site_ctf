from time_getter import timegetter
from users_getter import users_getter
import json


def handler(current_task, all_tasks, current_user):
    task_index = None
    for index, task in enumerate(all_tasks):
        if task['name'] == current_task:
            task_index = index
            break

    if task_index is not None:
        all_users = users_getter()
        all_users[current_user.username]['points'] += int(all_tasks[task_index]['points'])
        all_tasks[task_index]['users_solved'].append({"user": current_user.username, "time": timegetter()})

    with open('users.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_users, json_file, ensure_ascii=False, indent=4)

    with open('tasks.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_tasks, json_file, ensure_ascii=False, indent=4)
