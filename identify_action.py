# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

import datetime
import hashlib
import json
import logging.config
import os
import sys
import time
from multiprocessing import Pool, Manager

import config.config_default as config_default
from config.rule_constants import ConstValue
from database.mysql_tools import MysqlOperation, MysqlConnection
from database.oss_tools import OssOperator
from extract_label.extract_rules import SimpleRuleMatch, CompositeRuleMatch, PhraseRuleMatch, RulesMatch, TacticRulesMatch
from utils.nlp_tools import NLPTools
from words_correction.estate_corrector.corrector_factory import LMRulesCorrector
from words_correction.estate_corrector.corrector_rules import LMRules

project_root = ConstValue.project_root
logging.config.fileConfig(project_root + "/log/logging.conf")
logger_name = "identify-qualification"
logger = logging.getLogger(logger_name)

class MysqlBLogic(object):

    @classmethod
    def get_file_addresses(cls,connection = MysqlConnection(),sql_operation = MysqlOperation()):
        query_sql = ConstValue.fetch_voices_sql
        result = sql_operation.select_data(query_sql, connection)
        if not result:
            logger.error("No data fetched from database!")
        return result

    @classmethod
    def update_table_fields(cls,deal_result_list,connection = MysqlConnection(),sql_operation = MysqlOperation()):
        ### Update the database
        ai_deal_status = 0
        relate_id_dic = {}
        for identify_result_str in deal_result_list:
            identify_result = json.loads(identify_result_str)
            rule_type_name = identify_result.get(u"rule_type_name")
            rule_val = identify_result.get(u"rule_val")
            business_id = identify_result.get(u"business_id")
            record_id = identify_result.get(u"record_id")
            rule_type = rule_type_dic.get(rule_type_name, -1)
            current_time = int(round(time.time()))
            try:
                update_sql = "REPLACE INTO yw_first_call_extarct_info (contact_id,record_id,rule_type,rule_val," \
                             "rule_match_json,create_datetime,update_datetime,rule_type_name) values " \
                             "('%d','%d','%d','%d','%s','%d','%d','%s')" % \
                             (business_id, record_id, rule_type, rule_val, identify_result_str, current_time,
                              current_time, rule_type_name)
                sql_operation.update_data(sql=update_sql, connection=connection)
                relate_key = unicode(business_id) + "-" + unicode(record_id)
                if not relate_id_dic.has_key(relate_key):
                    relate_id_dic.update({relate_key: {u"business_id": business_id, u"record_id": record_id}})
            except:
                ai_deal_status = 2
                logger.error("Error when update database with result: " + identify_result_str)

        ### Update the field `ai_deal_status` in yw_talk_audio_relation, after checking all the items for one input file.
        for key, value in relate_id_dic.iteritems():
            business_id = value.get(u"business_id")
            record_id = value.get(u"record_id")
            check_count_sql = "SELECT count(*) as num FROM yw_first_call_extarct_info WHERE contact_id = '%d' " \
                              "AND record_id = '%d' AND rule_val = 101 OR 102" % (business_id, record_id)
            check_count_result = sql_operation.select_data(sql=check_count_sql, connection=connection)
            check_item_count = check_count_result[0].get(u"num", 0)
            if check_item_count == 11 and ai_deal_status <> 2:
                ai_deal_status = 1
            elif check_item_count < 11 and ai_deal_status <> 2:
                ai_deal_status = 0
            elif identify_result.get(u"ai_deal_status", 2) == 2:
                ai_deal_status = 2
            update_relation_sql = "UPDATE yw_talk_audio_relation SET ai_deal_status = '%d' WHERE business_id = '%d' " \
                                  "AND record_id = '%d'" % (ai_deal_status, business_id, record_id)
            sql_operation.update_data(sql=update_relation_sql, connection=connection)

