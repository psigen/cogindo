from cogindo import app
from flask import render_template, current_app
from flask.ext.security import login_required


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        content='Profile Page',
        google_conn=current_app.extensions['social'].google.get_connection())


@app.route('/team')
@login_required
def team():
    return render_template(
        'team.html',
        content='Team Page')
