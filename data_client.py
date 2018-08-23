import influxdb
import config
import datetime

class DataClient():
    def __init__(self):
        self.config = config.Config()
        self.influx_client = influxdb.InfluxDBClient(
            self.config.influxdb.host_url,
            self.config.influxdb.port,
            self.config.influxdb.username,
            self.config.influxdb.password,
            self.config.influxdb.database
        )
    def write(self, measurement, fields = {}, timestamp = None, tags = {}):
        return self.influx_client.write_points([self.json_data(
            measurement, fields, timestamp, tags
        )])

    def json_data(self, measurement, fields, timestamp = None, tags={}):
        if timestamp is None:
            timestamp = datetime.datetime.utcnow().isoformat()
        return {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": fields
            }
