import influx_client
import requests

# TODO: refactor this...
# cfg = config.Config()
# dc = data_client.DataClient(database=cfg.darksky.influx_database)

# def request_weather():
#   url = "https://api.darksky.net/forecast/{}/{},{}".format(
#     cfg.darksky.api_key, cfg.darksky.latitude, cfg.darksky.longitude)
#   resp = requests.get(url)
#   if resp.status_code!= 200:
#     return {}
#   try:
#     return resp.json()['currently']
#   except:
#     raise Exception(resp.text)

# wdata = request_weather()
# weather_fields = {
#  'apparent_temp' : float(wdata['apparentTemperature']),
#  'cloud_cover' : float(wdata['cloudCover']),
#  'due_point' : float(wdata['dewPoint']),
#  'humidity' : float(wdata['humidity']),
#  'ozone' : float(wdata['ozone']),
#  'precip_intensity' : float(wdata['precipIntensity']),
#  'precip_probability' : float(wdata['precipProbability']),
#  'pressure' : float(wdata['pressure']),
#  'temp' : float(wdata['temperature']),
#  'uv_index' : float(wdata['uvIndex']),
#  'visibility' : float(wdata['visibility']),
#  'wind_bearing' : float(wdata['windBearing']),
#  'wind_gust' : float(wdata['windGust']),
#  'wind_speed' : float(wdata['windSpeed'])
# }

# tags = {
#     'location': '395_riley'
# }

# dc.write('weather_report', fields=weather_fields, tags=tags)
