import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy


from sqlalchemy.sql import func

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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

    def obj_to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "updated_at": str(self.updated_at),
            "created_at": str(self.created_at)
        }


def dict_helper(objlist):
    result = [item.obj_to_json() for item in objlist]
    return result


@app.route('/')
def get_projects():
    data = Project.query.all()
    projects_json = dict_helper(data)
    return jsonify(projects_json)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
