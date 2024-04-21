import json.decoder

import flask.json
from flask import Flask, request, render_template, redirect, url_for, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', tasks=L)


L = []


@app.route('/list/<string:specified_list>/task/<string:task_to_add>', methods=['POST'])
def add_task(task_to_add, specified_list):
    specified_list.append(task_to_add)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    # task_title = request.form.get('title')
    # if task_title:  # Ensure the task title is not empty
    #     tasks.append(task_title)
    # return redirect(url_for('index'))


@app.route('/list/<string:specified_list>/task/<string:task_to_remove>', methods=['DELETE'])
def remove_task(task_to_remove, specified_list):
    specified_list.remove(task_to_remove)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/list', methods=['POST'])
def create():
    # new_list = request.form['new_list']
    new_list = request.json
    L.append(new_list)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/tasks', methods=['GET'])
def tasks():
    return jsonify(L)


if __name__ == '__main__':
    app.run()
