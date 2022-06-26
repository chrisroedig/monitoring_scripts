import requests
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from datetime import datetime

class DataSource(DataSourceBase):
  def __init__(self, config):
    self.config = config.http_check
    self.data = None
    if self.config is None:
        raise Exception('no configuration for http_check found')
  
  def get(self):
    self.data = requests.get(self.config.url)

  def payload(self):
    if self.data is None:
      self.get()
    fields = {
      'status_code': self.data.status_code,
      'success': int(self.data.ok),
      'latency': self.data.elapsed.total_seconds()
    }
    tags = { 'location': self.config.location_tag }
    return HttpCheckPayload(tags, fields)
  
  def payloads(self):
    if self.data is None:
      self.get()
    return [
      self.payload()
    ]

class HttpCheckPayload(DataPayload):
  def __init__(self, tags, fields):
    super().__init__(tags, fields)
    self.topic = ['http_check']
    self.tags = tags
    self.fields = fields
  def __repr__(self):
    return f'<HttpCheckPayload {self.topic} ☑️ {self.fields["success"]} ⏱ {self.fields["latency"]}s >'

  