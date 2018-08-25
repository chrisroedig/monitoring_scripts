import data_client
import config
import requests

cfg = config.Config()
old_dc = data_client.DataClient(database=cfg.influxdb.database)
dc = data_client.DataClient(database=cfg.envoy.influx_database)

data = requests.get('http://'+cfg.envoy.host_url+'/production.json').json()

consumption_data = data['consumption'][0]
consumption_fields = {
    'power': consumption_data['wNow'],
    'rms_current': consumption_data['rmsCurrent'],
    'rms_voltage':consumption_data['rmsVoltage'],
    'reactive_power':consumption_data['reactPwr'],
    'apparent_power':consumption_data['apprntPwr'],
    'power_factor':consumption_data['pwrFactor'],
    'wh_today': consumption_data['whToday'],
    'wh_last_seven_days': consumption_data['whLastSevenDays'],
    'wh_lifetime': consumption_data['whLifetime']
}


net_consumption_data = data['consumption'][1]
net_consumption_fields = {
    'power': net_consumption_data['wNow'],
    'rms_current': net_consumption_data['rmsCurrent'],
    'rms_voltage':net_consumption_data['rmsVoltage'],
    'reactive_power':net_consumption_data['reactPwr'],
    'apparent_power':net_consumption_data['apprntPwr'],
    'power_factor':net_consumption_data['pwrFactor'],
    'wh_today': net_consumption_data['whToday'],
    'wh_last_seven_days': net_consumption_data['whLastSevenDays'],
    'wh_lifetime': net_consumption_data['whLifetime']
}

production_data = data['production'][1]
production_fields = {
    'power': production_data['wNow'],
    'rms_current': production_data['rmsCurrent'],
    'rms_voltage':production_data['rmsVoltage'],
    'reactive_power':production_data['reactPwr'],
    'apparent_power':production_data['apprntPwr'],
    'power_factor':production_data['pwrFactor'],
    'wh_today': production_data['whToday'],
    'wh_last_seven_days': production_data['whLastSevenDays'],
    'wh_lifetime': production_data['whLifetime']
}

old_dc.write('iq_envoy_production', production_fields)
old_dc.write('iq_envoy_consumption', consumption_fields)

dc.write('iq_envoy_power', fields=production_fields, tags={'type':'production'})
dc.write('iq_envoy_power', fields=consumption_fields,tags={'type':'consumption'})
dc.write('iq_envoy_power', fields=net_consumption_fields,tags={'type':'net_consumption'})
