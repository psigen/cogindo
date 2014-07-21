from flask import render_template, current_app
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.social import Social
from flask.ext.social.datastore import MongoEngineConnectionDatastore

from cogindo import app
from cogindo import db


class Team(db.Document):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(unique=True, max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    remember_token = db.StringField(max_length=255)
    authentication_token = db.StringField(max_length=255)
    roles = db.ListField(db.ReferenceField(Role), default=[])
    team = db.ReferenceField(Team)

    @property
    def connections(self):
        return Connection.objects(user_id=str(self.id))


class Connection(db.Document):
    user_id = db.ObjectIdField()
    provider_id = db.StringField(max_length=255)
    provider_user_id = db.StringField(max_length=255)
    access_token = db.StringField(max_length=255)
    secret = db.StringField(max_length=255)
    display_name = db.StringField(max_length=255)
    full_name = db.StringField(max_length=255)
    profile_url = db.StringField(max_length=512)
    image_url = db.StringField(max_length=512)
    rank = db.IntField(default=1)

    @property
    def user(self):
        return User.objects(id=self.user_id).first()

# Setup Flask-Security.
Security(app, MongoEngineUserDatastore(db, User, Role))
Social(app, MongoEngineConnectionDatastore(db, Connection))


# Create test users.
@app.before_first_request
def create_default_users():
    for m in [User, Role, Connection]:
        m.drop_collection()

    current_app.security.datastore.create_user(email='psigen@gmail.com',
                                               password='moocow')
    current_app.security.datastore.create_user(email='jkl@example.com',
                                               password='jkljkl')
    current_app.security.datastore.commit()


@app.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        content='Profile Page',
        google_conn=current_app.social.google.get_connection())
