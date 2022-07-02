from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from lib.modem import MB8600
import datetime


class DataSource(DataSourceBase):
  def __init__(self, config):
    self.config = config.mb8600_modem
    self.data = None
    if self.config is None:
        raise Exception('no configuration for mb8600_modem found')
  
  def get(self):
    modem_client = MB8600(
      self.config.host, 
      self.config.username, 
      self.config.password)
    self.data ,_d = modem_client.get_influx_data()

  def payloads(self):
    if self.data is None:
      self.get()
    return [ self.payload(d) for d in self.data ]
  
  def payload(self, data):
    return PAYLOAD_CLASS[data['measurement']](
       data['tags'], data['fields'], data['time'])
    

class MB8600DownstreamChannelPayload(DataPayload):
    def __init__(self, tags, fields, time):
        super().__init__(tags, fields)
        self.timestamp = datetime.datetime.fromisoformat(time)
        self.topic = ['downstream_channel', str(tags['Channel'])]
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<MB8600DownstreamChannelPayload {self.topic} SNR: {self.fields["SNR"]}>'

class MB8600UpstreamChannelPayload(DataPayload):
    def __init__(self, tags, fields, time):
        super().__init__(tags, fields)
        self.timestamp = datetime.datetime.fromisoformat(time)
        self.topic = ['upstream_channel', str(tags['Channel'])]
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<MB8600UpstreamChannelPayload {self.topic} SNR: {self.fields["PowerdBmV"]}>'

class MB8600InfoPayload(DataPayload):
    def __init__(self, tags, fields, time):
        super().__init__(tags, fields)
        self.timestamp = datetime.datetime.fromisoformat(time)
        self.topic = ['modem_info']
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<MB8600InfoPayload {self.topic}>'

class MB8600UptimePayload(DataPayload):
    def __init__(self, tags, fields, time):
        super().__init__(tags, fields)
        self.timestamp = datetime.datetime.fromisoformat(time)
        self.topic = ['modem_uptime']
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<MB8600UptimePayload {self.topic}>'

PAYLOAD_CLASS = {
  'downstream_channel': MB8600DownstreamChannelPayload,
  'upstream_channel': MB8600UpstreamChannelPayload,
  'modem_info': MB8600InfoPayload,
  'uptime': MB8600UptimePayload
}
