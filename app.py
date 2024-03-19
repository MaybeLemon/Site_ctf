from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import hashlib

from flags_solved_handler import handler
from navigation import get_nav
from tasks import TasksGetter
from time_getter import timegetter

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ctf_table.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

data = {'nav': get_nav(app), 'otvet': ''}

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    time = db.Column(db.String(100))
    count = db.Column(db.Integer, default=0)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    task_type = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    flag = db.Column(db.String(100), nullable=False)
    users_solved = db.relationship('UserSolved', backref='task', lazy=True)

class UserSolved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        user_obj = Users.query.filter_by(username=current_user.username).first()
        data['points'] = user_obj.points
        data['admin'] = user_obj.admin
    else:
        data['admin'] = False
        data['points'] = ''

@app.route('/login', methods=['GET', 'POST'])
def login():
    data['otvet'] = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '' or password == '':
            data['otvet'] = 'Введите данные'
            return render_template('login.html', data=data)

        hash_sha512 = hashlib.sha512()
        hash_sha512.update(password.encode('utf-8'))
        pass_hash = hash_sha512.hexdigest()
        user = Users.query.filter_by(username=username).first()
        if user and user.password == hashlib.sha512(password.encode('utf-8')).hexdigest():
            login_user(user)
            return redirect(url_for('tasks'))
        else:
            data['otvet'] = 'Неверный логин или пароль'

    return render_template('login.html', data=data)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    data['otvet'] = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '' or password == '':
            data['otvet'] = 'Введите данные'
            return render_template('reg.html', data=data)
        hash_sha512 = hashlib.sha512()
        hash_sha512.update(password.encode('utf-8'))
        pass_hash = hash_sha512.hexdigest()
        if not Users.query.filter_by(username=username).first():
            new_user = Users(username=username, password=pass_hash, time=timegetter())
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
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
    return render_template('index.html', data=data)


@app.route('/tasks')
def tasks():
    taskgetter = TasksGetter(Task, db)
    if current_user.is_authenticated:
        data['user_solved'] = [result[0] for result in UserSolved.query.filter_by(user=current_user.username).with_entities(UserSolved.task_id).distinct().all()]
    else:
        data['user_solved'] = []
    data['task_types'] = taskgetter.get_task_types()

    if 'sort_type' in request.args:
        data['tasks'] = taskgetter.get_tasks(sort_type=request.args['sort_type'])
    else:
        data['tasks'] = taskgetter.get_tasks()
    return render_template('list_tasks.html', data=data)


@app.route('/task', methods=['GET', 'POST'])
def task():
    if current_user.is_authenticated:
        users_solved = [result[0] for result in UserSolved.query.filter_by(user=current_user.username).with_entities(UserSolved.task_id).distinct().all()]
    else:
        users_solved = []
    if 'task' in request.args:
        data['current_task'] = TasksGetter(Task, db).read_task(request.args['task'])
        if users_solved is not None and data['current_task'].id in users_solved: data['solved'] = True
        else: data['solved'] = False

        if data['current_task'] is None:
            return render_template('error.html', data=data)
        if request.method == 'POST' and current_user.is_authenticated:
            if request.form['flag'] == data['current_task'].flag:
                data['otvet_task'] = handler(data['current_task'].name, Task, Users, UserSolved, db, current_user)
                data['flag-correct'] = True
            else:
                data['otvet_task'] = 'Ваш флаг неверен'
                data['flag-correct'] = False
        else:
            data['otvet_task'] = ''
    return render_template('task.html', data=data)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not data['admin']:
        return render_template('error.html', data=data)

    if request.method == 'POST':
        TasksGetter(Task, db).write_task(request.form['name'],
                                 request.form['type'],
                                 request.form['description'],
                                 request.form['filename'],
                                 request.form['flag'],
                                 request.form['points'])
    return render_template('admin.html', data=data)


@app.route('/top')
def top():
    data['users'] = Users.query.order_by(Users.points.desc()).all()
    return render_template('top.html', data=data)


@app.route('/file')
def file():
    if 'filename' in request.args:
        return send_file(f"tasks_files/{request.args['type']}/{request.args['filename']}")
    return render_template('error.html', data=data)

@app.route('/profile')
def profile():
    if 'username' in request.args:
        user_on_profile = Users.query.filter_by(username=request.args['username']).first()
        data['username'] = request.args['username']
        data['is_cur_admin'] = user_on_profile.admin
        data['count'] = user_on_profile.count
        data['points'] = user_on_profile.points
    return render_template('profile.html', data=data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run('0.0.0.0', port=5009, debug=True)
