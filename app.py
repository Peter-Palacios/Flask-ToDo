import json.decoder
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask import Flask, request, render_template, redirect, url_for, jsonify
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


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html', form=form)


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
    return render_template('index.html', name=current_user.username, taskList=L)


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



L = {}


@app.route('/list/<string:specified_list>/task/<string:task_to_add>', methods=['POST'])
def add_task(task_to_add, specified_list):
    if specified_list not in L:
        return jsonify({'error': 'List not found'}), 404
    L[specified_list].append(task_to_add)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/list/<string:specified_list>/task/<string:task_to_remove>', methods=['DELETE'])
def remove_task(task_to_remove, specified_list):
    if specified_list not in L.keys():
        return jsonify({'error': 'List not found'}), 404
    if task_to_remove not in L[specified_list]:
        return jsonify({'error': 'Task not found'}), 404
    L[specified_list].remove(task_to_remove)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/list', methods=['POST'])
def create():
    # new_list = request.form['new_list']
    request_json = request.get_json()
    new_list = request_json.get('new_list')
    if new_list is None:
        return jsonify({'success': False, 'error': 'Incorrect data type provided'}), 400
    L[new_list] = []

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/tasks', methods=['GET'])
def tasks():
    return jsonify(L)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
