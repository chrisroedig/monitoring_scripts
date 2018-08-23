import yaml

class Config():
    def __init__(self, filename='config.yml', d = None, source = None):
        if d is not None:
            self._source = source
            self._data = d
        else:
            self._source = filename
            self._data = yaml.load(file(filename))
    def list(self):
        return self._data.keys()
    def __getattr__(self,name):
        val = self._data.get(name)
        if type(val) == dict:
            return self.child_config(val, name)
        return val
    def __repr__(self):
        return "< Configuration from " + self._source +" >"
    def child_config(self, d, name):
        val = self.__class__(d=d, source = self._source+"::"+name )
        return val
