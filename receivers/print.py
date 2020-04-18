from receivers.receiver import ReceiverBase
import json


class Receiver(ReceiverBase):
    def __init__(self, config):
        self.config = config.mqtt

    def send(self, payload, source_config = None):
        topic_str = '|'.join(payload.topic)
        print(f'[ {topic_str} ]: {payload}')
