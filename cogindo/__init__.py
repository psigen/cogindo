import os
from flask import Flask

from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'  # TODO: secure this

# Configure a database client.
app.config["MONGODB_SETTINGS"] = \
    {"DB": os.environ.get("MONGODB_DATABASE", "cogindo"),
     "USERNAME": os.environ.get("MONGODB_USER", ""),
     "PASSWORD": os.environ.get("MONGODB_PASS", ""),
     "HOST": os.environ.get("MONGODB_HOST", "localhost"),
     "PORT": int(os.environ.get("MONGODB_PORT", "27017"))}

# Configure Google oauth login.
app.config['SECURITY_POST_LOGIN'] = '/profile'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['id']
app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': os.environ.get("SOCIAL_GOOGLE_KEY",
        '989743370750-67nsgjpaojfbfdpd5fugrih9r8696buj.apps.googleusercontent.com'),
    'consumer_secret': os.environ.get("SOCIAL_GOOGLE_SECRET",
        's0BOlRGv9203qsXYNtB2rSbL')
}

# Initialize flask extensions.
db = MongoEngine(app)
api = Api(app)

# Create route views.
import cogindo.users
import cogindo.views
cogindo.views  # TODO: keep linter from complaining.
