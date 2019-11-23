import random
import time
import pymysql
from password import mysql_password


def log(*args, **kwargs):
    time_format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    formatted = time.strftime(time_format, value)
    print(formatted, flush=True, *args, **kwargs)


def random_string():
    """
    生成一个随机的字符串
    """
    seed = 'sdfsdafasfsdfsdwtfgjdfghfg'
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=mysql_password,
        db='dawn',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

