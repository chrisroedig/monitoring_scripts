import importlib
import sys
import config

def run(source_name, task_name):
    source = importlib.import_module("sources."+source_name).DataSource(config.Config())
    source.__getattribute__(task_name)() 

if __name__ == '__main__':
    source_name = sys.argv[1]
    task_name = sys.argv[2]
    run(source_name, task_name)
