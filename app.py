from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from flags_solved_handler import handler
from navigation import get_nav
from tasks import TasksGetter

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

data = {'nav': get_nav(app)}


class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        return self.username

users = {'admin': {'password': 'qwerty123'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            return 'Неправильное имя пользователя или пароль'

    return render_template('login.html', data=data)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in users:
            users[username] = {'password': password}
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
    return render_template('login.html', data=data)



@app.route('/')
def hello():
    return render_template('index.html', data=data)


@app.route('/tasks')
def tasks():
    taskgetter = TasksGetter()
    data['tasks-type'] = taskgetter.tasks_types
    if 'sort_type' in request.args:
        data['tasks'] = taskgetter.get_tasks(sort_type=request.args['sort_type'])
    else:
        data['tasks'] = taskgetter.get_tasks()
    return render_template('list_tasks.html', data=data)


@app.route('/task', methods=['GET', 'POST'])
def task():
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
    if request.method == 'POST':
        TasksGetter().write_task(request.form['name'],
                                 request.form['type'],
                                 request.form['description'],
                                 request.form['filename'],
                                 request.form['flag'],
                                 request.form['points'])
    return render_template('admin.html', data=data)

@app.route('/file')
def file():
    if 'filename' in request.args:
        return send_file(f'tasks_files/{request.args['type']}/{request.args['filename']}')
    return render_template('error.html', data=data)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
