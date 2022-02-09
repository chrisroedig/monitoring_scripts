from http import client
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from receivers.receiver import ReceiverBase

class Receiver(ReceiverBase):
    def __init__(self, config):
        if config.influxdb is None:
            raise Exception('configuration for "influxdb" not found')
        self.config = config.influxdb
    
    def send_x(self, payload, source_config = None):
        measurement = payload.topic[0]
        client = self.client(source_config.influx_database)
        data = self.json_data(
            measurement, payload.fields, timestamp=payload.timestamp, tags=payload.tags)
        client.write_points([data])
    
    def send(self, payload, source_config):
        measurement = payload.topic[0]
        client = self.client()
        data = self.json_data(
            measurement, payload.fields, timestamp=payload.timestamp, tags=payload.tags)
        point = Point.from_dict(data)
        
        with self.client().write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(source_config.influx_database, self.config.org, point)
        

    def json_data(self, measurement, fields, timestamp = None, tags={}):
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        return {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": fields
            }

    def client(self):
        return InfluxDBClient(
            self.config.host_url,
            self.config.token,
            org=self.config.org
        )


