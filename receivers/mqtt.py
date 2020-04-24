from receivers.receiver import ReceiverBase
import paho.mqtt.publish as publish
import json


class Receiver(ReceiverBase):
    def __init__(self, config):
        self.config = config.mqtt

    def send(self, payload, source_config = None):
        topic = '/'.join([self.config.root_topic] + payload.topic)
        payload_json = json.dumps({
            "fields": payload.fields,
            "tags": payload.tags
            })
        publish.single(topic, payload=payload_json, hostname=self.config.host)
