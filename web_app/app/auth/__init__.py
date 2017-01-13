from flask import Blueprint
from .. import app

auth = Blueprint('auth', __name__, url_prefix='/auth')

from . import views
from . import forms

app.register_blueprint(auth)

