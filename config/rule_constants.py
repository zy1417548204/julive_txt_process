#!/usr/bin/python
# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

import os

class ConstValue(object):

    project_root = os.path.abspath(os.path.join(os.getcwd()))

    fetch_voices_sql = 'select talk.record_file_url, talk.record_file_aliyun_url, talk.record_txt_json_url,talk.order_id, ' \
                       'relation.business_id,relation.record_id ' \
                       'from ' \
                       '(select * ' \
                       'from yw_sys_number_talking talking' \
                       ' where order_id in (20014934,20014936,20014937,20014939,20014950,20014951,20014952,20014958,20014960,20014969,20014971,20014994,20014999,20015016,20015017,20015020,' \
                       '20015021,20015220,20015462,20015463,20015464,20015465,20015466,20015468,20015470,20015471,20015473,20015467,20015476,20015479,20015480,20015483,' \
                       '20015485,20015487,20015491,20015495,20015500,20015501,20015503,20014904,20015506,20015507,20015509,20015511,20015513,20015515,20015516,20015518,' \
                       '20015519,20015521,20015523,20015524,20015532,20015049,20015382,20015535,20015536,20015546,20015550,20015551,20015417,20015554,20015573,20015574,' \
                       '20015575,20015580,20015582,20015586,20015587,20015588,20015589,20015591,20015595,20015592,20015576,20015598,20015599,20015600,20015601,20015603,' \
                       '20015604,20015605,20015607,20015608,20015609,20015610,20015611,20015612,20015613,20015614,20015615,20015616,20015617,20015625,20015629,20015630,' \
                       '20015639,20015641,20015644,20015645,20015981,20016008)) talk,' \
                       '(select record_id,business_id ' \
                       'from yw_talk_audio_relation relation ' \
                       'where relation.lable_type = 1 ' \
                       'and relation.business_type = 1 ' \
                       'and relation.lable_val = 100) relation ' \
                       'where talk.id = relation.record_id ' \
                       'and talk.record_file_aliyun_url <> \'\' ' \
                       'and talk.record_txt_json_url <> \'\''

    sql_for_test = 'select relation.record_id, relation.business_id,talk.record_file_url, talk.record_file_aliyun_url, talk.record_txt_json_url,talk.order_id,' \
                   'rule.rule_type,rule.rule_type_name,rule.rule_match_json,rule.rule_val ' \
                   'from ' \
                   '(select * ' \
                   'from yw_sys_number_talking talking ' \
                   'where order_id in (20014934,20014936,20014937,20014939,20014950,20014951,20014952,20014958,20014960,20014969,20014971,20014994,20014999,20015016,20015017,20015020,' \
                   '20015021,20015220,20015462,20015463,20015464,20015465,20015466,20015468,20015470,20015471,20015473,20015467,20015476,20015479,20015480,20015483,' \
                   '20015485,20015487,20015491,20015495,20015500,20015501,20015503,20014904,20015506,20015507,20015509,20015511,20015513,20015515,20015516,20015518,' \
                   '20015519,20015521,20015523,20015524,20015532,20015049,20015382,20015535,20015536,20015546,20015550,20015551,20015417,20015554,20015573,20015574,' \
                   '20015575,20015580,20015582,20015586,20015587,20015588,20015589,20015591,20015595,20015592,20015576,20015598,20015599,20015600,20015601,20015603,' \
                   '20015604,20015605,20015607,20015608,20015609,20015610,20015611,20015612,20015613,20015614,20015615,20015616,20015617,20015625,20015629,20015630,' \
                   '20015639,20015641,20015644,20015645,20015981,20016008)) talk,' \
                   '(select record_id,business_id ' \
                   'from yw_talk_audio_relation relation ' \
                   'where relation.lable_type = 1 ' \
                   'and relation.business_type = 1 ' \
                   'and relation.lable_val = 100) relation, ' \
                   'yw_first_call_extarct_info rule ' \
                   'where talk.id = relation.record_id ' \
                   'and rule.contact_id = relation.business_id ' \
                   'and rule.record_id = relation.record_id ' \
                   'and talk.record_file_aliyun_url <> \'\' ' \
                   'and talk.record_file_aliyun_url <> \'\' ' \
                   'order by relation.record_id'

    def __init__(self):
        # load house type dictionary

        voice_tag_list = [u'speaker', u'bg', u'ed', u'onebest']
        dic_folder_path = os.path.abspath(os.path.join(os.getcwd())) + '/project_dic'
        districts = [u'区域', u'工作地点', u'上班', u'工作', u'公司', u'单位']
        districts.extend([unicode(district.strip(),encoding='utf-8') for district in open(dic_folder_path+'/cj_district.dic').readlines()])
        house_types = [unicode(type.strip(),encoding='utf-8') for type in open(dic_folder_path+'/house_type.dic', 'rb').readlines()]
        employee_names = [unicode(name.strip(),encoding='utf-8') for name in open(dic_folder_path+'/employee_name.dic', 'rb').readlines()]

        self.simple_fields = [u'推荐APP',u'加微信',u'目的',u'面积',u'户型']
        self.composite_fields = [u'预算',u'资质']
        self.phrase_fields = [u'节点',u'区域',u'邀约']
        self.complex_tactic_fields = [u'自我介绍']

        self.simple_rule_fields = {
            u'推荐APP': [u'APP', u'app', u'下载'],
            u'加微信': [u'微信'],
            u'目的': [u'自住', u'自己住', u'投资', u'置换'],
            u'面积': [u'平米', u'平方米'],
            u'户型': house_types,
            u'总价预算': [u'总价', u'预算', u'总价预算', u'总房款'],
            u'首付预算': [u'首付', u'比例'],
            u'户籍': [u'户口', u'户籍', u'本市', u'外地', u'本地'],
            u'纳税': [u'纳税', u'六十个月'],
            u'社保': [u'社保', u'五年'],
            u'信贷能力': [u'首套', u'二套', u'限购', u'限贷', u'贷款'],
            u'名下房产': [u'名下', u'几套房', u'有无房', u'有没有房'],
            u'资质本身': [u'资质'],
            u'邀约': [u'实地', u'周末', u'平时', u'周六', u'周日', u'看房', u'抽时间', u'有时间', u'看看', u'有空吗'],
            u'区域': districts,
            u'节点': [u'回电话', u'打电话', u'去电话', u'地点']
        }

        self.composite_rule_fields = {
            u'预算': [u'总价预算', u'首付预算'],
            u'资质': [u'资质本身', u'户籍', u'纳税', u'社保', u'信贷能力', u'名下房产']
        }

        self.phrase_rule_fields = {
            u'节点': [
                [u'有空', u'时候'], [u'时候', u'有时间'], [u'时候', u'有空'], [u'时间',u'有空'], [u'时候',u'方便'],
                [u'时间', u'方便'], [u'方便', u'接电话'], [u'约', u'时候'], [u'约', u'地方']
            ],
            u'区域': [
                [u'哪个', u'区域'], [u'工作', u'地点'], [u'哪里', u'上班']
            ],
            u'邀约': [
                [u'实地', u'看房'], [u'周末', u'方便'], [u'工作日', u'方便']
            ]
        }

        self.tactic_rule_fields = {
            u'自我介绍': {
                u'公司品牌': [u'居理新房', u'侃家网'],
                u'称号': [u'咨询师'],
                u'员工名称': employee_names
            }
        }

        self.rule_type_dic = {
            u"自我介绍":1,
            u"邀约":2,
            u"推荐APP":3,
            u"节点":4,
            u"加微信":5,
            u"资质":6,
            u"预算":7,
            u"目的":8,
            u"区域":9,
            u"面积":10,
            u"户型":11
        }

