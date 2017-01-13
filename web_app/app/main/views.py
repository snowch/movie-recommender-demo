from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask.ext.login import login_required, current_user
from . import forms
from . import main 
from .. import app
from ..models import Movie, Recommendation, Rating
from ..dao import RecommendationsNotGeneratedException, RecommendationsNotGeneratedForUserException

@main.route('/home', methods=['GET'])
def home():

    session['search_string'] = None
    session['movies'] = []

    return render_template('/main/index.html', 
            name = session.get('search_string'),
            movies = session.get('movies'))


@main.route('/', methods=['GET', 'POST'])
def index():

    search_string = session.get('search_string') 
    if search_string:
        session['movies'] = Movie.find_movies(
                                        current_user.get_id(),
                                        session.get('search_string')
                                        )
    else:
        session['movies'] = []

    return render_template('/main/index.html', 
            name = search_string,
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

@main.route('/set_search_string', methods=['POST'])
def set_search_string():
    form = forms.SearchForm()
    session['search_string'] = form.search_string.data
    return redirect(url_for('main.index'))

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
