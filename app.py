from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', tasks=L)


L = []


@app.route('/add', methods=['POST'])
def add_task(task, specified_list):
    specified_list.append(task)
    # task_title = request.form.get('title')
    # if task_title:  # Ensure the task title is not empty
    #     tasks.append(task_title)
    # return redirect(url_for('index'))


@app.route('/add/<string:a>', methods=['DELETE'])
def remove_from_list(task, specified_list):
    specified_list.remove(task)


@app.route('/create', methods=['POST'])
def create():
    new_list = request.form['new_list']
    L.append(new_list)


if __name__ == '__main__':
    app.run()