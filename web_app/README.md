### Setup

#### Prerequisites

- Cloud Foundry CLI installed: https://console.ng.bluemix.net/docs/starters/install_cli.html
- Local python version must be 3.5.x.  Older python versions will not work.
- Linux/OS X are recommended for your local development environment.

#### Setup the source code

```
git clone https://github.com/snowch/demo_2710
cd demo_2710/web_app
source venv/bin/activate
pip3.5 install -r requirements.txt
```

#### Configure Cloudant and Redis

 - Create a Cloudant and Redis service in Bluemix.
 - Create the file etc/cloudant_vcap.json (see cloudant_vcap.json_template)
 - Create the file etc/redis_vcap.json (see redis.json_template)


#### Setup the databases

```
./run.sh db_all
```

### Run locally

```
./run.sh
```

You should see a URL output:

```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Open this to try out the webapp locally.

### Push to bluemix

 - edit manifest.yml
   - provide a unique host
   - change the name of the services to reflect
     - your cloudant service name
     - your redis service name

Then run:

```
# When you login, you will be prompted to select the space and org.
# ensure you choose the space/org where you created your Cloudant 
# service and Redis service 

cf login ...

# verify that cf is pointing at the right space/org

cf target

# you can now push the web app to Bluemix

cf push
```

### To create recommendations

 - create an account in the webapp
 - rate some movies
 - create a new DSX project, then
   - upload the Install spark-cloudant 1.6.4 lib.ipynb notebook
   - run the Install spark-cloudant 1.6.4 lib.ipynb notebook 
   - upload the Cloudant+Recommender+Pyspark.ipynb notebook
   - follow the instructions in the notebook to setup the cloudant_credentials.json file
   - click: Cell -> run all
 - when finished, navigate back to the web application and click on 'Get Recommendations'
 - if recommendations were generated without error:
    - save a new version of the notebook: File -> Save Version
    - setup a DSX schedule job to run the version every hour

### Developing

You can run python code from the python REPL, e.g.


```
$ cd web_app
$ source venv/bin/activate
$ source set_vcap.sh
$ python3.5
>>> from app import app
>>> from app.dao import MovieDAO
>>> MovieDAO.get_movie_names([1,2,3])
{1: 'Toy Story (1995)', 2: 'Jumanji (1995)', 3: 'Grumpier Old Men (1995)'}
>>>
```
