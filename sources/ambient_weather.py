from ambient_api.ambientapi import AmbientAPI
import requests
import datetime
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.ambient
        self.data = None
        self.url = f'https://api.ambientweather.net/v1/devices/{self.config.mac_address}'
        if self.config is None:
            raise Exception('no configuration for ambient found')
    
    def get(self):
        params = {
            'apiKey': self.config.api_key,
            'applicationKey': self.config.application_key,
            'limit':1
            }
        resp = requests.get(self.url, params)
        self.data = resp.json()[0]
    
    def payloads(self):
        if self.data is None:
            self.get()
        topic = self.config.mac_address[-8:].replace(':','')    
        fields = {
            'wind_direction': self.data["winddir"],
            'wind_speed_mph': float(self.data["windspeedmph"]),
            'wind_gust_mph': float(self.data["windgustmph"]),
            'temp_f': float(self.data["tempf"]),
            'hourly_rain_in': float(self.data["hourlyrainin"]),
            'event_rain_in': float(self.data["eventrainin"]),
            'barometric_pressure_rel_in': float(self.data["baromrelin"]),
            'barometric_pressure_abs_in': float(self.data["baromabsin"]),
            'humidity': self.data["humidity"],
            'temp_indoor_f': float(self.data["tempinf"]),
            'humidity_indoor': self.data["humidityin"],
            'uv_index': self.data["uv"],
            'solar_flux': float(self.data["solarradiation"]),
            'apparent_temp_f': float(self.data["feelsLike"]),
            'dew_point_f': float(self.data["dewPoint"]),
            'timestamp_utc_ms': self.data["dateutc"]
        }
        tags = {
          'location': self.config.location_tag
        }
        return [AmbientWeatherPayload(topic, tags, fields)]


class AmbientWeatherPayload(DataPayload):
    def __repr__(self):
        return f'<AmbientWeatherPayload {self.topic} temp: {self.fields["temp_f"]}>'