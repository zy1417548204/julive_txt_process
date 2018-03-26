# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

import jieba

from config.rule_constants import ConstValue
from utils.nlp_tools import NLPTools
from utils.text_dealer import Preprocess


class RulesMatch(object):
    def rule_identifier(self):
        pass

class ItemRulesMatch(RulesMatch):

    def __init__(self,field_keyword_dic):
        if not field_keyword_dic:
            self.field_dic = ConstValue().simple_rule_fields
        else:
            self.field_dic = field_keyword_dic

    """Find all start indexes of input pattern that appears in input sentence.
    :param sentence: The given sentence.
    :param pattern: The pattern to be found in the sentence.
    :return: A list of first character index of matched pattern position in the sentence.
    """
    def _find_string_index(self,sentence,pattern):
        start_index = 0
        match_index_list = []
        # print "pattern type:" + str(type(pattern))
        # print "sentence type:" + str(type(sentence))
        if isinstance(pattern,str):
            pattern = pattern.decode("utf-8")
            # print "new pattern type:" + str(type(pattern))
        if isinstance(sentence,str):
            sentence = sentence.decode("utf-8")
        while sentence.find(pattern,start_index) != -1 :
            start_index = sentence.find(pattern,start_index)
            match_index_list.append(start_index)
            start_index = start_index + len(pattern)
        return match_index_list

    """Found first index list of the given keyword which appears in the given sentence, as well as the match result flag.
    :param key:
    :param sentence:
    :return: return tuple, the first element is start position of the keyword matching in the given sentence,
            and the second element is the flag whether the keyword is matched in the sentence or not.
    """
    def _match_keyword(self, key, sentence):
        match_list = self._find_string_index(sentence=sentence,pattern=key)
        is_match = False
        if len(match_list) > 0:
            is_match = True
        # print match_list,is_match
        return (match_list, is_match)

    """Found keyword matching positions in the input sentence. The matching start and end positions are offered.
    :param key: keyword to match in the given sentence
    :param sentence: input sentence where the keywords found
    :return: keyword index list found in the input sentence, the list item structure is a dict, 
             eg.: [{"start":65,"end":67},{"start":77,"end":79}], start means the beginning position of the keyword 
             appearance, while end means the ending position of the keyword appearance.
    """
    def _keyword_positions(self,key,sentence):
        match_list,is_match = self._match_keyword(key, sentence)
        match_dic = []
        if is_match:
            for index in match_list:
                start = index
                end = start + len(key)
                match_dic.append({"start":start,"end":end})
            return match_dic
        else:
            return match_dic


