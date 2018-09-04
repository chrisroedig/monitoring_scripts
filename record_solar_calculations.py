import data_client
import config
from pysolar import solar
import datetime
import math

cfg = config.Config()
dc = data_client.DataClient(database=cfg.darksky.influx_database)

scfg = cfg.pysolar
lat = scfg.latitude
lng = scfg.longitude
now = datetime.datetime.now()


def calc_solar_data(t):
    solar_fields = {
     'altitude': 0.0,
     'azimuth': 0.0,
     'direct_flux': 0.0,
     'max_direct_power': 0.0,
     'projected_direct_power': 0.0
    }

    solar_fields['altitude'] = solar.get_altitude(lat, lng, t)
    solar_fields['azimuth'] = (180 - solar.get_azimuth(lat, lng, t))%360

    az_diff = scfg.panel_azimuth - solar_fields['azimuth']
    az_projection = max(0,math.cos(math.pi*az_diff/180.0))

    alt_diff = (90-scfg.panel_altitude) - solar_fields['altitude']
    alt_projection = max(0,math.cos(math.pi*alt_diff/180.0))

    solar_fields['alt_projection'] = float(alt_projection)
    solar_fields['az_projection'] = float(az_projection)
    solar_fields['total_projection'] = float(az_projection * alt_projection)



    effective_area = scfg.system_efficiency *scfg.panel_count * scfg.panel_area
    if solar_fields['altitude'] > 0:
        solar_fields['direct_flux'] = solar.radiation.get_radiation_direct(t, solar_fields['altitude'])
        solar_fields['projected_flux'] = solar_fields['direct_flux'] * solar_fields['total_projection']
        solar_fields['max_direct_power'] = effective_area * solar_fields['direct_flux']
        solar_fields['projected_direct_power'] = effective_area *  solar_fields['projected_flux']
    return solar_fields

tags = {
    'location': scfg.location_tag,
    'system': '20xSW295_IQ6+'
}

def batch(start_date, days):
    slices = days*24*6
    for i in range(slices):
        ts = start_date + datetime.timedelta(minutes=i*10)
        utcts = ts + datetime.timedelta(hours=4)
        data = calc_solar_data(ts)
        print(utcts,data)
        dc.write('solar_report', fields=data, tags=tags, timestamp=utcts)

if __name__ == '__main__':
    now = datetime.datetime.now()
    data = calc_solar_data(now)
    dc.write('solar_report', fields=data, tags=tags)
