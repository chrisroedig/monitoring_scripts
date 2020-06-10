from pysolar import solar
import datetime
import math
from sources.data_source import DataPayload
from sources.data_source import DataSourceBase

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.pysolar
        if self.config is None:
            raise Exception('no configuration for pysolar found')
        self.reset_fields()
        
    def reset_fields(self):
        self.fields = {
            'altitude': 0.0,
            'azimuth': 0.0,
            'direct_flux': 0.0,
            'max_direct_power': 0.0,
            'projected_direct_power': 0.0
        }

    def payloads(self, start_time=None, samples=6, step=10):
        if start_time is None:
            start_time = datetime.datetime.now(datetime.timezone.utc)
        times = [ 
            (start_time + datetime.timedelta(minutes=(i * step))) 
            for i in range(samples) 
            ]
        return [ self.payload(t) for t in times ]

    def payload(self, time):
        ts = time
        lat = self.config.latitude
        lng = self.config.longitude
        paz = self.config.panel_azimuth
        palt = self.config.panel_altitude

        effective_area = self.config.system_efficiency * self.config.panel_count * self.config.panel_area

        self.fields['altitude'] = solar.get_altitude(lat, lng, ts)
        self.fields['azimuth'] = (180 - solar.get_azimuth(lat, lng, ts))%360

        az_diff = paz - self.fields['azimuth']
        az_projection = max(0,math.cos(math.pi*az_diff/180.0))

        alt_diff = (90-palt) - self.fields['altitude']
        alt_projection = max(0,math.cos(math.pi*alt_diff/180.0))

        self.fields['alt_projection'] = float(alt_projection)
        self.fields['az_projection'] = float(az_projection)
        self.fields['total_projection'] = float(az_projection * alt_projection)

        if self.fields['altitude'] > 0:
            self.fields['direct_flux'] = solar.radiation.get_radiation_direct(ts, self.fields['altitude'])
            self.fields['projected_flux'] = self.fields['direct_flux'] * self.fields['total_projection']
            self.fields['max_direct_power'] = effective_area * self.fields['direct_flux']
            self.fields['projected_direct_power'] = effective_area *  self.fields['projected_flux']
        tags = {
            'location': self.config.location_tag,
        }
        return PySolarPayload(tags, self.fields, time)


class PySolarPayload(DataPayload):
    def __init__(self, tags, fields, timestamp):
        self.topic = [ 'solar_report', tags['location']]
        self.timestamp = timestamp
        self.tags = tags
        self.fields = fields
    
    def __repr__(self):
        return f'<PySolarPayload {self.topic} power: {self.fields["projected_direct_power"]}>'