class TextFileObject(object):

    @classmethod
    def from_oss(cls,result_list,oss_operator):
        object_list = []
        for item_dic in result_list:
            if isinstance(item_dic, dict):
                business_id = item_dic.get(u"business_id", 0)
                record_id = item_dic.get(u"record_id", 0)
                record_txt_json_url = item_dic.get(u"record_txt_json_url", "")
                if record_txt_json_url:

                    remote_stream = oss_operator.download_file_as_stream(key_name=record_txt_json_url[1:])
                    file_sentence_list = []
                    if remote_stream:
                        result_list = []
                        while 1:
                            buf = remote_stream.read(1024 * 1024)
                            if not buf:
                                break
                            else:
                                print type(buf),buf
                                result_list.append(unicode(buf, "utf8"))
                        for sub_list in result_list:
                            for item in json.loads(sub_list):
                                # extract_json = {u"onebest": item.get(u"onebest", ""),
                                #                 u"bg": item.get(u"start_time", ""),
                                #                 u"ed": item.get(u"end_time", ""),
                                #                 u"speaker": item.get(u"speaker", "")}
                                file_sentence_list.append(item)
                    object_list.append({u"business_id": business_id, u"record_id": record_id,
                                        u"file_url": record_txt_json_url, u"file_sentence_list": file_sentence_list})
        return object_list

    @classmethod
    def from_local_file(cls,local_file_path):
        ## To be continued....
        file_name_list = os.listdir(local_file_path)
        object_list = []
        i = 0
        while i < len(file_name_list):
            file_name = file_name_list[i]
            file_path = local_file_path + "/" + file_name

            file = open(file_path, "rb")
            file_json = json.load(file, encoding="utf-8")
            sentence_json_list = []
            id = 0
            for line in file_json:
                if isinstance(line, dict):
                    sentence_key = hashlib.md5(unicode(line)).hexdigest()

                    line.update({u"id": id})
                    line.update({u"sentence_key": sentence_key})
                    id += 1
                sentence_json_list.append(line)
            object_list.append({})
            file.close()