'''
'''
class SentenceParseRules(RulesMatch):

    def __init__(self, chi_dependency_parser):
        self.field_dic = ConstValue().simple_rule_fields
        self.chi_dependency_parser = chi_dependency_parser

    """Identify the field keywords existence in given sentence.
    :param keyword_list:
    :param sentence:
    :return: A dict type with elements: sentence, matched keywords and matched or not
    """
    def identify_sentence_with_keywords(self,keyword_list,sentence):
        matched_keyword_list = []
        for keyword in keyword_list:
            # print "keyword type: " + str(type(keyword))
            # print "sentence type: " + str(type(sentence))
            if isinstance(keyword,str):
                keyword = unicode(keyword, encoding="utf-8")

            if sentence.find(keyword) <> -1:
                matched_keyword_list.append(keyword)
                # print keyword + " " + sentence
        has_keywords = False
        if len(matched_keyword_list) > 0:
            has_keywords = True
        return {"sentence": sentence, "matched_keywords": matched_keyword_list, "has_keywords": has_keywords}

    """The dependency parser generates many word pair nodes which are not related with any keyword given.
       This function filtered out those nodes and keep those meaningful relations.
       :param keyword_list:
       :param relation_tuple_list:
       :return: 
    """
    def filter_relation_with_keywords(self,keyword_list,relation_tuple_list):
        relation_tuple_list = list(relation_tuple_list)
        filtered_tuple_list = []
        for relation_tuple in relation_tuple_list:
            has_keyword = False
            for keyword in keyword_list:
                if isinstance(keyword,str):
                    keyword = unicode(keyword,encoding="utf-8")
                if relation_tuple[0].find(keyword) <> -1 or relation_tuple[1].find(keyword) <> -1:
                    has_keyword = True
                    break
                # print "first word: " + relation_tuple[0] + " keyword: " \
                #       + keyword + " second word:" + relation_tuple[1] + " has_keywords:" + str(has_keyword)
            if has_keyword:
                filtered_tuple_list.append(relation_tuple)
                # print "first word: " + relation_tuple[0] + " keyword: " \
                #       + keyword + " second word:" + relation_tuple[1] + " has_keywords:" + str(has_keyword)
        return filtered_tuple_list

    """Combine the input tuples as a list, if the second tuple does not exist in first tuple list, combing the input
       two parameters together as one list.
    :param first_tuple: A tuple or a list with tuple objects.
    :param second_tuple: A second tuple to be combined with previous one
    :return: A list with combined tuple objects.
    """
    def merge_tuple(self,first_tuple, second_tuple):
        tuple_list = []
        if not isinstance(first_tuple,list):
            tuple_list.append(first_tuple)
        else:
            tuple_list = list(first_tuple)
        for tuple in tuple_list:
            if cmp(tuple, second_tuple) == 0:
                return tuple_list
        tuple_list.append(second_tuple)
        return tuple_list

    """Parse sentence structures from the given sentence list and field name. This function aims to learn word relation
       structures from all given json formatted sentences splitted from the training paragraphs, which were recognized
       by xunfei voice recognition service in advance.
    Process steps as following:
    1.For specified field name, select the sentences which are matched with field keywords.
    2.Parse the dependency structure for those given sentences.
    3.Filter the parse nodes with field keywords.
    4.Reduce duplicate structure
    :param rule_type_name: The input field name to be identified in given sentences
    :param sentence_list: The json format sentences segmented from paragraphs.
    :return: The tuple list of word relations learned from given sentences. eg: [("关注","核心","nsubj")]
    """
    def parse_sentence_structure(self,rule_type_name,sentence_json_list):

        keyword_list = self.field_dic.get(rule_type_name)
        sentence_field_word_structure_list = []
        for sentence_json in sentence_json_list:
            sentence = Preprocess().remove_useless(sentence_json.get(u"onebest"))
            # print sentence

            # Step 1: For specified field name, select the sentences which are matched with field keywords.
            sentence_keyword_match_dic = self.identify_sentence_with_keywords(keyword_list=keyword_list,
                                                                              sentence=sentence)
            if len(sentence_keyword_match_dic) > 0 and sentence_keyword_match_dic.get("has_keywords"):
                # Step 2: Parse the dependency structure for those given sentences.
                relation_tuple_list=self.dependency_parser(sentence)
                phrases = ConstValue().phrase_rule_fields.get(rule_type_name,[])
                if phrases:
                    for relation_tuple in relation_tuple_list:
                        phrases.append([relation_tuple[0],relation_tuple[1]])
                else:
                    phrases = relation_tuple_list
                # print relation_tuple_list
                # Step 3: Filter the parse nodes with field keywords.
                print phrases
                filtered_relation_list = self.filter_relation_with_keywords(keyword_list=keyword_list,
                                                                  relation_tuple_list=phrases)
                if len(sentence_field_word_structure_list) > 0 and len(filtered_relation_list) > 0:
                    sentence_field_word_structure_list.extend(filtered_relation_list)
                elif len(sentence_field_word_structure_list) == 0 and len(filtered_relation_list) > 0:
                    sentence_field_word_structure_list.append(filtered_relation_list)
                elif len(filtered_relation_list) == 0:
                    continue

        # Step4: Reduce the duplicate structures
        if len(sentence_field_word_structure_list) > 0:
            sentence_field_word_structure_list = reduce(self.merge_tuple,sentence_field_word_structure_list)
        return sentence_field_word_structure_list


    """Parse the input sentence with stanford dependency parser.
    :param sentence: The input sentence to be parsed.
    :return: The word pair nodes with their own word dependency relation.
    """
    def dependency_parser(self,sentence):
        nt = NLPTools()
        # segmenter = nt.define_stanford_segmenter()
        sentence_seg = " ".join(jieba.cut(sentence))
        # print sentence_seg
        res_parse_nodes = list(self.chi_dependency_parser.parse(sentence_seg.split()))
        relation_tuple_list = []
        for row in res_parse_nodes[0].triples():
            first_word = row[0][0]
            relation = row[1]
            second_word = row[2][0]
            # print first_word,second_word,relation
            relation_tuple_list.append((first_word,second_word,relation))
        return relation_tuple_list

    """Search the given words relation structures within the given sentence.
    :param sentence: The input sentence.
    :param sentence_field_word_structure_list: The word relation structure list, which relate to specified field name
           in this project.
    :return: A dictionary of the input sentence analyzed with word relation structures. eg:
            {"sentence":sentenceA,
             "sentence_structure_match_list":[
                                              {"start_position":34,
                                               "end_position":45,
                                               "relation_tuple":("关注","核心","nsubj")
                                              }
                                             ]
            }
    """
    def word_structure_match(self,sentence,sentence_field_word_structure_list):
        sentence_structure_match_list = []
        for relation_tuple in sentence_field_word_structure_list:
            first_word = relation_tuple[0]
            second_word = relation_tuple[1]
            first_word_occurrence_start = sentence.find(first_word)
            first_word_occurrence_end = first_word_occurrence_start + len(first_word)
            second_word_occurrence_start = sentence.find(second_word)
            second_word_occurrence_end = second_word_occurrence_start + len(second_word)

            if first_word_occurrence_start <> -1 and second_word_occurrence_start <> -1:
                if first_word_occurrence_start > second_word_occurrence_start:
                    word_structure_dic = {"start_position":second_word_occurrence_start,
                                          "end_position":first_word_occurrence_end,
                                          "relation_tuple":relation_tuple}
                    sentence_structure_match_list.append(word_structure_dic)
                elif first_word_occurrence_start < second_word_occurrence_start:
                    word_structure_dic = {"start_position":first_word_occurrence_start,
                                          "end_position":second_word_occurrence_end,
                                          "relation_tuple":relation_tuple}
                    sentence_structure_match_list.append(word_structure_dic)
        return {"sentence":sentence,"sentence_structure_match_list":sentence_structure_match_list}

