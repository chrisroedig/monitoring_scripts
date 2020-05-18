import requests
import json
import time
import sys
from datetime import datetime
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
import pickle
import os

API_URL = 'https://api.ecobee.com/'

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.ecobee
        self.data = None
        if self.config is None:
            raise Exception('no configuration for ecobee found')
        self.session_file = self.config.get('session_file','ecobee_session.p')
        self.session = {}
        self.load_session()
    
    def load_session(self):
        if not os.path.exists(self.session_file):
            return False
        self.session = pickle.load(open( self.session_file, "rb" ))
        return self.session != None

    def save_session(self):
        pickle.dump( self.session, open( self.session_file, "wb" ) )

    def get_pin(self):
        resp = self.get("authorize", params= {'scope': 'smartWrite', 'response_type': 'ecobeePin'}, auth=False)
        data = resp.json()
        return data['ecobeePin'], data['code']

    def create_original_token(self, code):
        resp = self.post("token", params= {'code': code, 'grant_type': 'ecobeePin'})
        data = resp.json()
        if data.get('access_token', None) is None:
            return None
        return data

    def create_token(self, refresh_token):
        resp = self.post("token", params = {'grant_type': 'refresh_token', 'code': refresh_token})
        data = resp.json()
        if data.get('access_token', None) is None:
            return None
        return data

    def get(self, path, params = {}, auth=True):
        p = { 'client_id': self.config.client_id }
        p.update(params)
        h = {}
        if(auth is True):
            h.update({'Authorization': 'Bearer %s' % self.session['access_token']})
        return requests.get("%s/%s" % (API_URL, path) , params = p, headers = h)
  
    def post(self, path, params = {}, data = None):
        p = { 'client_id': self.config.client_id }
        p.update(params)
        return requests.post("%s/%s" % (API_URL, path) , params = p, data = data)

    def authorize(self):
        print('Requesting OAUTH PIN...')
        pin, code = self.get_pin()
        
        print('log in at: https://www.ecobee.com/consumerportal')
        print('and go to')
        print('https://www.ecobee.com/consumerportal/index.html#/my-apps/add/new')
        print('enter this PIN: %s'% (pin))

        token_info = None
        for i in range(20):
            token_info = self.create_original_token(code)
            if token_info is None :
                print('retrying...')
            else:
                print('got token!')
                print(token_info)
                self.session = token_info
                self.save_session()
                break
            time.sleep(5)
        print('Done!')

    def reauthorize(self):
        token_info = self.create_token(self.session['refresh_token'])
        if token_info is None :
            print('FAILED')
            return False
        else:
            print('got token!')
            print(token_info)
            self.session = token_info
            self.save_session()
            return True

    def read(self):
        body = { "selection": {           \
            "selectionType": "registered",  \
            "selectionMatch": "",           \
            "includeEquipmentStatus": True, \
            "includeSensors": True,         \
            "includeSettings": True,        \
            "includeRuntime": True          \
            }}
        resp = self.get('1/thermostat',params = { 'format':'json', 'body':json.dumps(body) })
        if(resp.status_code=='200'):
            raise Exception(f'Read failed with code {resp.status_code}')
        self.data = resp.json()
        if(self.data['status']['code']!=0):
            raise Exception(f'Code {self.data["status"]["code"]}: {self.data["status"]["message"]}')
        return self.data

    def thermostat(self, data=None):
        if self.data is None:
            self.read()
        data = self.data['thermostatList'][0]
        fields = {
            'mode' : data['settings']['hvacMode'],
            'cool_temp_f' : data['runtime']['desiredCool']/10.0,
            'heat_temp_f' : data['runtime']['desiredHeat']/10.0,
            'hvac_cool' : int(data['settings']['hvacMode'] == 'cool'),
            'hvac_heat' : int(data['settings']['hvacMode'] == 'heat'),
            'hvac_auto' : int(data['settings']['hvacMode'] == 'auto'),
            'fan_mode' : data['runtime']['desiredFanMode'],
            'fan_mode_auto' : int(data['runtime']['desiredFanMode'] == 'auto'),
            'fan_mode_on' : int(data['runtime']['desiredFanMode'] == 'on'),
            'heating' : int('auxHeat' in data['equipmentStatus']),
            'cooling' : int('compCool' in data['equipmentStatus']),
            'fan_running' : int('fan' in data['equipmentStatus'])
        }
        tags = {
            'data_type': 'system',
            'location': self.config.location_tag
        }
        topic = 'thermostat'
        return ThermostatDataPayload(tags, fields)

    def sensors(self, data=None):
        if self.data is None:
            self.read()
        data = self.data['thermostatList'][0]['remoteSensors']
        return map(self.sensor, data)

    def sensor(self, data):
        tags = {
                'data_type': 'sensor',
                'sensor_type': data['type'],
                'sensor_code': data.get('code', 'main'),
                'location': self.config.location_tag
        }
        fields = {}
        for cap in data['capability']:
            fields[cap['type']] = cap['value']
            if cap['type'] == 'temperature':
                fields[cap['type']] = int(fields[cap['type']]) / 10.0
            if cap['type'] == 'occupancy':
                fields[cap['type']] = int(fields[cap['type']] == 'true')
            if cap['type'] == 'humidity':
                fields[cap['type']] = float(fields[cap['type']])
        return SensorDataPayload(tags, fields)
    
    def payloads(self):
        return [self.thermostat()] + list(self.sensors())

class SensorDataPayload(DataPayload):
    def __init__(self, tags, fields):
        self.topic = [ 'hvac_sensor', 'ecobee', tags['sensor_code'] ]
        self.tags = tags
        self.fields = fields
        self.timestamp = datetime.now()

    def __repr__(self):
        return f'<SensorDataPayload {self.tags["sensor_code"]} temp: {self.fields["temperature"]}>'

class ThermostatDataPayload(DataPayload):
    def __init__(self, tags, fields):
        self.topic = [ 'hvac_system', 'ecobee', 'thermostat' ]
        self.tags = tags
        self.fields = fields
        self.timestamp = datetime.now()
        
    def __repr__(self):
        return f'<ThermostatDataPayload mode: {self.fields["mode"]}, temps: {self.fields["heat_temp_f"]}/{self.fields["cool_temp_f"]}>'