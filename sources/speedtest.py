import speedtest
from sources.data_source import DataSourceBase
from sources.data_source import DataPayload
from datetime import datetime

class DataSource(DataSourceBase):
    def __init__(self, config):
        self.config = config.speedtest
        self.data = None
        if self.config is None:
            raise Exception('no configuration for speedtest found')
    def get(self):
        # Set up Speed Test
        servers = []
        threads = None

        s = speedtest.Speedtest()
        s.get_servers(servers)
        s.get_best_server()

        # Perform Speed Test and grab results
        s.download(threads=threads)
        s.upload(threads=threads)
        self.data = s.results.dict()

    def payload(self):
        # Tag the measurement
        tags = {
            'location': self.config.location_tag,
            'isp' : self.data['client']['isp'],
            'ip': self.data['client']['ip'],
            'server_host' : self.data['server']['host']
        }

        # Structure the measurement data
        fields = {
            'upload_rate_bits': self.data['upload'],
            'download_rate_bits': self.data['download'],
            'ping_latency_ms': self.data['ping'],
            'bytes_sent': self.data['bytes_sent'],
            'bytes_received': self.data['bytes_received']
        }
        return SpeedTestPayload(tags, fields)
    
    def payloads(self):
        if self.data is None:
            self.get()
        return [
            self.payload()
        ]

class SpeedTestPayload(DataPayload):
    def __init__(self, tags, fields):
        super().__init__(tags, fields)
        self.topic = ['isp_speedtest']
        self.tags = tags
        self.fields = fields
    def __repr__(self):
        return f'<SpeedTestPayload {self.topic} up: {self.fields["upload_rate_bits"]} down: {self.fields["download_rate_bits"]}>'
