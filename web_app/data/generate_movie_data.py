# get film data from wikipedia

def get_film_names(url, year):
    
    import requests
    html_doc = requests.get(url).text

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')

    films = {}
    table_headers = soup.find_all("th", text="Opening" )

    for th in table_headers:
        table = th.parent.parent
        for tr in table.find_all('tr'):
            ind = 0
            for td in tr.find_all('td', rowspan=lambda x: x is None):
                if ind == 0:
                    film = td.find(text=True)
                    if film.parent.name == 'a':
                        film_id = '{0} ({1})'.format(film, year)
                        film_href = 'https://en.wikipedia.org' + film.parent['href']
                        films[film_id] = film_href
                ind += 1
    
    return films


years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']

with open('movies.dat', 'w') as fh:
    pass

film_id = 0
for year in years:
    films = (
        get_film_names(
            'https://en.wikipedia.org/wiki/{0}_in_film'.format(year), year
        )
    )
    with open('movies.dat'.format(year), 'a') as fh:
        for k, v in films.items():
            film_id += 1
            fh.write("{}::{}::{}\n".format(film_id, k, v))


# Make some fake ratings

num_users = 6000
num_ratings_per_user_min = 10
num_ratings_per_user_max = 100

min_movie_id = 1
max_movie_id = film_id


import hashlib
import re
import random

# generate biased ratings
def get_rating(film_id):
    h = hashlib.md5(str(film_id).encode('utf-8')).hexdigest()

    m = re.search("[012345]", h)
    digit = int(h[m.start()])
    if digit == 3:
        rating = random.randrange(1, 3)
    else:
        rating = random.randrange(3, 6)
    return rating



# ok, do it ...

import random

with open('ratings.dat', 'w') as file_handler:
    for user_id in range(1, num_users):
        
        movie_ids = [random.randrange(min_movie_id, max_movie_id) for _ in range(num_ratings_per_user_min, num_ratings_per_user_max)]

        user_bias = random.randrange(1, 100)
        
        for movie_id in movie_ids:
       
            if user_bias < 10:
                # 10% of users rate low
                rating = random.randrange(1, 3)

            elif user_bias >= 10 and user_bias < 20:
                # 10% of users rate high
                rating = random.randrange(3, 6)

            elif user_bias >= 20 and user_bias < 30:
                # 10% of users rate don't rate at all
                rating = -1

            else:
                # the rest rate according to taste
                rating = get_rating(movie_id)
           
            if rating > 0:
                file_handler.write("{}::{}::{}::N/A\n".format(
                        user_id, 
                        movie_id,
                        rating
                    ))


# In[ ]:



