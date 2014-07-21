from flask import render_template, current_app, redirect, url_for
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, login_user
from flask.ext.social import Social, login_failed
from flask.ext.social.utils import get_connection_values_from_oauth_response
from flask.ext.social.views import connect_handler
from flask.ext.social.datastore import MongoEngineConnectionDatastore
import uuid

from cogindo import app
from cogindo import db
from cogindo.puzzles import Team


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    name = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    remember_token = db.StringField(max_length=255)
    authentication_token = db.StringField(max_length=255)
    roles = db.ListField(db.ReferenceField(Role), default=[])
    team = db.ReferenceField(Team)

    meta = {
        'indexes': [
            {'fields': ['email'], 'unique': True,
             'sparse': True, 'types': False},
        ],
    }

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

    ds = current_app.extensions['security'].datastore
    ds.create_user(name='PRAS', email='pras@example.com', password='moocow')
    ds.create_user(name='PYRY', email='pyry@example.com', password='asdf')
    ds.commit()


@app.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html',
        content='Profile Page',
        google_conn=current_app.extensions['social'].google.get_connection())


@login_failed.connect_via(app)
def on_login_failed(sender, provider, oauth_response):
    connection_values = \
        get_connection_values_from_oauth_response(provider, oauth_response)

    ds = current_app.extensions['security'].datastore
    user = ds.create_user(name=connection_values['display_name']['givenName'],
                          password=str(uuid.uuid4()))
    ds.commit()

    connection_values['user_id'] = user.id
    connection_values['display_name'] = \
        connection_values['display_name']['givenName']
    connection_values['full_name'] = \
        ' '.join([connection_values['full_name']['givenName'],
                  connection_values['full_name']['familyName']])
    connect_handler(connection_values, provider)
    login_user(user)

    return redirect(url_for('profile'))
