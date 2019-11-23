import typing

import pymysql

from dawn_framework.utils import log


# noinspection SqlNoDataSourceInspection,SqlResolve
class SQLModel(object):

    def __init__(self, form):
        self.id = form.get('id', None)

    @classmethod
    def table_name(cls):
        return '{}'.format(cls.__name__)

    @classmethod
    def new(cls, form):
        m = cls(form)
        _id = cls.insert(m.__dict__)
        m.id = _id
        return m

    @classmethod
    def _pymysql_connection(cls):
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='hxdns74521',
            db='dawn',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection

    @classmethod
    def insert(cls, form: typing.Dict[str, str]):
        # INSERT INTO
        #     `user` (`username`, `password`, `email`)
        # VALUES
        #     (`gua`, `123`, `gua@gua.com`)
        connection = cls._pymysql_connection()
        try:
            sql_keys = []
            sql_values = []
            for k in form.keys():
                sql_keys.append('`{}`'.format(k))
                sql_values.append('%s')
            formatted_sql_keys = ', '.join(sql_keys)
            formatted_sql_values = ', '.join(sql_values)

            sql_insert = 'INSERT INTO `{}` ({}) VALUES ({});'.format(
                cls.table_name(), formatted_sql_keys, formatted_sql_values
            )
            log('ORM insert <{}>'.format(sql_insert))
            values = tuple(form.values())
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_insert, values)))
                cursor.execute(sql_insert, values)
                _id = cursor.lastrowid
            connection.commit()
        finally:
            connection.close()
        return _id

    @classmethod
    def one(cls, **kwargs):
        sql_where = ' AND '.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        sql_select = 'SELECT * FROM {} WHERE {}'.format(cls.table_name(), sql_where)
        log('ORM one <{}>'.format(sql_select))

        values = tuple(kwargs.values())
        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_select, values)))
                cursor.execute(sql_select, values)
                result = cursor.fetchone()
        finally:
            connection.close()

        if result is None:
            return None
        else:
            m = cls(result)
        return m

    @classmethod
    def all(cls, **kwargs):
        # SELECT * FROM User WHERE username='xxx' AND password='xxx'
        sql_select = 'SELECT * FROM {}'.format(cls.table_name())

        if len(kwargs) > 0:
            sql_where = ' AND '.join(
                ['`{}`=%s'.format(k) for k in kwargs.keys()]
            )
            sql_select = '{} WHERE {}'.format(sql_select, sql_where)
        log('ORM all <{}>'.format(sql_select))

        values = tuple(kwargs.values())
        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_select, values)))
                cursor.execute(sql_select, values)
                result = cursor.fetchall()
        finally:
            connection.close()

        ms = []
        for row in result:
            m = cls(row)
            ms.append(m)
        return ms

    @classmethod
    def delete(cls, id):
        sql_delete = 'DELETE FROM {} WHERE `id`=%s'.format(cls.table_name())
        log('ORM delete <{}>'.format(sql_delete))

        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_delete, (id,))))
                cursor.execute(sql_delete, (id,))
            connection.commit()
        finally:
            connection.close()

    @classmethod
    def update(cls, id, **kwargs):
        # UPDATE
        # 	`User`
        # SET
        # 	`username`=%s, `password`=%s
        # WHERE `id`=%s;
        sql_set = ', '.join(
            ['`{}`=%s'.format(k) for k in kwargs.keys()]
        )
        sql_update = 'UPDATE {} SET {} WHERE `id`=%s'.format(
            cls.table_name(),
            sql_set,
        )
        log('ORM update <{}>'.format(sql_update.replace('\n', ' ')))

        values = list(kwargs.values())
        values.append(id)
        values = tuple(values)

        connection = cls._pymysql_connection()
        try:
            with connection.cursor() as cursor:
                log('ORM execute <{}>'.format(cursor.mogrify(sql_update, values)))
                cursor.execute(sql_update, values)
            connection.commit()
        finally:
            connection.close()
