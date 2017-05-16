from kafka import KafkaProducer
from kafka.errors import KafkaError
import ssl
import sys
import json

if len(sys.argv) != 2:
    sys.exit("Usage: ./send_message.py text_to_send")

with open('etc/vcap.json') as data_file:    
    mhProps = json.load(data_file)

bootstrap_servers = mhProps['kafka_brokers_sasl']
sasl_plain_username = mhProps['user']
sasl_plain_password = mhProps['password']
topic = mhProps['topic']

text_to_send = sys.argv[1].encode()


sasl_mechanism = 'PLAIN'
security_protocol = 'SASL_SSL'

# Create a new context using system defaults, disable all but TLS1.2
context = ssl.create_default_context()
context.options &= ssl.OP_NO_TLSv1
context.options &= ssl.OP_NO_TLSv1_1

producer = KafkaProducer(bootstrap_servers = bootstrap_servers,
                         sasl_plain_username = sasl_plain_username,
                         sasl_plain_password = sasl_plain_password,
                         security_protocol = security_protocol,
                         ssl_context = context,
                         sasl_mechanism = sasl_mechanism,
                         api_version=(0,10))

# Asynchronous by default
future = producer.send(topic, text_to_send)

try:
    record_metadata = future.get(timeout=10)
except KafkaError:
    log.exception()
    pass

# Successful result returns assigned partition and offset
print ('topic', record_metadata.topic)
print ('partition', record_metadata.partition)
print ('offset', record_metadata.offset)
