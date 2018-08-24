import data_client
import config
import requests

cfg = config.Config()
dc = data_client.DataClient(database=cfg.darksky.influx_database)

def request_weather():
  url = "https://api.darksky.net/forecast/{}/{},{}".format(
    cfg.darksky.api_key, cfg.darksky.latitude, cfg.darksky.longitude)
  resp = requests.get(url)
  if resp.status_code!= 200:
    return {}
  try:
    return resp.json()['currently']
  except:
    raise Exception(resp.text)

wdata = request_weather()
weather_fields = {
 'apparent_temp' : wdata['apparentTemperature'],
 'cloud_cover' : wdata['cloudCover'],
 'due_point' : wdata['dewPoint'],
 'humidity' : wdata['humidity'],
 'storm_bearing' : wdata['nearestStormBearing'],
 'storm_distance' : wdata['nearestStormDistance'],
 'ozone' : wdata['ozone'],
 'precip_intensity' : wdata['precipIntensity'],
 'precip_probability' : wdata['precipProbability'],
 'pressure' : wdata['pressure'],
 'temp' : wdata['temperature'],
 'uv_index' : wdata['uvIndex'],
 'visibility' : wdata['visibility'],
 'wind_bearing' : wdata['windBearing'],
 'wind_gust' : wdata['windGust'],
 'wind_speed' : wdata['windSpeed']
}

tags = {
    'location': '395_riley'
}
dc.write('weather_report', fields=weather_fields, tags=tags)
