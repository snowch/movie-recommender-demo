from flask.ext.script import Manager, Server
from app import app
import config
from db_setup import delete_dbs, create_dbs, populate_movie_db, populate_rating_db, create_moviedb_indexes, create_authdb_indexes, create_latest_recommendations_index, create_test_user

port = app.config['PORT']
server = Server(host="0.0.0.0", port=port)

manager = Manager(app)
manager.add_command("runserver", server)

@manager.command
def db_all():
    "Delete and recreate Cloudant databases"
    db_delete()
    db_setup()
    db_populate()
    create_test_user()

@manager.command
def db_delete():
    "Delete Cloudant databases"
    delete_dbs()

@manager.command
def db_setup():
    "Create Cloudant databases"
    create_dbs()
    create_moviedb_indexes()
    create_authdb_indexes()
    create_latest_recommendations_index()

@manager.command
def db_populate():
    "Populate Cloudant databases"
    populate_movie_db()
    populate_rating_db()

if app.debug:
    # debug routes
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, rule)

if __name__ == '__main__':
    manager.run()
