# -*- coding: utf-8 -*-

# pylint: disable-msg=C0111,W0231,W1201,C0301,W0212,R0903,R0913
# C0111: Missing method docstring
# W0231: threading.local __init__ is not called
# W1201: logging specify string format
# C0301: Line too long
# W0212: Access to a protected member _db_ctx
# R0903: Too few public methods
# R0913: Too many arguments

"""
use case:
    mysql_client = MysqlClient()
    mysql_client.create_engine('root', 'password', 'test')

    mysql_client.update('drop table if exists user')
    mysql_client.update(
        'create table user001 (id int primary key, name text')
    mysql_client.insert("user001", **{"id": "2000", "name": "aa"})
    users = db.select('select * from user')  # user: [{"id": "2000", "name": "aa"}] # noqa

    with mysql_client.connection():
        mysql_client.insert(...)
        mysql_client.update(...)

    with mysql_client.transaction():
        mysql_client.insert(...)
        mysql_client.update(...)
"""

import logging
import threading
import functools

import MySQLdb


__all__ = ["MysqlClient"]


class _DBCtx(threading.local):
    """ 持有数据库连接的私有对象 """

    def __init__(self, _engine):
        self._engine = _engine
        self.connection = None
        self.transaction = 0

    def is_connet(self):
        """ is connect """
        return self.connection is not None

    def connect(self):
        if self.connection is None:
            connection = self._engine()
            logging.info('open connection <%s>...' % hex(id(connection)))
            self.connection = connection

    def cursor(self):
        self.connect()
        return self.connection.cursor()

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def cleanup(self):
        if self.connection is not None:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection = None


class _ConnectionCtx(object):
    """ with connnection """

    def __init__(self, _db_ctx):
        self._db_ctx = _db_ctx
        self.should_cleanup = False

    def __enter__(self):
        if not self._db_ctx.is_connet():
            self._db_ctx.connect()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if self.should_cleanup is True:
            self._db_ctx.cleanup()


class _TransactionCtx(object):
    """ with transaction """

    def __init__(self, _db_ctx):
        self._db_ctx = _db_ctx
        self.should_cleanup = False

    def __enter__(self):
        if not self._db_ctx.is_connet():
            self._db_ctx.connect()
            self.should_cleanup = True
        self._db_ctx.transaction += 1
        logging.info('begin transaction...' if self._db_ctx.transaction == 1 else 'join current transaction...') # noqa
        return self

    def __exit__(self, exctype, excvalue, traceback):
        self._db_ctx.transaction -= 1
        try:
            if self._db_ctx.transaction == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_cleanup is True:
                self._db_ctx.cleanup()

    def commit(self):
        try:
            self._db_ctx.commit()
            logging.info('commit ok.')
        except Exception as ex:
            logging.warn(ex)
            self.rollback()
            raise

    def rollback(self):
        logging.warning('rollback transaction...')
        self._db_ctx.rollback()
        logging.info('rollback ok.')


def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        client = args[0]
        with _ConnectionCtx(client._db_ctx):
            return func(*args, **kw)
    return _wrapper


class MysqlClient(object):
    """ mysql client """

    def __init__(self):
        self._engine = None
        self._db_ctx = None

    def create_engine(
            self, user, password, database, host="127.0.0.1", port=3306, **kwargs): # noqa
        if self._engine is not None:
            raise Exception("Engine is already initialized")

        # 连接数据库参数
        params = dict(user=user, passwd=password,
                      db=database, host=host, port=port)
        defaults = dict(use_unicode=True, charset='utf8')
        for key, value in defaults.iteritems():
            params[key] = kwargs.pop(key, value)
        params.update(kwargs)

        # init
        self._engine = lambda: MySQLdb.connect(**params)
        self._db_ctx = _DBCtx(self._engine)
        logging.info('Init mysql engine <%s> ok.' % hex(id(self._engine)))

    def _select(self, sql, first, *args):
        cursor = None
        sql = sql.replace('?', '%s')
        logging.info('SQL: %s, ARGS: %s' % (sql, args))
        try:
            cursor = self._db_ctx.cursor()
            cursor.execute(sql, args)
            if cursor.description:
                names = [x[0] for x in cursor.description]
            if first:
                values = cursor.fetchone()
                if not values:
                    return None
                return dict(zip(names, values))
            return [dict(zip(names, x)) for x in cursor.fetchall()]
        finally:
            if cursor is not None:
                cursor.close()

    def _update(self, sql, *args):
        cursor = None
        sql = sql.replace('?', '%s')
        logging.info('SQL: %s, ARGS: %s' % (sql, args))
        try:
            cursor = self._db_ctx.cursor()
            cursor.execute(sql, args)
            affect_rowcount = cursor.rowcount
            if self._db_ctx.transaction == 0:
                # no transaction enviroment:
                logging.info('auto commit')
                self._db_ctx.commit()

            return affect_rowcount
        finally:
            if cursor is not None:
                cursor.close()

    @with_connection
    def update(self, sql, *args):
        return self._update(sql, *args)

    @with_connection
    def insert(self, table, **kw):
        cols, args = zip(*kw.iteritems())
        sql = 'insert into `%s` (%s) values (%s)' % (
            table,
            ','.join(['`%s`' % col for col in cols]),
            ','.join(['"%s"' % value for value in args])
        )
        return self._update(sql)

    @with_connection
    def select(self, sql, *args):
        return self._select(sql, False, *args)

    @with_connection
    def select_one(self, sql, *args):
        return self._select(sql, True, *args)

    def connection(self):
        return _ConnectionCtx(self._db_ctx)

    def transaction(self):
        return _TransactionCtx(self._db_ctx)


######################################################


def main():
    logging.basicConfig(level=logging.INFO)
    client = MysqlClient()

    client.create_engine('root', 'password', 'test')

    with client.transaction():
        client.update('drop table if exists user001')
        client.update(
            'create table user001 (id int primary key, name text,'
            'email text, passwd text, last_modified real)')
        client.insert("user001", **{"id": "2000", "name": "aa", "email": "aa", "passwd": "aa", "last_modified":123456}) # noqa
        print client.select("select * from user001")


if __name__ == '__main__':
    main()
