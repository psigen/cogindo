from flask import Flask

from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'  # TODO: secure this

# Configure a database client.
app.config["MONGODB_SETTINGS"] = {"DB": "miridan",
                                  #"USERNAME": "my_user_name",
                                  #"PASSWORD": "my_secret_password",
                                  "HOST": "127.0.0.1", "PORT": 27017}

# Configure Google oauth login.
app.config['SECURITY_POST_LOGIN'] = '/profile'
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
