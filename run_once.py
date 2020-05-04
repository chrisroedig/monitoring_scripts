import importlib
import sys
import config

def run(source_name, reciever_names):
    # get the config
    cfg = config.Config()
    # instantiate the source
    source = importlib.import_module("sources."+source_name).DataSource(cfg)
    # instantiate the receivers
    receivers = []
    for receiver_name in reciever_names:
        receivers.append(importlib.import_module("receivers."+receiver_name).Receiver(cfg))
    if len(receivers) == 0:
        receivers.append(importlib.import_module("receivers.print").Receiver(cfg))
    # get the array of data payloads
    # iterate array and send it to each receiver
    for payload in source.payloads():
        for receiver in receivers:
            receiver.send(payload, source_config = source.config)


if __name__ == '__main__':
    source_name = sys.argv[1]
    receiver_names = sys.argv[2:]
    if len(receiver_names) == 0:
        receiver_names.append('print')
    run(source_name, receiver_names)