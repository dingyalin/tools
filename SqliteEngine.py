# -*- coding: utf-8 -*-
'''
Created on 2016年12月30日

@author: dWX347607
'''


import sqlite3
import logging



engine = None


class _LasyConnection(object):
    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            connection = engine.connect()
            logging.info('open connection <%s>...' % hex(id(connection)))
            self.connection = connection
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()


class SqliteEngine(object):
    
    def __init__(self):
        pass
    
    def create_engine(self):
        return self
    
    
    