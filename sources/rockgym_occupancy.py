import requests
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from datetime import datetime
import re as reg

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.rockgym_occupancy
        self.data = None
        if self.config is None:
            raise Exception('no configuration for rockgym found')
    
    def get(self):
        r = requests.get(self.config.iframe_url, verify=False)
        raw_data = r.text.encode('utf-8').decode('unicode_escape')
        self.data = {
            'count': reg.search("\\\'count\\\' : (.*),", raw_data)[1],
            'capacity': reg.search("\\\'capacity\\\' : (.*),", raw_data)[1]
        }

    def payload(self):
        fields = self.data
        tags = {}
        return RockgymOccupancyPayload(tags, fields)
    
    def payloads(self):
        if self.data is None:
            self.get()
        return [
            self.payload()
        ]

class RockgymOccupancyPayload(DataPayload):
    def __init__(self, tags, fields):
        self.topic = ['rockgym_occupancy']
        self.tags = tags
        self.fields = fields
        self.timestamp = datetime.now()
    def __repr__(self):
        return f'<RockgymOccupancyPayload {self.topic} count/cap: {self.fields["count"]}/{self.fields["capacity"]}>'