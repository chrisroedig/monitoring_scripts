import requests
from datetime import datetime
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload

# NOTE: alternative source weatherbit.io

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.darksky
        self.data = None
        if self.config is None:
            raise Exception('no configuration for ambient found')
        self.url = "https://api.darksky.net/forecast/{}/{},{}".format(
            self.config.api_key, self.config.latitude, self.config.longitude)
        self.data = None

    def get(self):
        resp = requests.get(self.url, verify=False)
        if resp.status_code!= 200:
            return False
        try:
            self.data = resp.json()['currently']
            return True
        except:
            print(resp.text)
            return False

    def payloads(self):
        return [ self.payload() ]
    
    def payload(self):
        if self.data is None:
            self.get()
        fields = {
            'apparent_temp' : float(self.data['apparentTemperature']),
            'cloud_cover' : float(self.data['cloudCover']),
            'due_point' : float(self.data['dewPoint']),
            'humidity' : float(self.data['humidity']),
            'ozone' : float(self.data['ozone']),
            'precip_intensity' : float(self.data['precipIntensity']),
            'precip_probability' : float(self.data['precipProbability']),
            'pressure' : float(self.data['pressure']),
            'temp' : float(self.data['temperature']),
            'uv_index' : float(self.data['uvIndex']),
            'visibility' : float(self.data['visibility']),
            'wind_bearing' : float(self.data['windBearing']),
            'wind_gust' : float(self.data['windGust']),
            'wind_speed' : float(self.data['windSpeed'])
        }
        tags = {}
        return DarkskyPayload(tags, fields)

class DarkskyPayload(DataPayload):
    def __init__(self, tags, fields):
        super().__init__(tags, fields)
        self.topic = [ 'weather_report' ]
        self.tags = tags
        self.fields = fields

    def __repr__(self):
        return f'<DarkskyPayload {self.topic} temp: {self.fields["apparent_temp"]}>'
