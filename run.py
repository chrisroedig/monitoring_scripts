import importlib
import sys
import config

# instantiate the source
source_name = sys.argv[1]
cfg = config.Config()
source = importlib.import_module("sources."+source_name).DataSource(cfg)

# instantiate the receivers
receivers = []
for receiver_name in sys.argv[2:]:
    receivers.append(importlib.import_module("receivers."+receiver_name).Receiver(cfg))

# get the array of data payloads
# iterate array and send it to each receiver
for payload in source.payloads():
    for receiver in receivers:
        receiver.send(payload, source.config)


