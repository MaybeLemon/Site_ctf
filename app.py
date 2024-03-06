from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import hashlib

from flags_solved_handler import handler
from navigation import get_nav
from tasks import TasksGetter
from users_getter import users_getter, save_users
from time_getter import timegetter

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

data = {'nav': get_nav(app), 'otvet': ''}


class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    data['otvet'] = ''
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '' or password == '':
            data['otvet'] = 'Введите данные'
            return render_template('login.html', data=data)
        hash_sha512 = hashlib.sha512()
        hash_sha512.update(password.encode('utf-8'))
        pass_hash = hash_sha512.hexdigest()
        if username in users and users[username]['password'] == pass_hash:
            user = User(username)
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            data['otvet'] = 'Неверный логин или пароль'

    return render_template('login.html', data=data)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    data['otvet'] = ''
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '' or password == '':
            data['otvet'] = 'Введите данные'
            return render_template('reg.html', data=data)
        hash_sha512 = hashlib.sha512()
        hash_sha512.update(password.encode('utf-8'))
        pass_hash = hash_sha512.hexdigest()
        if username not in users:
            users[username] = {'password': pass_hash, 'points': 0, 'admin': False, 'time': timegetter()}
            save_users(users)
            user = User(username)
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            data['error'] = 'Пользователь с таким именем уже существует.'
            return render_template('reg.html', data=data)

    return render_template('reg.html', data=data)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('login'))

@app.route('/')
def hello():
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    return render_template('index.html', data=data)


@app.route('/tasks')
def tasks():
    taskgetter = TasksGetter()
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    data['tasks-type'] = taskgetter.tasks_types
    if current_user.is_authenticated:
        data['points'] = users[current_user.username]['points']
    else:
        data['points'] = ''
    if 'sort_type' in request.args:
        data['tasks'] = taskgetter.get_tasks(sort_type=request.args['sort_type'])
    else:
        data['tasks'] = taskgetter.get_tasks()
    return render_template('list_tasks.html', data=data)


@app.route('/task', methods=['GET', 'POST'])
def task():
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    if 'task' in request.args:
        data['current_task'] = TasksGetter().read_task(request.args['task'])
        if request.method == 'POST' and current_user.is_authenticated:
            if request.form['flag'] == data['current_task']['flag']:
                all_tasks = TasksGetter().get_tasks()
                handler(data['current_task']['name'], all_tasks, current_user)
                data['otvet_task'] = 'Ваш флаг верен'
                data['flag-correct'] = True
            else:
                data['otvet_task'] = 'Ваш флаг неверен'
                data['flag-correct'] = False
        else:
            data['otvet_task'] = ''
    return render_template('task.html', data=data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    if not data['admin']:
        render_template('error.html', data=data)

    if request.method == 'POST':
        TasksGetter().write_task(request.form['name'],
                                 request.form['type'],
                                 request.form['description'],
                                 request.form['filename'],
                                 request.form['flag'],
                                 request.form['points'])
    return render_template('admin.html', data=data)

@app.route('/top')
def top():
    users = users_getter()
    if current_user.is_authenticated:
        data['admin'] = users[current_user.username]['admin']
    else:
        data['admin'] = False
    data['users'] = sorted(users.items(), key=lambda x: x[1]['points'], reverse=True)
    return render_template('top.html', data=data)

@app.route('/file')
def file():
    if 'filename' in request.args:
        return send_file(f'tasks_files/{request.args['type']}/{request.args['filename']}')
    return render_template('error.html', data=data)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
