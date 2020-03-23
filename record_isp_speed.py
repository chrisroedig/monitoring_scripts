# {
# 'download': 10154489.247588266,
# 'upload': 3391086.0923270765,
# 'ping': 28.171,
# 
#  'server': {'url': 'http://speedy.az21.cloudpropeller.com:8080/speedtest/upload.php',
#   'lat': '39.9611',
#   'lon': '-82.9989',
#   'name': 'Columbus, OH',
#   'country': 'United States',
#   'cc': 'US',
#   'sponsor': 'CloudPropeller.com',
#   'id': '24678',
#   'host': 'speedy.az21.cloudpropeller.com:8080',
#   'd': 13.701871236061143,
#   'latency': 28.171},

#  'timestamp': '2020-03-23T14:48:41.257967Z',
#  'bytes_sent': 5242880,
#  'bytes_received': 12745120,
#  
#  'share': None,
#  'client': {'ip': '24.96.10.176',
#   'lat': '40.0818',
#   'lon': '-82.9665',
#   'isp': 'WideOpenWest',
#   'isprating': '3.7',
#   'rating': '0',
#   'ispdlavg': '0',
#   'ispulavg': '0',
#   'loggedin': '0',
#   'country': 'US'}}


import data_client
import config
import datetime
import speedtest
import dateutil

# Configuration and InfluxDB client
cfg = config.Config()
scfg = cfg.speedtest
dc = data_client.DataClient(database=scfg.influx_database)

# Set up Speed Test
servers = []
threads = None

s = speedtest.Speedtest()
s.get_servers(servers)
s.get_best_server()

# Perform Speed Test and grab results
s.download(threads=threads)
s.upload(threads=threads)
st_data = s.results.dict()

# Tag the measurement
tags = {
    'location': '395Riley',
    'isp' : st_data['client']['isp'],
    'ip': st_data['client']['ip'],
    'server_host' : st_data['server']['host']
}

# Structure the measurement data
data = {
    'upload_rate_bits': st_data['upload'],
    'download_rate_bits': st_data['download'],
    'ping_latency_ms': st_data['ping'],
    'bytes_sent': st_data['bytes_sent'],
    'bytes_received': st_data['bytes_received']
}

# parse the given timestamp
timestamp = dateutil.parser.isoparse(st_data['timestamp'])

# write the data to influxdb
dc.write('speedtest', fields=data, tags=tags, timestamp=timestamp)