class SimpleRuleMatch(ItemRulesMatch):

    def __init__(self,field_keyword_dic):
        super(SimpleRuleMatch,self).__init__(field_keyword_dic)

    """For those simply matching the keyword fields.
    :param rule_type_name: The specified checking field to find in given paragraph.
    :param sentence_json_list: The sentence list that segmented from an entire paragraph, with start time and end time.
    :return: A dictionary formatted like {"field":rule_type_name,
                                          "sentence_match_list":[
                                                                 {"sentence":sentenceA, 
                                                                  "keywords_positions":
                                                                                       [
                                                                                        {"keyword_name":keyword_nameA,
                                                                                         "positions":
                                                                                                      [
                                                                                                       {"start":65,"end":67},
                                                                                                       {"start":77,"end":79}
                                                                                                      ]
                                                                                        }
                                                                                       ]
                                                                  "start_time":"72400",
                                                                  "end_time":"91610"
                                                                 }
                                                                ]
                                         }
    """
    def rule_identifier(self,rule_type_name,sentence_json_list):
        field_list = self.field_dic
        field_match_dic = {}
        if not isinstance(rule_type_name, unicode):
            rule_type_name = unicode(rule_type_name, "utf-8")
        field_match_dic.update({u"rule_type_name": rule_type_name})
        sentence_match_list = []

        for sentence_json in sentence_json_list:
            sentence = sentence_json.get(u"onebest","")
            start_time = sentence_json.get(u"bg","")
            end_time = sentence_json.get(u"ed","")
            speaker = sentence_json.get(u"speaker","")
            sentence_key = sentence_json.get(u"sentence_key","")
            keywords = field_list.get(rule_type_name)
            keywords_positions = []
            for keyword in keywords:
                if not isinstance(keyword, unicode):
                    keyword = unicode(keyword, "utf-8")
                single_keyword_positions = super(SimpleRuleMatch,self)._keyword_positions(key=keyword,
                                                                   sentence=sentence)
                if single_keyword_positions:
                    keywords_positions.append(
                        {u"keyword_name": keyword, u"positions": single_keyword_positions}
                    )
            if keywords_positions:
                sentence_json.update({u"sentence": sentence, u"keywords_positions" : keywords_positions})
                del sentence_json[u"onebest"]
                sentence_match_list.append(sentence_json)
                # sentence_match_list.append({u"sentence": sentence,
                #                             u"sentence_key": sentence_key,
                #                             u"keywords_positions": keywords_positions,
                #                             u"speaker": speaker,
                #                             u"start_time": start_time, u"end_time": end_time})
        field_match_dic.update({u"sentence_match_list": sentence_match_list})
        if sentence_match_list:
            field_match_dic.update({u"rule_val":101})
        else:
            field_match_dic.update({u"rule_val":102})
        return field_match_dic

