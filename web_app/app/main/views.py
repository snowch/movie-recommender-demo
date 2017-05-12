from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user
from . import forms
from . import main 
from .. import app
from ..models import Movie, Recommendation, Rating
from ..dao import RecommendationsNotGeneratedException, RecommendationsNotGeneratedForUserException

import flask
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8


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


@main.route("/report")
def report():

    # TODO move Hive code to a new file hive_dao.py

    from . import app

    if not app.config['BI_HIVE_ENABLED']:
        return render_template('/main/bi_not_enabled.html')

    BI_HIVE_HOSTNAME = app.config['BI_HIVE_HOSTNAME']
    BI_HIVE_USERNAME = app.config['BI_HIVE_USERNAME']
    BI_HIVE_PASSWORD = app.config['BI_HIVE_PASSWORD']

    from impala.dbapi import connect 
    from impala.util import as_pandas

    # TODO probably want to cache the connection rather than
    # instantiate it on every request
    
    # Note that BigInsights Enterprise clusters will need to specify the
    # ssl certificate because it is self-signed.

    conn = connect(
                host=BI_HIVE_HOSTNAME,
                port=10000, 
                use_ssl=True, 
                auth_mechanism='PLAIN', 
                user=BI_HIVE_USERNAME, 
                password=BI_HIVE_PASSWORD
                )

    cursor = conn.cursor()

    # FIXME we probably want to create aggregates on hadoop
    #       and cache them rather than returning the whole data
    #       set here
    cursor.execute(
            'select * from movie_ratings', 
            configuration={ 
                'hive.mapred.supports.subdirectories': 'true', 
                'mapred.input.dir.recursive': 'true' 
                })

    df = as_pandas(cursor)

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


