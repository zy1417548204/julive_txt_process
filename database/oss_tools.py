# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

import os
import shutil
import time

import oss2

import config.config_default as config_default


class OssOperator(object):

    def __init__(self,access_id,access_key,end_point,bucket_name):
        self.auth = oss2.Auth(access_key_id=access_id,access_key_secret=access_key)
        self.service = oss2.Service(auth=self.auth,endpoint=end_point)
        self.access_key_id = access_id
        self.access_key_secret = access_key
        self.end_point = end_point
        self.bucket_name = bucket_name

    def create_bucket(self):
        bucket = oss2.Bucket(auth=self.auth,endpoint=self.end_point,bucket_name=self.bucket_name)
        bucket.create_bucket()

    def upload_string(self,key_name,input_str):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        bucket.put_object(key=key_name,data=input_str)

    def upload_file(self,key_name,local_file_path):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        with open(local_file_path,'rb') as fileobj:
            result = bucket.put_object(key=key_name,data=fileobj)
        return result

    def upload_bytes(self,key_name,object_bytes):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        if isinstance(object_bytes,bytes):
            bucket.put_object(key_name,object_bytes)
        else:
            print 'The input object should be in type \'bytes\'!'

    def download_stream(self,key_name,local_file_path):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        remote_stream = bucket.get_object(key=key_name)
        with open(local_file_path,'wb') as local_fileobj:
            shutil.copyfileobj(remote_stream,local_fileobj)

    def download_file_as_stream(self,key_name):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        return bucket.get_object(key=key_name)

    def download_file(self,key_name,local_file_path):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        bucket.get_object_to_file(key_name,local_file_path)

    def delete_file(self,key_name):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        bucket.delete_object(key_name)

    def does_file_exists(self,key_name):
        bucket = oss2.Bucket(auth=self.auth, endpoint=self.end_point, bucket_name=self.bucket_name)
        return bucket.object_exists(key_name)


if __name__ == '__main__':

    oss_config = config_default.configs['oss']

    local_file_path = os.path.abspath(os.path.join(os.getcwd(),'../..')) + '/resource/wangxiongfirst.txt'
    end_point = oss_config[u'end_point']
    access_key_id = oss_config[u'access_key_id']
    access_key_secret = oss_config[u'access_key_secret']
    bucket_name = oss_config[u'bucket_name']
    # key_name = u'recordfile/test.txt'
    key_name = u'recordfile/20180108/20180108_13816287927_13700949.txt'
    local_file_save_path = os.path.abspath(os.path.join(os.getcwd(),'../..')) + '/resource/download/wangxiongfirst.txt'
    oss_operator = OssOperator(access_id=access_key_id,access_key=access_key_secret,end_point=end_point,bucket_name=bucket_name)
    print oss_operator.does_file_exists(key_name)
    # if oss_operator.does_file_exists(bucket_name,key_name):
    #     oss_operator.delete_file(bucket_name,key_name)
    # result = oss_operator.upload_file(bucket_name,key_name,local_file_path)
    # print type(result.status)
    file_exists = oss_operator.does_file_exists(key_name)
    print file_exists
    if file_exists:
        remote_stream = oss_operator.download_file_as_stream(key_name)

    if remote_stream:
        result_list = []
        while 1:
            buf = remote_stream.read(16 * 1024)
            if not buf:
                break
            result_list.append(unicode(buf,'utf-8'))
        download_result = ''.join(result_list)
    new_key_name = u'recordfile/' + unicode(time.strftime("%Y-%m-%d",time.localtime()),encoding='utf-8') + 'wangxiongfirst.txt'
    # oss_operator.upload_bytes(bucket_name,new_key_name,download_result)
    print type(download_result)
    oss_operator.upload_string(new_key_name,download_result)

    if oss_operator.does_file_exists(new_key_name):
        new_remote_stream = oss_operator.download_file(new_key_name,local_file_save_path)
