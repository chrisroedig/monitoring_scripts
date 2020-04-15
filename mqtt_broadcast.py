import paho.mqtt.publish as publish
import importlib
import sys
import config
import json

# instantiate the data_source
source_name = sys.argv[1]
source = importlib.import_module("sources."+source_name).DataSource(config.Config())

# grab the mqtt root topic
mqtt_host = config.Config().mqtt.host
root_topic = source.config.mqtt_topic

# get the array of data payloads
# iterate array and send mqtt messages
for payload in source.payloads():
    topic = '/'.join([root_topic, payload.topic])
    payload_json = json.dumps(payload.fields)
    publish.single(topic, payload=payload_json, hostname=mqtt_host)

