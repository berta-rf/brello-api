import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


from sqlalchemy.sql import func

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize ma
ma = Marshmallow(app)


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Project {self.name}>'

    def __init__(self, name, description, status):
        self.name = name
        self.description = description
        self.status = status

    def create(self):
        self.updated_at = datetime.now()
        db.session.add(self)
        db.session.commit()
        return self


# Projects Schema
class ProjectSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'status', 'updated_at', 'created_at')


# Init schema
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


# API ENDPOINTS

# get all projects
@app.route('/projects')
def get_projects():
    all_projects = Project.query.all()
    result = projects_schema.dump(all_projects)
    return jsonify(result)


# get one project
@app.route('/projects/<id>')
def get_project(id):
    project = Project.query.get(id)
    return project_schema.jsonify(project)


# create new project
@app.route('/projects', methods=['POST'])
def add_project():
    name = request.json['name']
    description = request.json['description']
    status = request.json['status']

    new_project = Project(name, description, status)

    Project.create(new_project)
    return project_schema.jsonify(new_project)


# update project
@app.route('/projects/<id>', methods=['PUT'])
def update_project(id):
    project = Project.query.get(id)

    if 'name' in request.json:
        project.name = request.json['name']

    if 'description' in request.json:
        project.description = request.json['description']

    if 'status' in request.json:
        project.status = request.json['status']

    db.session.commit()

    return project_schema.jsonify(project)


# delete project
@app.route('/projects/<id>', methods=['DELETE'])
def delete_project(id):
    project = Project.query.get(id)
    db.session.delete(project)
    db.session.commit()

    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5002)
