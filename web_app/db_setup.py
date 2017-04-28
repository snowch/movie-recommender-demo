import requests, json
import os.path

from app import app
from app.cloudant_db import cloudant_client
from app.redis_db import set_next_user_id
from app import models

from cloudant.design_document import DesignDocument
from cloudant.security_document import SecurityDocument
from requests.exceptions import HTTPError

CL_URL      = app.config['CL_URL']
CL_AUTH     = app.config['CL_AUTH']
CL_MOVIEDB  = app.config['CL_MOVIEDB']
CL_AUTHDB   = app.config['CL_AUTHDB']
CL_RATINGDB = app.config['CL_RATINGDB']
CL_RECOMMENDDB = app.config['CL_RECOMMENDDB']

CL_DBS = [ CL_MOVIEDB, CL_AUTHDB, CL_RATINGDB, CL_RECOMMENDDB ]


# TODO use flask logging rather than print()

def dbs_exist():

    dbs = cloudant_client.all_dbs()
    for db in CL_DBS:
        if db not in dbs:
            print('Database not found', db)
            return False

    return True

def delete_dbs():

    dbs = cloudant_client.all_dbs()
    for db in CL_DBS:
        if db in dbs:
            print('Deleting database', db)
            cloudant_client.delete_database(db)

def create_dbs():

    dbs = cloudant_client.all_dbs()
    for db in CL_DBS:
        if db in dbs:
            print('Found database', db)
        else:
            db_handle = cloudant_client.create_database(db)
            if db_handle.exists():
                print('Created database', db)
       
                # Make all dbs except for the Authentication DB readable by everyone
                if not db == CL_AUTHDB:
                    print('Making {0} database readable by everyone'.format(db))

                    with SecurityDocument(db_handle) as security_document:
                        security_document.update({'cloudant': {'nobody': ['_reader']}})

            else:
                print('Problem creating database', db)

def md5(fname):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def populate_movie_db():

    movie_file = 'data/movies.dat'
    
    movie_db = cloudant_client[CL_MOVIEDB]

    bulk_docs = []
    with open(movie_file, 'r', encoding='ISO-8859-1') as f:
        for line in f:
            (movieid, moviename, url) = line.strip().split('::')

            bulk_docs.append({
                '_id': movieid,
                'name': moviename,
                'url': url
                })

    resp = movie_db.bulk_docs(bulk_docs)
    num_ok = len([ r['ok'] for r in resp if 'ok' in r ])
    print('num saved: ', num_ok)

def populate_rating_db():

    rating_file = 'data/ratings.dat'
    
    rating_db = cloudant_client[CL_RATINGDB]

    max_user_id = 0
    chunk = 0
    bulk_docs = []
    with open(rating_file, 'r', encoding='ISO-8859-1') as f:
        while True:
            line = f.readline().strip()

            if not line == '':
                (user_id, movie_id, rating, timestamp) = line.split('::')

                user_id = int(user_id)

                if user_id > max_user_id:
                    max_user_id = user_id
                
                bulk_docs.append({
                    '_id': "user_{0}/movie_{1}".format(user_id, movie_id),
                    'rating': rating,
                    'timestamp': timestamp
                    })
                chunk = chunk + 1

                # max request size is 1MB - we need to ensure chunks are 
                # smaller than this, 10000 docs was chosen arbitrarily and
                # seems to be ok

                if chunk % 10000 == 0:
                    resp = rating_db.bulk_docs(bulk_docs)
                    num_ok = len([ r['ok'] for r in resp if 'ok' in r ])
                    print('chunk: ', chunk, ' num saved: ', num_ok)
                    bulk_docs = []

                # uncomment to only load 10000 ratings 
                #if chunk % 50000 == 0:
                #    break
            else:
                break

    if app.config['REDIS_ENABLED'] == True:
        set_next_user_id(max_user_id + 1)

def create_latest_recommendations_index():

    ddoc_fn = '''
function(doc) {
  emit([doc.user, doc.timestamp], null);
}
'''    
    db = cloudant_client[CL_RECOMMENDDB]
    index_name = 'latest-recommendation-index'

    ddoc = DesignDocument(db, index_name)
    if ddoc.exists():
        ddoc.fetch()
        ddoc.update_view(index_name, ddoc_fn)
        print('updated', index_name)
    else:
        ddoc.add_view(index_name, ddoc_fn)
        print('created', index_name)
    ddoc.save()

def create_moviedb_indexes():

    ddoc_fn = '''
function(doc){
  index("default", doc._id);
  if (doc.name){
    index("name", doc.name, {"store": true});
  }
}
'''    
    db = cloudant_client[CL_MOVIEDB]
    index_name = 'movie-search-index'

    ddoc = DesignDocument(db, index_name)
    if ddoc.exists():
        ddoc.fetch()
        ddoc.update_search_index(index_name, ddoc_fn, analyzer=None)
        print('updated', index_name)
    else:
        ddoc.add_search_index(index_name, ddoc_fn, analyzer=None)
        print('created', index_name)
    ddoc.save()

    # Test the index

    # end_point = '{0}/{1}/_design/{2}/_search/{2}'.format ( CL_URL, CL_MOVIEDB, index_name )
    # data = {
    #     "q": "name:Toy Story",
    #     "sort": "foo",
    #     "limit": 3
    # }
    # headers = { "Content-Type": "application/json" }
    # response = cloudant_client.r_session.post(end_point, data=json.dumps(data), headers=headers)
    # print(response.json())

def create_authdb_indexes():

    db = cloudant_client[CL_AUTHDB]

    ddoc_fn = '''
function(doc){
  if (doc.email) {
    emit(doc.email);
  }
}
'''    
    view_name = 'authdb-email-index'

    ddoc = DesignDocument(db, view_name)
    if ddoc.exists():
        ddoc.fetch()
        ddoc.update_view(view_name, ddoc_fn)
        print('updated', view_name)
    else:
        ddoc.add_view(view_name, ddoc_fn)
        print('created', view_name)
    ddoc.save()

    # Test the index

    # import urllib
    # key = urllib.parse.quote_plus('a@a.com')

    # end_point = '{0}/{1}/_design/{2}/_view/{2}?key="{3}"'.format ( CL_URL, CL_AUTHDB, view_name, key )
    # response = cloudant_client.r_session.get(end_point)
    # print(response.json())


def create_test_user():
    user = models.User(None, 'a@a.com', 'a')
    user.save()
