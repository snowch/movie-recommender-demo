### Manual Setup

#### Prerequisites

- Cloud Foundry CLI installed: https://console.ng.bluemix.net/docs/starters/install_cli.html
- Local python version must be 3.5.x.  Older python versions will not work.
- Virtualenv installed
- Linux/OS X are recommended for your local development environment.

#### Setup the source code

```
git clone https://github.com/snowch/movie-recommender-demo
cd movie-recommender-demo/web_app
virtualenv venv --python=python3.5 
source venv/bin/activate
pip3.5 install -r requirements.txt
```

#### Configure Cloudant

 - Create a Cloudant service in Bluemix.
 - Create the file web_app/etc/cloudant_vcap.json (see [web_app/etc/cloudant_vcap.json_template](./web_app/etc/cloudant_vcap.json_template) for an example)
 
#### Configure Message Hub (optional)
 
 - Create a MessageHub service in Bluemix.
 - Create the file web_app/etc/messagehub_vcap.json (see [web_app/etc/messagehub_vcap.json_template](./web_app/etc/messagehub_vcap.json_template) for an example)
 - Edit manifest.yml to uncomment the messagehub configuration
 - When the web application gets deployed, a topic 'movie_ratings' will be created for you
 
#### Configure Redis (optional)
 
 - Create a Redis service in Bluemix.
 - Create the file web_app/etc/redis_vcap.json (see [web_app/etc/redis_vcap.json_template](./web_app/etc/redis_vcap.json_template) for an example)
 - Edit manifest.yml to uncomment the redis configuration
 
#### Configure BigInsights (optional)
 
 - Create a BigInsights Basic service in Bluemix.  Ensure you select Hive and Spark as optional components.
 - Create the file hdp_app/etc/vcap.json with your Message Hub details (see [hdp_app/etc/vcap.json_template](./hdp_app/etc/vcap.json_template) for an example)
 - Create the file hdp_app/etc/bi_connection.properties with your BigInsight details (see [hdp_app/etc/bi_connection.properties_template](./hdp_app/etc/bi_connection.properties_template) for an example)
 - Follow the steps in the [README](./hdp_app/README.md) to build and deploy the spark code


#### Setup the Cloudant databases

This only needs to be performed once.

```
cd web_app
./run.sh db_all
```

If you want to use BigInsights:
```
cf set-env movie-recommend-demo BI_HIVE_USERNAME changeme
cf set-env movie-recommend-demo BI_HIVE_PASSWORD changeme
cf set-env movie-recommend-demo BI_HIVE_HOSTNAME changeme
cf restage movie-recommend-demo
```

### Run web_app locally

```
cd web_app
./run.sh
```

You should see a URL output:

```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Open this to try out the webapp locally.

### Push web_app to bluemix

 - edit manifest.yml
   - provide a unique host
   - change the name of the services to reflect
     - your cloudant service name
     - your redis service name
     - your message hub service name

Then run the following commands:

```
# change directory to the folder with manifest.yml

cd ..

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
   - upload the [Step 06 - Install Spark Cloudant](../notebooks/Step 06 - Install Spark Cloudant.ipynb) notebook to DSX
   - run the `Step 06 - Install Cloudant Python` notebook 
   - upload the [Step 07 - Cloudant Datastore Recommender](../notebooks/Step 07 - Cloudant Datastore Recommender.ipynb) notebook to DSX
   - follow the instructions in the notebook to setup the cloudant_credentials.json file
   - click: Cell -> run all
 - when finished, navigate back to the web application and click on 'Get Recommendations'
 - if recommendations were generated without error:
    - save a new version of the notebook: File -> Save Version
    - setup a DSX schedule job to run the version every hour

