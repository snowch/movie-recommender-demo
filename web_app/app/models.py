from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import g, current_app, request, url_for, jsonify
from flask.json import JSONEncoder
from flask.ext.login import UserMixin, AnonymousUserMixin, current_user
import os, json
import requests
import time
import urllib
from . import app, login_manager
import collections
import numpy as np
from .dao import MovieDAO, RatingDAO, RecommendationDAO, UserDAO, RecommendationsNotGeneratedException, RecommendationsNotGeneratedForUserException
from . import messagehub_client


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Movie):
            return obj.as_dict()
        if isinstance(obj, Recommendation):
            return obj.as_dict()
        else:
            JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder


class Recommendation:

    def __init__(self, movie_id, movie_name, rating):
        self.movie_id = movie_id
        self.movie_name = movie_name
        self.rating = rating

    @staticmethod
    def get_latest_recommendation_timestamp():
        return RecommendationDAO.get_latest_recommendation_timestamp()

    @staticmethod
    def calculate_ratings(user_id, pf_keys, pf_vals):

        # See here for the rationale behind this approach:
        # http://stackoverflow.com/questions/41537470/als-model-how-to-generate-full-u-vt-v

        Vt = np.matrix(np.asarray(pf_vals))

        full_u = np.zeros(len(pf_keys))

        def set_rating(pf_keys, full_u, key, val):
            try:
                idx = pf_keys.index(key)
                full_u.itemset(idx, val)
            except ValueError:
                # the movie didn't have any ratings in when the model 
                # when the product features were create last time the 
                # model was trained
                pass
            except:
                import sys
                print("Unexpected error:", sys.exc_info()[0])

        for key, value in Rating.get_ratings(user_id).items():
            set_rating(pf_keys, full_u, key, value)

        recommendations = full_u*Vt*Vt.T

        ratings = list(np.sort(recommendations)[:,-10:].flat)
        ratings = [ str(r) for r in ratings ]

        movie_ids = np.where(recommendations >= np.sort(recommendations)[:,-10:].min())[1]
        movie_ids = [ int(m) for m in movie_ids ]

        return (ratings, movie_ids)


    @staticmethod
    def get_recommendations(user_id):

        ret = RecommendationDAO.get_recommendations_or_product_features(user_id)

        if ret['type'] == 'als_recommendations':

            movie_ids = list(ret['recommendations'].keys())
            ratings = list(ret['recommendations'].values())

            recommendation_type = "BATCH"
        else:
      
            pf_keys = ret['pf_keys']
            pf_vals = ret['pf_vals']
            
            ( ratings, movie_ids ) = Recommendation.calculate_ratings(
                                                                    user_id, 
                                                                    pf_keys, 
                                                                    pf_vals
                                                                    )
            recommendation_type = "REALTIME"

        # we have the movie_ids, let's get the movie names
        recommendations = [] 
        for movie_id, movie_name in MovieDAO.get_movie_names(movie_ids).items():
            rating = ratings[movie_ids.index(movie_id)]
            recommendation = Recommendation(movie_id, movie_name, rating)
            recommendations.append(recommendation)

        # sort by rating
        recommendations.sort(key=lambda r: r.rating, reverse=True)

        return (recommendation_type, recommendations)

    def as_dict(self):
        return dict(
                    movie_id = self.movie_id,
                    movie_name = self.movie_name,
                    rating = self.rating
                )

class Rating:

    @staticmethod
    def get_ratings(user_id):
        return RatingDAO.get_ratings(user_id)

    @staticmethod
    def save_rating(movie_id, user_id, rating):
        RatingDAO.save_rating(
                int(movie_id), user_id, rating
                )

        if app.config['MESSAGEHUB_ENABLED'] == True:
            message = '{0},{1},{2}'.format(user_id, movie_id, rating)
            messagehub_client.send_message( message )
            print('Sent message to MessageHub', message)

class Movie:

    def __init__(self, movie_id, name):
        self.movie_id = movie_id
        self.name = name 
        self.rating = None

    def as_dict(self):
        return dict(
                    movie_id = self.movie_id,
                    name = self.name,
                    rating = self.rating
                )
    
    def __repr__(self):
        return str(self.as_dict())

    @staticmethod
    def find_movies(user_id, search_string):

        movies_dict = MovieDAO.find_movies(search_string)

        # the DAO expects movie_ids to be integers
        movie_ids = [ int(m) for m in list(movies_dict.keys()) ]

        # we need to also get the user ratings
        movie_ratings = RatingDAO.get_ratings(user_id, movie_ids)

        # we need to get the user's rating for the movie if available
        movies = []
        for movie_id, movie_name in movies_dict.items():

            movie_id = int(movie_id)

            movie = Movie(
                        movie_id,
                        movie_name,
                        )

            # the user rated this movie
            if movie_id in movie_ratings:
                movie.rating = movie_ratings[movie_id]

            movies.append(movie)

        return movies


class User(UserMixin):

    id = ''
    email = ''
    password_hash = ''
    confirmed = False

    def __init__(self, id, email, password=None, password_hash=None):
        self.id = id 
        self.email = email
        if password_hash:
            self.password_hash = password_hash
        else:
            self.password_hash = generate_password_hash(password)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def email_is_registered(email):
        return User.find_by_email(email) is not None

    def __repr__(self):
        return '<User %r>' % self.email

    def save(self):

        if self.id != None:
            raise BaseException("Updating user account is not supported")

        user_id = UserDAO.create_user(
                                    self.email,
                                    self.password_hash
                                    )
        self.user_id = id

    @staticmethod
    def find_by_email(email):

        user_dict = UserDAO.find_by_email(email)

        if user_dict:
            return User(
                        user_dict['user_id'],
                        email,
                        password_hash=user_dict['password_hash']
                    )
        else:
            return None

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):

    user_dict = UserDAO.load_user(user_id)
    
    if user_dict:
        return User(
                    user_id,
                    user_dict['email'],
                    password_hash=user_dict['password_hash']
                )
    else:
        return None

