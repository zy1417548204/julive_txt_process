# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

import pymysql

import config.config_default as config_default


class MysqlConnection(object):
    _connection = None

    def __new__(cls):
        if not cls._connection:
            mysql_config = config_default.configs[u'mysql']
            cls._connection = pymysql.connect(host=mysql_config[u'host'],
                                 user=mysql_config[u'user'],
                                 password=mysql_config[u'password'],
                                 db=mysql_config[u'db'],
                                 charset=mysql_config[u'charset'],
                                 cursorclass=pymysql.cursors.DictCursor)
        return cls._connection

class MysqlOperation(object):

    def select_data(self,sql,connection):

        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

    def update_data(self,sql,connection):

        with connection.cursor() as cursor:
            cursor.execute(sql)


if __name__ == '__main__':
    sql = 'select talk.id, talk.record_file_url, talk.record_file_aliyun_url, talk.record_txt_json_url ' \
          'from ' \
          'comjia_merge.yw_talk_audio_relation as relation,' \
          'comjia_merge.yw_sys_number_talking as talk where relation.record_id = talk.id'

    try:
        connection = MysqlConnection()
        sql_operation = MysqlOperation()
        result = sql_operation.select_data(sql,connection)
        print result
    finally:
        connection.close()