class CompositeRuleMatch(ItemRulesMatch):
    def __init__(self,field_keyword_dic):
        super(CompositeRuleMatch,self).__init__(field_keyword_dic)

    """
    :param rule_type_name_dic: The structure looks like this....
                            {
                             "rule_type_name":"资质"
                             "sub_rule_type_name_list":["户籍","纳税","社保","信贷能力","名下房产","资质本身"]
                            }
    :param sentence_json_list: The sentence list that segmented from an entire paragraph, with start time and end time.
    :return: A dictionary formatted like {"field":rule_type_name,
                                          "sentence_match_list":[
                                                                  {"sub_rule_type_name":sub_rule_type_nameA,
                                                                   "sub_field_match_list":[
                                                                                          {"sentence":sentenceA, 
                                                                                           "keywords_positions":
                                                                                                                [
                                                                                                                 {"keyword_name":keyword_nameA,
                                                                                                                  "positions":
                                                                                                                               [
                                                                                                                                {"start":65,"end":67},
                                                                                                                                {"start":77,"end":79}
                                                                                                                               ]
                                                                                                                 }
                                                                                                                ]
                                                                                           "start_time":"72400",
                                                                                           "end_time":"91610"
                                                                                          }
                                                                                        ]
                                                                  }
                                                                 ]
                                         }
    """
    def rule_identifier(self,rule_type_name,sentence_json_list):
        field_match_dic = {}

        composite_rule_dic = ConstValue().composite_rule_fields
        sub_rule_type_name_list = composite_rule_dic.get(rule_type_name, [])
        field_dic = self.field_dic
        rule_val = 102

        if not isinstance(rule_type_name, unicode):
            rule_type_name = unicode(rule_type_name, encoding="utf-8")
        sentence_match_list = []
        for sentence_json in sentence_json_list:
            sentence = sentence_json.get(u"onebest","")
            # start_time = sentence_json.get(u"bg","")
            # end_time = sentence_json.get(u"ed","")
            # speaker = sentence_json.get(u"speaker","")
            # sentence_key = sentence_json.get(u"sentence_key")
            keywords_positions = []
            for sub_rule_type_name in sub_rule_type_name_list:
                keywords_list = field_dic.get(sub_rule_type_name, [])
                for keyword in keywords_list:
                    if not isinstance(keyword, unicode):
                        keyword = unicode(keyword, encoding="utf-8")
                    single_keyword_positions = super(CompositeRuleMatch,self)._keyword_positions(key=keyword, sentence=sentence)
                    if single_keyword_positions:
                        keywords_positions.append(
                            {u"keyword_name": keyword, u"positions": single_keyword_positions}
                        )
            if keywords_positions:
                sentence_json.update({u"sentence": sentence, u"keywords_positions": keywords_positions})
                del sentence_json[u"onebest"]
                sentence_match_list.append(sentence_json)
                # sentence_match_list.append({u"sentence": sentence,
                #                             u"sentence_key": sentence_key,
                #                             u"keywords_positions": keywords_positions,
                #                             u"speaker": speaker,
                #                             u"start_time": start_time, u"end_time": end_time})
        field_match_dic.update({u"rule_type_name": rule_type_name,u"sentence_match_list": sentence_match_list})
        if sentence_match_list:
            rule_val = 101
        field_match_dic.update({u"rule_val":rule_val})
        return field_match_dic

