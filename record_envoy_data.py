import data_client
import config
import requests

cfg = config.Config()
dc = data_client.DataClient(database=cfg.envoy.influx_database)

data = requests.get('http://'+cfg.envoy.host_url+'/production.json').json()

consumption_data = data['consumption'][0]
consumption_fields = {
    'power': consumption_data['wNow'],
    'rms_current': consumption_data['rmsCurrent'],
    'rms_voltage':consumption_data['rmsVoltage'],
    'reactive_power':consumption_data['reactPwr'],
    'apparent_power':consumption_data['apprntPwr'],
    'power_factor':consumption_data['pwrFactor']
}
dc.write('iq_envoy_consumption', consumption_fields)

production_data = data['production'][1]
production_fields = {
    'power': production_data['wNow'],
    'rms_current': production_data['rmsCurrent'],
    'rms_voltage':production_data['rmsVoltage'],
    'reactive_power':production_data['reactPwr'],
    'apparent_power':production_data['apprntPwr'],
    'power_factor':production_data['pwrFactor']
}

dc.write('iq_envoy_production', production_fields)
