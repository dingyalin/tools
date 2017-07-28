# -*- coding: utf-8 -*-

"""
Created on 2017年5月11日

@author: dWX347607
"""


class Dict(dict):
    """ Simple dict but support access as x.y style """

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for key, value in zip(names, values):
            self[key] = value

    def __getattr__(self, key):
        try:
            value = self[key]
            return value if not isinstance(value, dict) else Dict(**value)
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


if __name__ == "__main__":
    D1 = Dict(**{"aa": {"bb": "11"}})

    print D1.aa.bb
