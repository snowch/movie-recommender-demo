from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask_sslify import SSLify
from flask_login import LoginManager
from flask_moment import Moment


app = Flask(__name__)
sslify = SSLify(app)
moment = Moment(app)

app.config.from_object('config.Config')

login_manager = LoginManager()
login_manager.init_app(app)

bootstrap = Bootstrap(app)
moment = Moment(app)

from . import dao
from . import models
from . import views
from . import main
from . import auth


