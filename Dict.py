# -*- coding: utf-8 -*-


class Dict(dict):
    
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v
            
    def __getattr__(self, key):
        try:
            value = self[key]
            return value if not isinstance(value, dict) else  Dict(**value)
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
        
        
        
if __name__ == "__main__":
    D1 = Dict(**{"aa": {"bb": "11"}})
    
    print D1.aa.bb