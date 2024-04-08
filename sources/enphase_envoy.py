import requests
import pickle
import os
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from datetime import datetime
import json

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.enphase_envoy
        self.data = None
        if self.config is None:
            raise Exception('no configuration for envoy found')
        self.session_file = self.config.get('session_file','enphase_session.p')
        self.session = {}
        self.load_session()

    def load_session(self):
        if not os.path.exists(self.session_file):
            return False
        self.session = pickle.load(open( self.session_file, "rb" ))
        return self.session != None

    def save_session(self):
        pickle.dump( self.session, open( self.session_file, "wb" ) )

    def reauthorize(self):
        login_url = "https://enlighten.enphaseenergy.com/login/login.json?"
        token_url = "https://entrez.enphaseenergy.com/tokens"
        user = self.config.user
        password = self.config.password
        envoy_serial = self.config.get('envoy_serial')

        # Get session_id
        response = requests.post(
            login_url,
            data={"user[email]": user, "user[password]": password}
        )
        session_id = response.json().get('session_id')

        # Get web_token
        response = requests.post(
            token_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"session_id": session_id, "serial_num": envoy_serial, "username": user})
        )
        
        web_token = response.text

        # Save the session
        self.session['access_token'] = web_token
        self.save_session()

    def get(self):
        print(self.session['access_token'])
        resp = requests.get(
            'http://'+self.config.host_url+'/production.json',
            headers={'Authorization': 'Bearer '+self.session['access_token']},
            verify=False
            )
        try:
            self.data = resp.json()
        except json.decoder.JSONDecodeError:
            print('Error decoding JSON')
            print(resp.content)

    def payload(self, field_data, ptype):
        fields = {
            'power': field_data['wNow'],
            'rms_current': field_data['rmsCurrent'],
            'rms_voltage':field_data['rmsVoltage'],
            'reactive_power':field_data['reactPwr'],
            'apparent_power':field_data['apprntPwr'],
            'power_factor':field_data['pwrFactor'],
            'wh_today': float(field_data['whToday']),
            'wh_last_seven_days': float(field_data['whLastSevenDays']),
            'wh_lifetime': float(field_data['whLifetime'])
        }
        tags = {'type': ptype}
        return EnvoyPayload(tags, fields)
    
    def payloads(self):
        if self.data is None:
            self.get()
        return [
            self.payload(self.data['consumption'][0], 'consumption'),
            self.payload(self.data['consumption'][1], 'net_consumption'),
            self.payload(self.data['production'][1], 'production'),
        ]

class EnvoyPayload(DataPayload):
    def __init__(self, tags, fields):
        super().__init__(tags, fields)
        self.topic = ['iq_envoy_power', tags['type']]
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<EnvoyPayload {self.topic} power: {self.fields["power"]}>'

