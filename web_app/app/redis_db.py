import requests, json
import atexit
import redis
from . import app

if app.config['REDIS_ENABLED'] == True:
    redis = redis.StrictRedis.from_url(app.config['REDIS_URI'])

def get_next_user_id():
    return redis.hincrby('app_ids', 'user_id')

def set_next_user_id(next_user_id):
    redis.hset("app_ids", "user_id", int(next_user_id))

@atexit.register
def python_shutting_down():
    print('Disconnecting redis client')
    # TODO




