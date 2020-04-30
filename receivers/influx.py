from influxdb import InfluxDBClient
import datetime
from receivers.receiver import ReceiverBase

class Receiver(ReceiverBase):
    def __init__(self, config):
        if config.influxdb is None:
            raise Exception('configuration for "influxdb" not found')
        self.config = config.influxdb
    
    def send(self, payload, source_config = None):
        measurement = payload.topic[0]
        client = self.client(source_config.influx_database)
        data = self.json_data(
            measurement, payload.fields, timestamp=payload.timestamp, tags=payload.tags)
        client.write_points([data])

    def json_data(self, measurement, fields, timestamp = None, tags={}):
        if timestamp is None:
            timestamp = datetime.datetime.utcnow().isoformat()
        return {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": fields
            }

    def client(self, database):
        return InfluxDBClient(
            self.config.host_url,
            self.config.port,
            self.config.username,
            self.config.password,
            database
        )


