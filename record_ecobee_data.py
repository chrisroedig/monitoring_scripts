import requests
from config import Config
import json
import time
import sys
import data_client

API_URL = 'https://api.ecobee.com/'
CFG = Config().ecobee
if CFG is None:
    raise Exception('no configuration for ecobee found')

DC = data_client.DataClient(database=CFG.influx_database)

def get_pin():
    resp = get("authorize", params= {'scope': 'smartWrite', 'response_type': 'ecobeePin'}, auth=False)
    data = resp.json()
    return data['ecobeePin'], data['code']

def create_original_token(code):
    resp = post("token", params= {'code': code, 'grant_type': 'ecobeePin'})
    data = resp.json()
    if data.get('access_token', None) is None:
        return None
    return data

def create_token(refresh_token):
    resp = post("token", params = {'grant_type': 'refresh_token', 'code': refresh_token})
    data = resp.json()
    if data.get('access_token', None) is None:
        return None
    return data

def get(path, params = {}, auth=True):
    p = { 'client_id': CFG.client_id }
    p.update(params)
    h = {}
    if(auth is True):
        h.update({'Authorization': 'Bearer %s' % CFG.access_token})
    return requests.get("%s/%s" % (API_URL, path) , params = p, headers = h)
  

def post(path, params = {}, data = None):
    p = { 'client_id': CFG.client_id }
    p.update(params)
    return requests.post("%s/%s" % (API_URL, path) , params = p, data = data)

def authorize():
    print('Requesting OAUTH PIN...')
    pin, code = get_pin()
    
    print('log in at: https://www.ecobee.com/consumerportal')
    print('and go to')
    print('https://www.ecobee.com/consumerportal/index.html#/my-apps/add/new')
    print('enter this PIN: %s'% (pin))

    token_info = None
    for i in range(20):
        token_info = create_original_token(code)
        if token_info is None :
            print('retrying...')
        else:
            print('got token!')
            print(token_info)
            CFG.save('access_token', token_info['access_token'])
            CFG.save('refresh_token', token_info['refresh_token'])
            break
        time.sleep(5)
    print('Done!')

def reauthorize():
    token_info = create_token(CFG.refresh_token)
    if token_info is None :
        print('FAILED')
    else:
        print('got token!')
        print(token_info)
        CFG.save('access_token', token_info['access_token'])
        CFG.save('refresh_token', token_info['refresh_token'])

def read():
    body = { "selection": {           \
        "selectionType": "registered",  \
        "selectionMatch": "",           \
        "includeEquipmentStatus": True, \
        "includeSensors": True,         \
        "includeSettings": True,        \
        "includeRuntime": True          \
        }}
    resp = get('1/thermostat',params = { 'format':'json', 'body':json.dumps(body) })
    if(resp.status_code=='200'):
        return None
    data = resp.json()
    return data

def record():
    data = read()
    thermostat_data = data['thermostatList'][0]
    runtime_data = thermostat_data['runtime']
    sensor_data = thermostat_data['remoteSensors']
    system_tags , system_fields = process_system_data(thermostat_data)
    sensor_measurements =  process_sensor_data(sensor_data)
    for sensor_tags, sensor_fields in  sensor_measurements:
        DC.write('hvac_sensor', fields=sensor_fields, tags=sensor_tags)   
    DC.write('hvac_system', fields=system_fields, tags=system_tags)


def process_sensor_data(sensors):
    sensor_data = []
    for sensor in sensors:
        tags = {
            'data_type': 'sensor',
            'sensor_type': sensor['type'],
            'sensor_code': sensor.get('code', 'main'),
            'location': CFG.location_tag
        }
        fields = {}
        for cap in sensor['capability']:
            fields[cap['type']] = cap['value']
            if cap['type'] == 'temperature':
                fields[cap['type']] = int(fields[cap['type']]) / 10.0
            if cap['type'] == 'occupancy':
                fields[cap['type']] = int(fields[cap['type']] == 'true')
            if cap['type'] == 'humidity':
                fields[cap['type']] = float(fields[cap['type']])
            sensor_data.append((tags, fields))
    return sensor_data

def process_system_data(thermostat_data):
    tags = {
        'data_type': 'system',
        'location': CFG.location_tag
    }
    status = thermostat_data['equipmentStatus']
    runtime = thermostat_data['runtime']
    settings = thermostat_data['settings']
    fields = {
        'hvac_cool' : int(settings['hvacMode'] == 'cool'),
        'hvac_heat' : int(settings['hvacMode'] == 'heat'),
        'hvac_auto' : int(settings['hvacMode'] == 'auto'),
        'fan_mode_auto' : int(runtime['desiredFanMode'] == 'auto'),
        'fan_mode_on' : int(runtime['desiredFanMode'] == 'on'),
        'cool_temp_f' : runtime['desiredCool']/10.0,
        'heat_temp_f' : runtime['desiredHeat']/10.0,
        'cooling': int('compCool' in status),
        'heating': int('auxHeat' in status),
        'fan_running': int('fan' in status)
    }
    return (tags, fields)

    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'auth':
           authorize()
        if sys.argv[1] == 'reauth':
            reauthorize()
        if sys.argv[1] == 'read':
            print(read())
    else:
        record()