import requests, json
import atexit

from . import app

CL_URL      = app.config['CL_URL']
CL_USER     = app.config['CL_USER']
CL_PASS     = app.config['CL_PASS']
CL_AUTH     = app.config['CL_AUTH']
CL_MOVIEDB  = app.config['CL_MOVIEDB']
CL_AUTHDB   = app.config['CL_AUTHDB']
CL_RATINGDB = app.config['CL_RATINGDB']

from cloudant.client import Cloudant
from cloudant.adapters import Replay429Adapter

cloudant_client = Cloudant(CL_USER, CL_PASS, url=CL_URL, adapter=Replay429Adapter(retries=10))
cloudant_client.connect()

@atexit.register
def python_shutting_down():
    print('Disconnecting cloudant client')
    cloudant_client.disconnect()




