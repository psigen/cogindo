from flask import Flask

from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'  # TODO: secure this

# Configure a database client.
app.config["MONGODB_SETTINGS"] = {"DB": "app27634037",
                                  "USERNAME": "P5oG6ydpWz",
                                  "PASSWORD": "a7Uzfg2myw",
                                  "HOST": "kahana.mongohq.com", "PORT": 10051}

# Configure Google oauth login.
app.config['SECURITY_POST_LOGIN'] = '/profile'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['id']
app.config['SOCIAL_GOOGLE'] = {
    'consumer_key': '989743370750-67nsgjpaojfbfdpd5fugrih9r8696buj.apps.googleusercontent.com',
    'consumer_secret': 's0BOlRGv9203qsXYNtB2rSbL'
}

# Initialize flask extensions.
db = MongoEngine(app)
api = Api(app)

# Create route views.
import cogindo.users
import cogindo.views
cogindo.views  # TODO: keep linter from complaining.
