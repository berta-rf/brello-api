import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


from sqlalchemy.sql import func

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize ma
ma = Marshmallow(app)


# PROJECT CLASS
class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    tasks = db.relationship('Task', backref='projects')

    def __repr__(self):
        return f'<Project {self.name}>'

    def __init__(self, name, description, due_date):
        self.name = name
        self.description = description
        self.due_date = due_date

    def create(self):
        self.updated_at = datetime.now()
        db.session.add(self)
        db.session.commit()
        return self

    def touch(self):
        if self.id is not None:
            self.updated_at = datetime.now()
            db.session.commit()
        return self


# Projects Schema
class ProjectSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'due_date', 'updated_at', 'created_at')


# Init schema
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


# API PROJECT ENDPOINTS

# get all projects
@app.route('/projects')
def get_projects():
    all_projects = db.session.execute(db.select(Project)).scalars()
    result = projects_schema.dump(all_projects)
    return jsonify(result)


# get one project
@app.route('/projects/<id>')
def get_project(id):
    project = db.get_or_404(Project, id)
    return project_schema.jsonify(project)


# create new project
@app.route('/projects', methods=['POST'])
def add_project():
    name = request.json['name']
    description = request.json['description']
    due_date = request.json['due_date']

    new_project = Project(name, description, due_date)

    Project.create(new_project)
    return project_schema.jsonify(new_project)


# update project
@app.route('/projects/<id>', methods=['PUT'])
def update_project(id):
    project = db.get_or_404(Project, id)

    if 'name' in request.json:
        project.name = request.json['name']

    if 'description' in request.json:
        project.description = request.json['description']

    if 'due_date' in request.json:
        project.due_date = request.json['due_date']

    db.session.commit()

    return project_schema.jsonify(project)


# delete project
@app.route('/projects/<id>', methods=['DELETE'])
def delete_project(id):
    project = db.get_or_404(Project, id)
    db.session.delete(project)
    db.session.commit()

    return "", 204


# TASK CLASS
class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    def __repr__(self):
        return f'<Task {self.name}>'

    def __init__(self, name, summary, status, priority):
        self.name = name
        self.summary = summary
        self.status = status
        self.priority = priority

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


# Task Schema
class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'summary', 'status', 'priority', 'project_id')


# Init schema
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


# API TASK ENDPOINTS

# get all tasks for a project
@app.route('/projects/<project_id>/tasks')
def get_tasks(project_id):
    all_tasks = db.session.execute(db.select(Task).where(Task.project_id == project_id)).scalars()
    result = tasks_schema.dump(all_tasks)
    return jsonify(result)


# create new task
@app.route('/projects/<project_id>/tasks', methods=['POST'])
def add_task(project_id):

    project = db.get_or_404(Project, project_id)

    name = request.json['name']
    summary = request.json['summary']
    status = request.json['status']
    priority = request.json['priority']

    new_task = Task(name, summary, status, priority)
    new_task.project_id = project_id

    Task.create(new_task)
    project.touch()

    return task_schema.jsonify(new_task)


# update task
@app.route('/projects/<project_id>/tasks/<id>', methods=['PUT'])
def update_task(project_id, id):

    project = db.get_or_404(Project, project_id)
    task = db.get_or_404(Task, id)

    if 'name' in request.json:
        task.name = request.json['name']

    if 'summary' in request.json:
        task.summary = request.json['summary']

    if 'status' in request.json:
        task.status = request.json['status']

    if 'priority' in request.json:
        task.priority = request.json['priority']

    db.session.commit()
    project.touch()

    return task_schema.jsonify(task)


# delete task
@app.route('/projects/<project_id>/tasks/<id>', methods=['DELETE'])
def delete_task(project_id, id):
    task = db.get_or_404(Task, id)
    db.session.delete(task)
    db.session.commit()

    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5002)
