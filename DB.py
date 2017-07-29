# -*- coding: utf-8 -*-

# pylint: disable-msg=W1201,C0111,C0103,W0201,w0231,W0621,W0212,W0612,R0903

'''
Created on 2017年5月11日

@author: dWX347607
'''

import logging
import threading
import functools
import MySQLdb


from Dict import Dict


__all__ = ["DB"]


class _Engine(object):
    """ 数据库引擎对象 """

    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()


class _LasyConnection(object):
    """ 数据库连接对象 """

    def __init__(self, _engine):
        self.connection = None
        self._engine = _engine

    def cursor(self):
        if self.connection is None:
            connection = self._engine.connect()
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


class _DbCtx(threading.local):
    """ 持有数据库连接的上下文对象 线程私有变量 """

    def __init__(self, _engine):
        self.connection = None
        self.transactions = 0
        self._engine = _engine

    def is_init(self):
        return self.connection is not None

    def init(self):
        self.connection = _LasyConnection(self._engine)
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()


class _ConnectionCtx(object):
    """ 连接上下文对象 """

    def __init__(self, _db_ctx):
        self._db_ctx = _db_ctx

    def __enter__(self):
        self.should_cleanup = False
        if not self._db_ctx.is_init():
            self._db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if self.should_cleanup is True:
            self._db_ctx.cleanup()


class _TransactionCtx(object):
    """ 事务上下文对象 """
    def __init__(self, _db_ctx):
        self._db_ctx = _db_ctx

    def __enter__(self):
        _db_ctx = self._db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        return self

    def __exit__(self, exctype, excvalue, traceback):
        _db_ctx = self._db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        _db_ctx = self._db_ctx
        try:
            _db_ctx.connection.commit()
        except:
            _db_ctx.connection.rollback()
            raise

    def rollback(self):
        self._db_ctx.connection.rollback()


def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        db = args[0]
        with _ConnectionCtx(db._db_ctx):
            return func(*args, **kw)
    return _wrapper


def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        db = args[0]
        with _TransactionCtx(db._db_ctx):
            return func(*args, **kw)
    return _wrapper


class DB(object):
    """
    use case:
        db = DB().create_engine('root', 'password', 'test')

        users = db.select('select * from user')
        n = db.update('insert into user(id, name) values(?, ?)', 4, 'Jack')

        with db.connection():
            db.select('...')
            db.update('...')
            db.update('...')

        with db.transaction():
            db.select('...')
            db.update('...')
            db.update('...')
    """

    def __init__(self):
        self._engine = None

    def create_engine(self, user, password, database, host='127.0.0.1',
                      port=3306, **kwargs):
        if self._engine is not None:
            raise Exception("Engine is already initialized")

        # 连接数据库参数
        params = dict(user=user, passwd=password,
                      db=database, host=host, port=port)
        defaults = dict(use_unicode=True, charset='utf8')
        for k, v in defaults.iteritems():
            params[k] = kwargs.pop(k, v)
        params.update(kwargs)

        self._engine = _Engine(lambda: MySQLdb.connect(**params))
        self._db_ctx = _DbCtx(self._engine)
        # test connection...
        logging.info('Init mysql engine <%s> ok.' % hex(id(self._engine)))

        return self

    def connection(self):
        return _ConnectionCtx(self._db_ctx)

    def transaction(self):
        return _TransactionCtx(self._db_ctx)

    def _select(self, sql, first, *args):
        _db_ctx = self._db_ctx
        cursor = None
        sql = sql.replace('?', '%s')
        logging.info('SQL: %s, ARGS: %s' % (sql, args))
        try:
            cursor = _db_ctx.connection.cursor()
            cursor.execute(sql, args)
            if cursor.description:
                names = [x[0] for x in cursor.description]
            if first:
                values = cursor.fetchone()
                if not values:
                    return None
                return Dict(names, values)
            return [Dict(names, x) for x in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()

    def _update(self, sql, *args):
        cursor = None
        sql = sql.replace('?', '%s')
        logging.info('SQL: %s, ARGS: %s' % (sql, args))
        try:
            cursor = self._db_ctx.connection.cursor()
            cursor.execute(sql, args)
            r = cursor.rowcount
            if self._db_ctx.transactions == 0:
                # no transaction enviroment:
                logging.info('auto commit')
                self._db_ctx.connection.commit()
            return r
        finally:
            if cursor:
                cursor.close()

    @with_connection
    def select(self, sql, *args):
        return self._select(sql, False, *args)

    @with_connection
    def select_one(self, sql, *args):
        return self._select(sql, True, *args)

    @with_connection
    def select_int(self, sql, *args):
        d = self._select(sql, True, *args)
        if len(d) != 1:
            raise Exception('Expect only one column.')
        return d.values()[0]

    @with_connection
    def update(self, sql, *args):
        return self._update(sql, *args)

    @with_connection
    def insert(self, table, **kw):
        cols, args = zip(*kw.iteritems())
        sql = 'insert into `%s` (%s) values (%s)' % (
            table,
            ','.join(['`%s`' % col for col in cols]),
            ','.join(['?' for i in range(len(cols))]))
        return self._update(sql, *args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = DB()

    db.create_engine('root', 'password', 'test')
    db.update('drop table if exists user001')
    db.update(
        'create table user001 (id int primary key, name text,' +
        'email text, passwd text, last_modified real)')
    import time
    u1 = dict(id=2000, name='Bob', email='bob@test.org', passwd='bobobob',
              last_modified=time.time())
    u2 = dict(id=2001, name='Aob', email='aob@test.org', passwd='aobobob',
              last_modified=time.time())

    with db.connection():
        db.insert("user001", **u1)
        db.insert("user001", **u2)
        print db.select("select * from user001")
