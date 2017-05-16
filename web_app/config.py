import os, json

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string' 
    PORT = os.getenv('PORT', '5000')

    vcap_services = os.getenv("VCAP_SERVICES")
    if not vcap_services:
        raise BaseException(
                'Environment variable VCAP_SERVICES was not found.\n' +
                'VCAP_SERVICES must exist and contain the contents of the bluemix vcap.json data.'
                )

    vcap = json.loads(vcap_services)

    # Cloudant details

    cloudant_credentials = vcap['cloudantNoSQLDB'][0]['credentials']

    CL_HOST = cloudant_credentials['host']
    CL_USER = cloudant_credentials['username']
    CL_PASS = cloudant_credentials['password']
    CL_URL  = cloudant_credentials['url']

    CL_AUTH = ( CL_USER, CL_PASS )

    CL_MOVIEDB  = 'moviedb'
    CL_AUTHDB   = 'authdb'
    CL_RATINGDB = 'ratingdb'
    CL_RECOMMENDDB = 'recommendationdb'

    # Redis details

    try:
        redis_credentials = vcap['compose-for-redis'][0]['credentials']
        REDIS_URI = redis_credentials['uri']
        REDIS_ENABLED = True
    except:
        REDIS_ENABLED = False
        print("Redis configuration not found in VCAP services. Running without Redis.")

    # Messagehub details
    
    try:
        messagehub_credentials = vcap['messagehub'][0]['credentials']
        MESSAGEHUB_ENABLED = True
        KAFKA_ADMIN_URL = messagehub_credentials['kafka_admin_url']
        KAFKA_API_KEY = messagehub_credentials['api_key']
        KAFKA_BROKERS_SASL = messagehub_credentials['kafka_brokers_sasl'] 
        KAFKA_USERNAME = messagehub_credentials['user'] 
        KAFKA_PASSWORD = messagehub_credentials['password']
        KAFKA_TOPIC = 'movie_ratings'
    except:
        MESSAGEHUB_ENABLED = False
        print("MessageHub configuration not found in VCAP services. Running without MessageHub.")

    # BigInsights details

    BI_HIVE_HOSTNAME = os.getenv("BI_HIVE_HOSTNAME")
    BI_HIVE_USERNAME = os.getenv("BI_HIVE_USERNAME")
    BI_HIVE_PASSWORD = os.getenv("BI_HIVE_PASSWORD")

    if BI_HIVE_HOSTNAME and BI_HIVE_USERNAME and BI_HIVE_PASSWORD:
        BI_HIVE_ENABLED = True
    else:
        print("BigInsights configuration not found in environement. Running without BigInsights.")
        BI_HIVE_ENABLED = False


    @staticmethod
    def init_app(app):
        pass
