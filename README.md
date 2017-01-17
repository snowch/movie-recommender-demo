## Overview

This project walks through how you can create recommendations using Apache Spark machine learning.  There are a number of jupyter notebooks that you can run on IBM Data Science Experience, and there a live demo of a movie recommendation web application you can interact with.

## Quick start

If you want to try out a live demo of the web application, visit [here](https://movie-recommend-demo.mybluemix.net/)

This project is a demo movie recommender application. This demo has been installed with approximately four thousand movies and one million ratings from the [MovieLens 1M Dataset](http://grouplens.org/datasets/movielens/1m/). The purpose of this web application is to allow users to search for movies, rate movies, and receive recommendations for movies based on their ratings.

## Notebooks

Start with [Step 00 - Project Overview](./Step 00 - Project Overview.ipynb) to read more about this project.

You can import these notebooks into IBM Data Science Experience.  I  have occasionally experienced issues when trying to load from a URL.  If that happens to you, try cloning or downloading this repo and importing the notebooks as files.

## Technologies

The technologies used in this demo are:

 - Python flask application
 - IBM Bluemix for hosting the web application and services
 - IBM Cloudant NoSQL for storing movies, ratings, user accounts and recommendations
 - IBM Compose Redis for maintaining an Atomic Increment counter for ID fields for user accounts
 - IBM Datascience Experience (DSX) and Spark as a Service for:
    - exploring data and analysing ratings
    - training and testing a recommendation model
    - retraining recommendation model hourly
    - generating recommendations and saving to Cloudant
 - IBM Datascience Experience (DSX) Github integration for saving notebooks
 
The overall architecture looks like this:

<p align="center">
<img alt="Overall Architecture" src="./docs/movie-recommender-demo.png" width="50%">
</p>

## Web application screenshots 

### Rating a movie

The screenshot below shows some movies being rated by a user.

![Screenshot of rating a movie](./docs/screenshot_ratings.png)

### Movie recommendations

The screenshot below shows movie recommendations provided by Spark machine learning.

![Screenshot of movie recommendations](./docs/screenshot_recommendations.png)

## Setting up your own demo web application instance on Bluemix

### Quick deploy

Click on this link, then follow the instructions.  Note that this step may take quite a long time (maybe 30 minutes).

[![Deploy to Bluemix](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/snowch/movie-recommender-demo.git)

An instance of Cloudant, Compose Redis and the Flask web application will be set up for you.

### Deploy using cf tools

See the instructions [here](https://github.com/snowch/movie-recommender-demo/blob/master/web_app/README.md)
