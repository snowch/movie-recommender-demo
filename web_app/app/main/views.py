try:
    import impyla 
except ImportError:
    print("Installing missing impyla")
    import pip
    pip.main(['install', '--no-deps', 'impyla'])

try:
    import thrift_sasl
except ImportError:
    print("Installing missing thrift_sasl")
    import pip
    # need a patched version of thrift_sasl.  see https://github.com/cloudera/impyla/issues/238
    pip.main(['install', '--no-deps', 'git+https://github.com/snowch/thrift_sasl'])



from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user
from . import forms
from . import main 
from .. import app
#from . import app

from ..models import Movie, Recommendation, Rating, User
from ..dao import RecommendationsNotGeneratedException, RecommendationsNotGeneratedForUserException

import flask
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

from impala.dbapi import connect 
from impala.util import as_pandas
from .. import messagehub_client
import time
import json

@main.route('/', methods=['GET'])
def index():

    return render_template('/main/home.html', 
            movies = session.get('movies'))


@main.route('/recommendations', methods=['GET', 'POST'])
def recommendations():

    user_id = current_user.get_id()

    if not user_id:
        flash('Recommendations are only available if you have an account.') 
        return render_template('/main/recommendations.html', recommendations=[])

    else:
        rated_movies = Rating.get_ratings(current_user.get_id())

        # the user needs to have rated some movies to be able to receive recommendations
        if len(rated_movies.keys()) == 0 and current_user.get_id():
            flash('No Recommendations found, please rate some movies.') 
            return render_template('/main/recommendations.html', recommendations=[], timestamp=None)

        try:
            timestamp = Recommendation.get_latest_recommendation_timestamp()
            (recommendation_type, recommendations) = \
                    Recommendation.get_recommendations(current_user.get_id())

        except RecommendationsNotGeneratedException:
            flash('No recommendations available - the Recommendation process has not run yet.') 
            return render_template('/main/recommendations.html', recommendations=[])
        except RecommendationsNotGeneratedForUserException:
            flash('No Recommendations found, please rate some movies.') 
            return render_template('/main/recommendations.html', recommendations=[], timestamp=timestamp)

        if recommendation_type:
            flash("Recommendation type: " + recommendation_type)

        return render_template('/main/recommendations.html', recommendations=recommendations, timestamp=timestamp)

@main.route('/search', methods=['POST'])
def search():
    form = forms.SearchForm()
    session['search_string'] = form.search_string.data

    search_string = session.get('search_string') 
    if search_string:
        search_string = search_string.strip()
        session['movies'] = Movie.find_movies(
                                        current_user.get_id(),
                                        session.get('search_string')
                                        )
    else:
        session['movies'] = []

    return render_template('/main/search_results.html', 
            search_string = search_string,
            movies = session.get('movies'))

@main.route('/set_rating', methods=['POST'])
@login_required
def set_rating():

    if not request.json or \
       not 'movie_id' in request.json or \
       not 'user_id' in request.json or \
       not 'rating' in request.json:
        abort(400)

    movie_id = request.json['movie_id']
    user_id  = request.json['user_id']
    rating   = request.json['rating']

    if rating == '-':
        Rating.save_rating(movie_id, user_id, None)
    else:
        Rating.save_rating(movie_id, user_id, int(rating))

    return('{ "success": "true" }')

def get_hive_cursor():

    # TODO move Hive code to a new file hive_dao.py

    if not app.config['BI_HIVE_ENABLED']:
        return render_template('/main/bi_not_enabled.html')

    BI_HIVE_HOSTNAME = app.config['BI_HIVE_HOSTNAME']
    BI_HIVE_USERNAME = app.config['BI_HIVE_USERNAME']
    BI_HIVE_PASSWORD = app.config['BI_HIVE_PASSWORD']


    # TODO probably want to cache the connection rather than
    # instantiate it on every request
    
    # Note that BigInsights Enterprise clusters will need to specify the
    # ssl certificate because it is self-signed.

    try:
        conn = connect(
                    host=BI_HIVE_HOSTNAME,
                    port=10000, 
                    use_ssl=True, 
                    auth_mechanism='PLAIN', 
                    user=BI_HIVE_USERNAME, 
                    password=BI_HIVE_PASSWORD
                    )
    except:
        return None

    return conn.cursor()

@main.route("/report")
def report():

    cursor = get_hive_cursor()

    if cursor is None:
        return render_template('/main/bi_connection_issue.html')

    # FIXME we probably want to create aggregates on hadoop
    #       and cache them rather than returning the whole data
    #       set here

    # we need to ignore monitoring pings which have rating user_id = -1 
    # and movie_id = -1
    try:
        cursor.execute(
            "select * from movie_ratings where customer_id <> '-1' and movie_id <> '-1'", 
            configuration={ 
                'hive.mapred.supports.subdirectories': 'true', 
                'mapred.input.dir.recursive': 'true' 
                })
    except:
        return render_template('/main/bi_connection_issue.html')

    df = as_pandas(cursor)
    
    count = df.shape[0]

    if count == 0:
       return render_template('/main/bi_no_records.html')

    from bokeh.charts import Bar, output_file, show

    fig = Bar(
            df,
            label='movie_ratings.rating',
            values='movie_ratings.rating',
            agg='count',
            title='Distribution of movie ratings',
            legend=False
            )


    fig.plot_height = 400
    fig.xaxis.axis_label = 'Rating'
    fig.yaxis.axis_label = 'Count ( Rating )'

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components(fig)
    html = flask.render_template(
        '/main/embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)

def check_auth(username, password):

    user = User.find_by_email(username)

    if user is not None and user.verify_password(password):
        return True
    else:
        return False

# This method keeps a thread open for a long time which is
# not ideal, but is the simplest way of checking.

@main.route("/monitor")
def monitor():

    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        data = { "error": "Permission denied." }
        response = app.response_class(
            response=json.dumps(data),
            status=550,
            mimetype='application/json'
        )
        return response

    cursor = get_hive_cursor()

    if cursor is None:
        data = { "error": "Could not connect to Hive" }
        response = app.response_class(
            response=json.dumps(data),
            status=500,
            mimetype='application/json'
        )
        return response

    timestamp = time.time()

    message = '{0},{1},{2}'.format(-1, -1, timestamp)
    messagehub_client.send_message( message ) 

    time.sleep(70)

    cursor.execute(
            'select * from movie_ratings where rating = {0}'.format(timestamp), 
            configuration={ 
                'hive.mapred.supports.subdirectories': 'true', 
                'mapred.input.dir.recursive': 'true' 
                })
    df = as_pandas(cursor)
    count = df.shape[0]

    if count == 1:
        data = { "ok": "App rating found in hadoop." }
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        data = { "error": "App rating not found in hadoop." }
        response = app.response_class(
            response=json.dumps(data),
            status=500,
            mimetype='application/json'
        )
        return response
