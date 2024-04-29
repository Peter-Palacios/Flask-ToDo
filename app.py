import json.decoder
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask import Flask, request, render_template, redirect, url_for, jsonify, session, current_app
from wtforms import ValidationError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    list_name = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='list', lazy='dynamic')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
    task_title = db.Column(db.String)
    task_description = db.Column(db.String)
    done = db.Column(db.Boolean)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    lists = db.relationship('List', backref='user', lazy='dynamic')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must match.')
    ])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        json_data = request.get_json(silent=True)

        if json_data:
            username = json_data.get('username')
            password = json_data.get('password')
        else:
            form = LoginForm()
            if form.validate_on_submit():
                username = form.username.data
                password = form.password.data
            else:
                return render_template('login.html', form=form)

        # Common authentication logic
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                if json_data:
                    return jsonify({'success': True}), 200  # Return JSON if called via API
                else:
                    return redirect(url_for('index'))
            else:
                error_message = "Invalid username or password"
                if json_data:
                    return jsonify({'success': False, 'message': error_message}), 401
                else:
                    return render_template('login.html', form=form, error=error_message)

    return render_template('login.html', form=LoginForm())


def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
        raise ValidationError('Username already exists. Choose a different one.')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    user_lists = List.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', name=current_user.username, taskList=user_lists)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is not None:
            form.username.errors.append('Username already exists. Choose a different one.')
            return render_template('register.html', form=form)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


# L = {}


@app.route('/list/<string:specified_list>/task/', methods=['POST'])
@login_required
def add_task(specified_list):
    user_list = List.query.filter_by(user_id=current_user.id, list_name=specified_list).first()
    if not user_list:
        return jsonify({'error': 'List not found'}), 404

    task_data = request.get_json()
    task_title = task_data.get('task_title')
    if not task_title:
        return jsonify({'error': 'Task title is required'}), 400

    new_task = Task(list_id=user_list.id, task_title=task_title, task_description=task_data.get('task_description', ''),
                    done=False)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({'success': True, 'task_id': new_task.id}), 200


@app.route('/list/<string:specified_list>/task', methods=['DELETE'])
@login_required
def remove_task(specified_list):
    task_data = request.get_json()
    task_to_remove = task_data.get('task_title')
    user_list = List.query.filter_by(user_id=current_user.id, list_name=specified_list).first()
    if not user_list:
        return jsonify({'error': 'List not found'}), 404

    user_task = user_list.tasks.filter_by(task_title=task_to_remove).first()
    if not user_task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(user_task)
    db.session.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/list', methods=['POST'])
@login_required
def create():
    request_json = request.get_json()
    new_list = request_json.get('new_list')
    if new_list is None:
        return jsonify({'success': False, 'error': 'Incorrect data type provided'}), 400
    new_user_list = List.query.filter_by(user_id=current_user.id, list_name=new_list).first()

    if new_user_list:
        return jsonify({'success': False, 'error': f'List {new_list} already exists'}), 400

    db.session.add(List(user_id=current_user.id, list_name=new_list))
    db.session.commit()

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/tasks', methods=['GET'])
@login_required
def tasks():
    all_lists = List.query.filter_by(user_id=current_user.id).all()
    tasks_by_list = {}

    for user_list in all_lists:
        list_tasks = Task.query.filter_by(list_id=user_list.id).all()
        tasks_by_list[user_list.list_name] = [task.task_title for task in list_tasks]

    return jsonify(tasks_by_list)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