class ActionIdentifier(object):

    def __init__(self, simple_fields=ConstValue().simple_fields,
                 composite_fields=ConstValue().composite_fields,
                 phrase_fields=ConstValue().phrase_fields,
                 simple_rule_fields=ConstValue().simple_rule_fields,
                 composite_rule_fields=ConstValue().composite_rule_fields,
                 phrase_rule_fields=ConstValue().phrase_rule_fields,
                 tactic_rule_fields=ConstValue().tactic_rule_fields,
                 chi_denpendency_parser=NLPTools().define_stanford_dependency_parser(),
                 corrector=LMRulesCorrector(LMRules())):
        self.__simple_fields = simple_fields
        self.__composite_fields = composite_fields
        self.__phrase_fields = phrase_fields
        self.__composite_rule_fields = composite_rule_fields
        self.__simple_rule_fields = simple_rule_fields
        self.__phrase_rule_fields = phrase_rule_fields
        self.__tactic_rule_fields = tactic_rule_fields
        self.__chi_dependency_parser = chi_denpendency_parser
        self.corrector = corrector

    def action(self,rule_type_name,sentences_json_list,file_name=u"",business_id=0,record_id=0):
        identify_result = {}
        proc_status = 1
        try:
            if self.__simple_rule_fields.has_key(rule_type_name):
                simple_rule_identifier = SimpleRuleMatch(self.__simple_rule_fields)
                identify_result = self.identifier(rule_type_name, sentences_json_list, simple_rule_identifier)
            elif self.__composite_rule_fields.has_key(rule_type_name):
                composite_rule_identifier = CompositeRuleMatch(self.__simple_rule_fields)
                identify_result = self.identifier(rule_type_name, sentences_json_list, composite_rule_identifier)
            elif self.__phrase_rule_fields.has_key(rule_type_name):
                phrase_rule_identifier = PhraseRuleMatch(self.__chi_dependency_parser)
                identify_result = self.identifier(rule_type_name, sentences_json_list, phrase_rule_identifier)
            elif self.__tactic_rule_fields.has_key(rule_type_name):
                if rule_type_name == u"自我介绍":
                    dic = self.__tactic_rule_fields.get(rule_type_name, {})
                    pending_sentence_list = self.keyword_corrector(sentence_jlist=sentences_json_list,
                                                                   rule_dic=dic)

                    tactic_rule_identifier = TacticRulesMatch(self.__simple_rule_fields)
                    identify_result = self.identifier(rule_type_name=rule_type_name,
                                                      sentences_json_list=pending_sentence_list,
                                                      rules=tactic_rule_identifier)
            else:
                proc_status = 2
                identify_result.update({u"rule_type_name": rule_type_name,
                                        u"rule_val": 103, u"sentence_match_list": []})
        except:
            proc_status = 2
            identify_result.update({u"rule_type_name": rule_type_name,
                                    u"rule_val": 104, u"sentence_match_list": []})
            logger.error(u"Parse error when process item with business_id = "+str(business_id) +
                         u" record_id = " + str(record_id) + u" rule_type_name = " + rule_type_name)

        identify_result.update({u"file_name":file_name,u"business_id":business_id,u"record_id":record_id})
        identify_result.update({u"proc_status":proc_status})
        return identify_result

    def keyword_corrector(self, sentence_jlist, rule_dic):
        corrected_sentence_list = []
        for sentence_json in sentence_jlist:
            if sentence_json.get(u"id", "") < 3:
                corrected_sentence_list.append(sentence_json)
            else:
                break
        idx = 0
        for sentence_json in corrected_sentence_list:

            sentence = sentence_json.get(u"onebest", "")
            if not isinstance(sentence, unicode):
                sentence = unicode(sentence, encoding="utf-8")
            corrected_keywords_list = []

            for key, keywords in rule_dic.items():

                selected_candidates = self.candidate_selector(keywords, sentence)
                onebest, is_corrected, corrected_keyword = self.replace_error(
                    selected_candidates,corrected_sentence_list[idx].get(u"onebest",""))
                corrected_sentence_list[idx].update({u"onebest": onebest})
                if is_corrected:
                    corrected_keywords_list.append({u"key": key, u"corrected_keyword": corrected_keyword})

                if corrected_keywords_list:
                    is_corrected = True

            corrected_sentence_list[idx].update({u"is_corrected": is_corrected,
                                                 u"corrected_keywords_list": corrected_keywords_list})
            idx += 1
        return corrected_sentence_list


    def identifier(self,rule_type_name,sentences_json_list=[],rules=RulesMatch()):
        return rules.rule_identifier(rule_type_name,sentences_json_list)

    def replace_error(self,selected_candidates,sentence):

        if selected_candidates:
            candidate = selected_candidates[0][2]
            keyword = selected_candidates[0][0]
            if isinstance(sentence,unicode):
                sentence = sentence.replace(candidate,keyword)
            return sentence,True,keyword
        else:
            return sentence,False,""

    """
    """
    def candidate_selector(self,keywords,sentence):
        candidate_list = []
        for keyword in keywords:
            if not isinstance(keyword,unicode):
                keyword = unicode(keyword,encoding="utf-8")
            candidates = self.corrector.direct_error_sentence(words_input=sentence, keyword=keyword, threshold=5)
            if candidates:
                candidate_list.append((keyword,candidates[0][1],candidates[0][0]))
            sorted_candidates = sorted(candidate_list,key=lambda candidate:candidate[1])
        return sorted_candidates

""" Latest version, the main function for multi-processing model
"""
def identify_proc(file_dic,rule_type_names,update_list,index):

    logger.info("Run task %s (%s)..." % (index, os.getpid()))

    for rtype_name in rule_type_names:

        item_identify_result = ai.action(rule_type_name=rtype_name,
                                         sentences_json_list=file_dic.get(u"sentence_json_list", []),
                                         file_name=file_dic.get(u"file_name", u""),
                                         business_id=file_dic.get(u"business_id", 0),
                                         record_id=file_dic.get(u"record_id", 0))

        file_name = item_identify_result.get(u"file_name")
        rtype_name = item_identify_result.get(u"rule_type_name")
        pre_str = file_name + "-" + rtype_name
        item_identify_result_str = json.dumps(item_identify_result, encoding="utf8", ensure_ascii=False)
        update_list.append(item_identify_result_str)
        logger.info(pre_str + ": " + item_identify_result_str)

