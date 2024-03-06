import json
import os


def users_getter():
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    else:
        return {}


def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as json_file:
        json.dump(users, json_file, ensure_ascii=False, indent=4)