class PhraseRuleMatch(SentenceParseRules):

    def __init__(self,chi_dependency_parser):
        super(PhraseRuleMatch,self).__init__(chi_dependency_parser)
        self.simple_rule_fields = ConstValue().simple_rule_fields
        self.phrase_rule_fields = ConstValue().phrase_rule_fields

    """Identify field name by phrase rule match
    :param rule_type_name: 
    :param sentence_list:
    :return
    """
    def rule_identifier(self,rule_type_name,sentence_list):

        field_match_dic = {}
        if not isinstance(rule_type_name, unicode):
            rule_type_name = unicode(rule_type_name, encoding="utf-8")
        field_match_dic.update({u"rule_type_name":rule_type_name})
        sentence_match_list = []

        sentence_field_word_structure_list = self.parse_sentence_structure(rule_type_name)

        for sentence_json in sentence_list:
            sentence = sentence_json.get(u"onebest","")
            # start_time = sentence_json.get(u"bg","")
            # end_time = sentence_json.get(u"ed","")
            # speaker = sentence_json.get(u"speaker","")
            # sentence_key = sentence_json.get(u"sentence_key")

            sentence_match_dic = self.word_structure_match(sentence,sentence_field_word_structure_list)
            if sentence_match_dic:
                sentence_match_dic.update(sentence_json)
                del sentence_match_list[u"onebest"]
                # sentence_match_dic.update({
                #                             u"sentence":sentence,
                #                             u"sentence_key":sentence_key,
                #                             u"start_time": start_time,
                #                             u"end_time": end_time,
                #                             u"speaker": speaker
                #                         })
                sentence_match_list.append(sentence_match_dic)
        if sentence_match_list:
            return {u"rule_type_name":rule_type_name,u"sentence_match_list":sentence_match_list,u"rule_val":101}
        else:
            return {u"rule_type_name":rule_type_name,u"sentence_match_list":sentence_match_list,u"rule_val":102}

    def parse_sentence_structure(self,rule_type_name):
        simple_dic = self.simple_rule_fields.get(rule_type_name,[])
        phrase_dic = self.phrase_rule_fields.get(rule_type_name,[])
        return {u"simple_dic":simple_dic,u"phrase_dic":phrase_dic}

    def word_structure_match(self,sentence,sentence_field_word_structure_list):
        sentence_structure_match_list = []
        simple_dic = []
        if isinstance(sentence_field_word_structure_list,dict):
            simple_dic = sentence_field_word_structure_list.get(u"simple_dic",[])
            phrase_dic = sentence_field_word_structure_list.get(u"phrase_dic",[])

        if simple_dic:
            for label in simple_dic:
                # print label + " " +  str(type(label))
                word_occurrence_start = sentence.find(label)
                if word_occurrence_start <> -1:
                    word_occurrence_end = word_occurrence_start + len(label)
                    word_structure_dic = {u"keyword_name":label,
                                          u"start": word_occurrence_start,
                                          u"end": word_occurrence_end}
                    sentence_structure_match_list.append(word_structure_dic)
        if phrase_dic:
            for phrase in phrase_dic:
                first_word = phrase[0]
                second_word = phrase[1]
                first_word_occurrence_start = sentence.find(first_word)
                first_word_occurrence_end = first_word_occurrence_start + len(first_word)
                second_word_occurrence_start = sentence.find(second_word)
                second_word_occurrence_end = second_word_occurrence_start + len(second_word)

                if first_word_occurrence_start <> -1 and second_word_occurrence_start <> -1:
                    if first_word_occurrence_start > second_word_occurrence_start:
                        word_structure_dic = {u"keyword_name":first_word + "..." + second_word,
                                              u"start": second_word_occurrence_start,
                                              u"end": first_word_occurrence_end}
                        sentence_structure_match_list.append(word_structure_dic)
                    elif first_word_occurrence_start < second_word_occurrence_start:
                        word_structure_dic = {u"keyword_name":first_word + "..." + second_word,
                                              u"start": first_word_occurrence_start,
                                              u"end": second_word_occurrence_end}
                        sentence_structure_match_list.append(word_structure_dic)
        if sentence_structure_match_list:
            return {u"keywords_positions": sentence_structure_match_list}
        else:
            return {}

