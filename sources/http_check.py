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
    self.data = {
        'status_code': 0,
        'latency': float(self.config.timeout),
        'success': 0,
      }
    try:
      resp = requests.get(self.config.url, timeout=self.config.timeout)
      self.data = {
        'status_code': resp.status_code,
        'latency': resp.elapsed.total_seconds(),
        'success': int(resp.ok)
      }
    except requests.exceptions.Timeout as e:
      print(f'HTTP Check timeout')
    except requests.exceptions.ConnectionError as e:
      print(f'HTTP Check conection error')
    except Exception as e:
      print(f'HTTP Check exception: {e}')


  def payload(self):
    if self.data is None:
      self.get()
    fields = self.data
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

  