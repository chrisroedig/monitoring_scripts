import data_client
import config
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

