import importlib
import sys
import config

source_name = sys.argv[1]
message = sys.argv[2]
source = importlib.import_module("sources."+source_name).DataSource(config.Config())
source.__getattribute__(message)() 
