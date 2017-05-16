from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask_sslify import SSLify
from flask_login import LoginManager
from flask_moment import Moment


app = Flask(__name__)

# see https://github.com/snowch/movie-recommender-demo/issues/2
app.session_cookie_name = 'JSESSIONID'

sslify = SSLify(app)
moment = Moment(app)

app.config.from_object('config.Config')

login_manager = LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)
moment = Moment(app)

from . import messagehub_client
from . import dao
from . import models
from . import views
from . import main
from . import auth


