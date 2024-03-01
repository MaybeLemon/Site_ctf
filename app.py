from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from navigation import get_nav

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

data = {'nav': get_nav(app)}


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

users = {'user1': {'password': 'password1'},
         'user2': {'password': 'password2'}}

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


@app.route('/protected')
@login_required
def protected():
    return 'Защищенная страница. Только для авторизованных пользователей.'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Вы успешно вышли из системы.'



@app.route('/')
def hello_world():
    return render_template('index.html', data=data)


@app.route('/tasks')
def tasks():
    return render_template('tasks.html', data=data)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
