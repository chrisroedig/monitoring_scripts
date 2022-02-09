import requests
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from datetime import datetime

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.enphase_envoy
        self.data = None
        if self.config is None:
            raise Exception('no configuration for envoy found')
    
    def get(self):
        self.data = requests.get('http://'+self.config.host_url+'/production.json').json()

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