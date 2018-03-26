# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:
from utils.text_dealer import Converter,Preprocess
from corrector_rules import LMRules

class LMRulesCorrector():

    def __init__(self,rules=LMRules()):
        self.rules = rules

    '''Calculate the edit distance between input two words.
    :param word1:
    :param word2:
    :return: The edit distance between the two input words
    '''
    def normal_leven(self,word1,word2):
        len1 = len(word1) + 1
        len2 = len(word2) + 1
        # create matrix
        matrix = [0 for n in range(len1 * len2)]
        # init x axis
        for i in range(len1):
            matrix[i] = i
        # init y axis
        for j in range(0,len(matrix),len1):
            if j % len1 == 0:
                matrix[j] = j
        for i in range(1,len1):
            for j in range(1,len2):
                if word1[i-1] == word2[j-1]:
                    cost = 0
                else:
                    cost = 1
                matrix[j*len1+i] = min(matrix[(j-1)*len1+i] + 1,
                                       matrix[j*len1+(i-1)] + 1,
                                       matrix[(j-1)*len1+(i-1)] + cost)
        return matrix[-1]

    def filter_candidate(self,candidates_pair_list,threshold):
        filtered_candidates = []
        for item in candidates_pair_list:
            if isinstance(item[1],int):
                if item[1] < threshold:
                    filtered_candidates.append(item)

        return filtered_candidates

    '''Filter the keyword candidates with input threshold, if candidate edit distance was smaller than threshold, it
       could be added into the output list.
       :param ngram:
       :param keyword:
       :param threshold:
       :return:
    '''
    def filter_keyword_candidates(self,ngram,keyword,threshold):
        keyword_py = Converter().get_word_pinyin(keyword)
        ngram_py_dic = Preprocess().create_pypair(ngram)
        candidates_dic = {}
        for key in ngram_py_dic.keys():
            value_py = ngram_py_dic.get(key)
            dist = self.normal_leven(keyword_py, value_py)
            candidates_dic.update({key: dist})
        sorted_candidates = sorted(candidates_dic.items(), key=lambda item: item[1])

        filtered_candidates = self.filter_candidate(sorted_candidates, threshold)
        return filtered_candidates


    '''This method use keyword finding errors within given sentence proactively
    :param sentence: 
    :param keyword: 
    :return 
    '''
    def create_keyword_candidates(self,wordsinput,keyword):
        ngram = []
        # rules = LMRules()
        n = len(keyword)
        if isinstance(wordsinput, unicode):
            if n == 2:
                ngram = self.rules.seq_collect_2gram(wordsinput)
            elif n == 3:
                ngram = self.rules.seq_collect_3gram(wordsinput)
            elif n == 4:
                ngram = self.rules.seq_collect_4gram(wordsinput)
        elif isinstance(wordsinput, list):
            if n == 2:
                ngram = self.rules.list_collect_2gram(wordsinput)
            elif n == 3:
                ngram = self.rules.list_collect_3gram(wordsinput)
            elif n == 4:
                ngram = self.rules.list_collect_4gram(wordsinput)
        # filtered_candidates = self.create_keyword_candidates(ngram,keyword,threshold)
        return ngram

    '''Given the input keyword, to find out the most possible word appears in the sentence. For the purpose of correction,
     this method also generates the suggested candidates which should be relating with the keyword.
    :param words_input: The input sentence or words list, the first version supports sentence only.
    :param keyword: The subject word to be found in a sentence.
    :param threshold: The maximum value for error deviation.
    :return: The suggested candidates for error correction.
    '''
    def direct_error_sentence(self,words_input,keyword,threshold):
        if isinstance(words_input,unicode):
            if not isinstance(keyword,unicode):
                raise Exception("The input keyword should be unicode!")
            ngram_list = self.create_keyword_candidates(words_input,keyword)
            filtered_candidates = self.filter_keyword_candidates(ngram_list, keyword, threshold)
            if len(filtered_candidates) > 0:
                return filtered_candidates
        else:
            print "This version of word corrector only support string sentence type!"