def multi_processing(file_num):
    logger.info("Parent process %s." % os.getpid())
    p = Pool()

    ai_deal_list = Manager().list()
    i = 0
    while i < file_num:
        file_object = file_object_list[i]
        file_name = file_object.get(u"file_url", "").replace(u".txt", u"_identified.txt")
        sentence_json_list = file_object.get(u"file_sentence_list", [])
        business_id = file_object.get(u"business_id", 0)
        record_id = file_object.get(u"record_id", 0)
        id = 0
        for line in sentence_json_list:
            if isinstance(line, dict):
                sentence_key = hashlib.md5(unicode(line)).hexdigest()
                line.update({u"id": id})
                line.update({u"sentence_key": sentence_key})
                sentence_json_list[id] = line
                id += 1
        file_dic = {u"file_name": file_name, u"sentence_json_list": sentence_json_list,
                    u"business_id": business_id, u"record_id": record_id}
        p.apply_async(identify_proc, args=(file_dic, rule_type_names, ai_deal_list, i))
        i += 1
    logger.info("Waiting for all subprocesses done...")
    p.close()
    p.join()

    logger.info("All subprocesses done.")
    endtime = datetime.datetime.now()
    elapse = (endtime - starttime).seconds
    logger.info("Time used: " + str(elapse))

    return ai_deal_list

if __name__ == "__main__":

    # args = sys.argv
    # if len(args) == 1 and os.path.exists(args[0]) and os.path.isdir(args[0]):
    #     if not os.listdir(args[0]):
    #         print u"The input folder is empty!"
    #
    #
    # elif len(args) > 0:
    #     print u"Please enter a correct folder path!"
    # else:
        ### Fetch the oss addresses of input texts
        logger.info("Start connecting mysql database...")
        connection = MysqlConnection()
        sql_operation = MysqlOperation()
        result = MysqlBLogic.get_file_addresses(connection=connection,sql_operation=sql_operation)

        ### Establish oss connection and download the input texts from oss
        logger.info("Start loading file object...")
        oss_config = config_default.configs[u"oss"]
        end_point = oss_config[u"end_point"]
        access_key_id = oss_config[u"access_key_id"]
        access_key_secret = oss_config[u"access_key_secret"]
        bucket_name = oss_config[u"bucket_name"]
        oss_operator = OssOperator(access_id=access_key_id, access_key=access_key_secret,
                                   end_point=end_point, bucket_name=bucket_name)
        file_object_list = TextFileObject.from_oss(result_list=result,oss_operator=oss_operator)

        ### Iteratively identify the quality checking items for input texts, and upload the results to oss,
        ### as well as save storage addresses in database
        logger.info("Preparing the main dictionary...")
        starttime = datetime.datetime.now()
        ai = ActionIdentifier()
        # ooperator = ObjectOperator()

        CV = ConstValue()
        ## Load all check items
        rule_type_names = CV.simple_fields
        rule_type_names.extend(CV.composite_fields)
        rule_type_names.extend(CV.phrase_fields)
        rule_type_names.extend(CV.complex_tactic_fields)
        ## A corresponding dictionary map the relationship of rule_type and rule_type_name
        rule_type_dic = CV.rule_type_dic

        ### Start identification using a 'Multiprocessing Model'
        online_file_num = len(file_object_list)
        dealed_list = multi_processing(file_num=online_file_num)

        ### Update the database
        MysqlBLogic.update_table_fields(deal_result_list=dealed_list, connection=connection, sql_operation=sql_operation)
        connection.commit()
        connection.close()