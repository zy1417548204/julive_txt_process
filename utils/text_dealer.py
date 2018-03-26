# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

import pypinyin
import jieba
import os
from extract_label.extract_rules import ConstValue

class Checker():

    '''Judge whether the input word has digit or not
    '''

    def has_digit(self,word):
        return any(char.isdigit() for char in word)

class Converter():

    '''Generate pinyin for input chinese word
    '''
    def get_word_pinyin(self,word):
        py = pypinyin.slug(word, separator=' ')
        return py

class Preprocess():

    global stop_words
    stop_words = []

    def __init__(self):
        dic_folder_path = ConstValue.project_root + '/project_dic'
        stop_word_file = open(dic_folder_path + '/stop_word.dic', 'rb')
        for word in stop_word_file.readlines():
            stop_words.append(unicode(word, encoding='utf-8').strip())

    def remove_useless(self,sentence):
        if not isinstance(sentence,unicode):
            raise Exception('The input sentence should be unicode format! However the actual type is '
                            + str(type(sentence)))
            return
        for word in stop_words:
            sentence = sentence.replace(word,'')
        return sentence

    def segment_sentence(self,sentence):
        seg_list = jieba.cut(sentence)
        return " ".join(seg_list).split()

    def create_pypair(self,wordlist):
        pypair = {}
        for word in wordlist:
            py = Converter().get_word_pinyin(word)
            pypair.update({word:py})
        return pypair

    def create_pysequence(self,sentence):
        word_list = self.segment_sentence(sentence)
        sequence = u''
        for word in word_list:
            py = Converter().get_word_pinyin(word)
            sequence += py + ' '
        return sequence