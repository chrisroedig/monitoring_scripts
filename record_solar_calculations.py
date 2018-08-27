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



solar_fields = {
 'altitude': 0.0,
 'azimuth': 0.0,
 'direct_flux': 0.0
}

solar_fields['altitude'] = solar.get_altitude(lat, lng, now)
solar_fields['azimuth'] = solar.get_azimuth(lat, lng, now)
solar_fields['direct_flux'] = solar.radiation.get_radiation_direct(now, solar_fields['altitude'])

az_diff = scfg.panel_azimuth - solar_fields['azimuth']
az_projection = abs(math.cos(math.pi*az_diff/180.0))

alt_diff = scfg.panel_altitude - solar_fields['altitude']
alt_projection = abs(math.cos(math.pi*alt_diff/180.0))

solar_fields['alt_projection'] = alt_projection
solar_fields['az_projection'] = az_projection
solar_fields['total_projection'] = az_projection * alt_projection

solar_fields['projected_flux'] = solar_fields['direct_flux'] * solar_fields['total_projection']

effective_area = scfg.system_efficiency *scfg.panel_count * scfg.panel_area

solar_fields['max_power'] = effective_area * solar_fields['direct_flux']
solar_fields['projected_max_power'] = effective_area *  solar_fields['projected_flux']

tags = {
    'location': scfg.location_tag,
    'system': '20xSW295_IQ6+'
}


dc.write('solar_report', fields=solar_fields, tags=tags)
