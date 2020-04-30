from datetime import datetime
class DataSourceBase():
    def __init__(self, config):
        self.config = config
        pass
    def payloads(self):
        return []

class DataPayload():
    def __init__(self, tags, fields, timestamp=None):
        if timestamp is None:
            self.timestamp = datetime.now()
        self.topic = __class__.__name__.lower()
        self.tags = tags
        self.fields = fields
    
    def __repr__(self):
        return f'<DataPayload {self.topic} >'