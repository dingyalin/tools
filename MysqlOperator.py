# encoding=utf-8
'''
Created on 2016年5月10日

@author: dWX347607
'''
import MySQLdb
import logging

class MysqlOperator(object):
    '''
    mysql数据库操作
    '''

    def __init__(self, _host, _port, _user, _passwd, _db):
        self.conn = None
        self.cur = None
        self.connect(_host, _port, _user, _passwd, _db)
        
    def connect(self, _host, _port, _user, _passwd, _db):
        try:
            self.conn = MySQLdb.connect(host=_host, user=_user, passwd=_passwd, db=_db, port=_port) 
            self.cur = self.conn.cursor() 
        except MySQLdb.Error, ex:
            logging.error(ex)
            
    def execute(self, sql):
        try:
            logging.info(sql)
            self.cur.execute(sql)
            return self.cur.fetchall()
        except MySQLdb.Error, ex:
            logging.error(ex)
            
    def commit(self):
        try:
            self.conn.commit()
        except MySQLdb.Error, ex:
            logging.error(ex)
            
    def update_t_sys_config(self, VALUE, CATEGORY, NAME, TENANT_ID):
        sql = "UPDATE `t_sys_config` SET `VALUE`='%s' WHERE (`CATEGORY`='%s') AND (`NAME`='%s') AND (`TENANT_ID`='%s')" % (VALUE, CATEGORY, NAME, TENANT_ID)
        logging.info(sql)
        self.execute(sql)
    
    def close(self):
        try:
            self.conn.close()  
            self.cur.close()
        except MySQLdb.Error, ex:
            logging.error(ex)
            
            