import json.decoder

import flask.json
from flask import Flask, request, render_template, redirect, url_for, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', taskList=L)


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
    app.run()
