from ambient_api.ambientapi import AmbientAPI
import data_client
import config
import requests
import datetime

cfg = config.Config()
dc = data_client.DataClient(database=cfg.ambient.influx_database)
acfg = cfg.ambient
url = f'https://api.ambientweather.net/v1/devices/{acfg.mac_address}'

params = {
    'apiKey': acfg.api_key,
    'applicationKey': acfg.application_key,
    'limit':1
    }
resp = requests.get(url, params)
data = resp.json()[0]
timestamp = datetime.datetime.fromtimestamp(data["dateutc"]/(1e3))

weather_fields = {
    'wind_direction': data["winddir"],
    'wind_speed_mph': data["windspeedmph"],
    'wind_gust_mph': data["windgustmph"],
    'temp_f': data["tempf"],
    'hourly_rain_in': data["hourlyrainin"],
    'event_rain_in': data["eventrainin"],
    'barometric_pressure_rel_in': data["baromrelin"],
    'barometric_pressure_abs_in': data["baromabsin"],
    'humidity': data["humidity"],
    'temp_indoor_f': data["tempinf"],
    'humidity_indoor': data["humidityin"],
    'uv_index': data["uv"],
    'solar_flux': data["solarradiation"],
    'apparent_temp_f': data["feelsLike"],
    'dew_point_f': data["dewPoint"]
}

tags = {
    'location': acfg.location_tag
}

dc.write('weather_station_data', fields=weather_fields, tags=tags)
