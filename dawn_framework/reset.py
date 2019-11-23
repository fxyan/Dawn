import utils


# noinspection SqlNoDataSourceInspection,SqlResolve
def reset(connection):
    sql_reset1 = '''
    DROP DATABASE `dawn`;
    '''
    sql_reset2 = '''
    CREATE DATABASE `dawn` 
    DEFAULT CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;
    '''
    sql_reset3 = 'USE `dawn`'
    with connection.cursor() as cursor:
        cursor.execute(sql_reset1)
        cursor.execute(sql_reset2)
        cursor.execute(sql_reset3)
        print('重置成功')


# noinspection SqlNoDataSourceInspection,SqlResolve
def create_user(connection):
    sql_create_table1 = '''
    CREATE TABLE `user` (
        `id`        INT NOT NULL AUTO_INCREMENT,
        `username`  VARCHAR(255) NOT NULL,
        `password`  VARCHAR(255) NOT NULL,
        PRIMARY KEY (`id`)
    );
    '''
    sql_create_table2 = '''
        CREATE TABLE `session` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `session_id` VARCHAR(45) NULL,
            `user_id` VARCHAR(45) NULL,
            `created_time` VARCHAR(255) NULL,
            `expired` VARCHAR(255) NULL,
            PRIMARY KEY (`id`)
        );
        '''
    sql_create_table3 = '''
        CREATE TABLE `weibo` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `content` VARCHAR(225) NULL,
            `user_id` VARCHAR(45) NULL,
            PRIMARY KEY (`id`)
        );
        '''
    sql_create_table4 = '''
        CREATE TABLE `comment` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `content` VARCHAR(225) NULL,
            `user_id` VARCHAR(45) NULL,
            `weibo_id` VARCHAR(45) NULL,
            PRIMARY KEY (`id`)
        );
        '''
    # 用 execute 执行一条 sql 语句
    # cursor 数据库游标
    with connection.cursor() as cursor:
        cursor.execute(sql_create_table1)
        cursor.execute(sql_create_table2)
        cursor.execute(sql_create_table3)
        cursor.execute(sql_create_table4)
        print('创建成功')


if __name__ == '__main__':
    connection = utils.connection()
    try:
        reset(connection)
        create_user(connection)
    finally:
        connection.close()