class TacticRulesMatch(ItemRulesMatch):

    def __init__(self,field_keyword_dic):
        super(TacticRulesMatch,self).__init__(field_keyword_dic)
        self.tactic_rule_fields = ConstValue().tactic_rule_fields

    """Identify field name by tactic rule, which means the input should meet all requirements in a tactic rule 
    """
    def rule_identifier(self,rule_type_name,sentence_json_list):
        field_dic = self.tactic_rule_fields.get(rule_type_name,{})
        if isinstance(field_dic,dict):
            sentence_match_list = []
            for sentence_json in sentence_json_list:
                corrected_keywords_list = sentence_json.get(u"corrected_keywords_list",[])
                sentence = sentence_json.get(u"onebest","")
                # start_time = sentence_json.get(u"bg","")
                # end_time = sentence_json.get(u"ed","")
                # speaker = sentence_json.get(u"speaker","")
                # sentence_key = sentence_json.get(u"sentence_key")
                rule_val = 102
                if not corrected_keywords_list:
                    continue
                else:
                    keywords_positions = []
                    for corrected_dic in corrected_keywords_list:
                        corrected_keyword = corrected_dic.get(u"corrected_keyword", "")
                        single_keyword_positions = super(TacticRulesMatch, self)._keyword_positions(
                            key=corrected_keyword,
                            sentence=sentence)
                        if single_keyword_positions:
                            keywords_positions.append(
                                {u"keyword_name": corrected_keyword, u"positions": single_keyword_positions}
                            )
                    # if len(corrected_keywords_list) == len(field_dic):
                    #     is_qualified = True
                    if keywords_positions:
                        sentence_json.update({u"sentence": sentence, u"keywords_positions": keywords_positions})
                        sentence_match_list.append(sentence_json)
                        # sentence_match_list.append({u"sentence": sentence,
                        #                             u"sentence_key": sentence_key,
                        #                             u"keywords_positions": keywords_positions,
                        #                             u"start_time": start_time,
                        #                             u"end_time": end_time,
                        #                             u"speaker": speaker})
            if sentence_match_list:
                rule_val = 101

            return {u"rule_type_name": rule_type_name, u"sentence_match_list": sentence_match_list, u"rule_val": rule_val}

        else:
            print "The input field dictionary should be in \"dict\" type!"
