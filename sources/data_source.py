class DataSourceBase():
    def __init__(self, config):
        self.config = config
        pass
    def payloads(self):
        return []

class DataPayload():
    def __init__(self, topic, tags, fields):
        self.topic = topic
        self.tags = tags
        self.fields = fields
    
    def __repr__(self):
        return f'<DataPayload {self.topic} >'