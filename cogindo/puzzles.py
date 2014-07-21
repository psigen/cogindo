from cogindo import app
from cogindo import db

from flask import render_template
from flask.ext.security import login_required


class PuzzleInstance(db.Document):
    name = db.StringField(max_length=80)


class Team(db.Document):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)
    puzzles = db.ListField(db.ReferenceField(PuzzleInstance), default=[])


@app.route('/team')
@login_required
def team():
    return render_template(
        'team.html',
        content='Team Page')
