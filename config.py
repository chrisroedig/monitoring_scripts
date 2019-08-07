import yaml

class Config():
    def __init__(self, filename='config.yml', d = None, source = None):
        if d is not None:
            self._source = source
            self._data = d
        else:
            self._source = filename
            self._data = yaml.load(open(filename, 'r').read())
    def list(self):
        return self._data.keys()
    def __getattr__(self,name):
        if self._data is None:
            return None
        val = self._data.get(name, None)
        if type(val) == dict:
            return self.child_config(val, name)
        return val
    def __repr__(self):
        return "< Configuration from " + self._source +" >"
    def child_config(self, d, name):
        val = self.__class__(d=d, source = self._source+"::"+name )
        return val
    def path(self):
        return self._source.split("::")
    def save(self, keyname, value):
        filename = self.path()[0]
        file_dict = yaml.load(open(filename, 'r').read())
        working_dict = file_dict
        self._data[keyname] = value
        for k in self.path()[1:]:
            working_dict= working_dict[k]
        working_dict.update(self._data)
        stream = open(filename, 'w')
        yaml.dump(file_dict, stream, default_flow_style=False)

