import enlighten
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from datetime import datetime, timedelta

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.enphase_enlighten
        self.data = None
        if self.config is None:
            raise Exception('no configuration for enlighten found')
        self.client = enlighten.Client(
          persist_config=True,
          persist_session=True,
          session_file=self.config.session_file,
          config_file=self.config.config_file
        )
        self.time_delay = self.config._data.get('time_delay', 20)
        self.client.login(self.config.username, self.config.password)

    def get(self):
        self.time = datetime.now() - timedelta(minutes=self.time_delay)
        _t, self.powers = self.client.array_power(self.time)
        self.devices = self.client.device_index
      
    def payloads(self):
        self.get()
        return map(self.payload, enumerate(self.devices))

    def payload(self, device_id):
        i , device_id = device_id
        tags = {
          'device_id': device_id,
          'panel_number': i
        }
        fields = {
          'power' : self.powers[i]
        }
        return EnlightenPayload(tags, fields, self.time)

class EnlightenPayload(DataPayload):
    def __init__(self, tags, fields, timestamp):
        self.timestamp = timestamp
        self.topic = ['enlighten', 'device', tags['device_id']]
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<EnlightenPayload {self.topic} power: {self.fields["power"]}>'