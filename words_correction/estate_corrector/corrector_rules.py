# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:


class LMRules():

    '''Collect 2-grams in given word list, the 2-gram words may exist in the word list, as well as be concatenated by
       two uni-gram words.
    :param word_list: A given list of one sentence which is segmented into words.
    :return: A list of 2-gram words within the given word list
    '''
    def list_collect_2gram(self,word_list):
        two_grams = []
        pre_unigram = u''
        for word in word_list:
            if len(word) == 2:
                two_grams.append(word)
                pre_unigram = u''
            elif len(word) == 1:
                if len(pre_unigram) == 0:
                    pre_unigram = word
                elif len(pre_unigram) == 1:
                    pre_unigram = pre_unigram + word
                    two_grams.append(pre_unigram)
                elif len(pre_unigram) == 2:
                    pre_unigram = pre_unigram[1] + word
                    two_grams.append(pre_unigram)
        return two_grams

    def seq_collect_2gram(self,sentence):
        two_grams = [sentence[index:index+2] for index in range(0,len(sentence)-1,1)]
        return two_grams

    '''Collect 3-grams in given word list, the 3-gram words may exist in the word list, as well as be consequently 
       concatenated by an uni-gram and 2-gram word or three uni-gram words.
    :param word_list:
    :return: 
    '''
    def list_collect_3gram(self,word_list):
        three_grams = []
        concat_word = u''
        flag = False
        for word in word_list:
            if len(word) == 3:
                three_grams.append(word)
                concat_word = u''
            elif len(word) == 2:
                if len(concat_word) == 1:
                    concat_word = concat_word + word
                    three_grams.append(concat_word)
                    concat_word = word
                else:
                    if flag:
                        concat_word = concat_word[1:]
                        if len(concat_word) == 1:
                            concat_word = concat_word + word
                            three_grams.append(concat_word)
                        flag = False
                    else:
                        concat_word = word
            elif len(word) == 1:
                if len(concat_word) == 2:
                    concat_word = concat_word + word
                    three_grams.append(concat_word)
                    if flag:
                        concat_word = concat_word[1:]
                    else:
                        concat_word = word
                elif len(concat_word) == 1:# If there were two single unigram words concatenated, mark it for
                    concat_word = concat_word + word # next judgment.
                    flag = True
                else:
                    concat_word = word

        return three_grams

    def seq_collect_3gram(self,sentence):
        three_grams = [sentence[index:index+3] for index in range(0,len(sentence)-2,1)]
        return three_grams

    '''Collect 4-grams in the given word list, the 4-gram words may exist in the word list, as well as be concatenated
       consequently by four uni-grams, or one uni-gram and a 3-gram, or two 2-grams, as well as two uni-grams and a 
       2-gram word.
    :param word_list:
    :return:
    '''
    def list_collect_4gram(self,word_list):
        four_grams = []
        concat_word = u''
        flag = False
        index = 0
        for word in word_list:
            if len(word) == 4:
                four_grams.append(word)
            elif len(word) == 3:
                if len(concat_word) == 1:
                    concat_word = concat_word + word
                    four_grams.append(concat_word)
                    concat_word = word
                    index = 3
                elif len(concat_word) == 2:
                    if index == 1:
                        concat_word = concat_word[1:] + word
                        four_grams.append(concat_word)
                        concat_word = word
                        index = 3
                    else:
                        concat_word = word
                elif len(concat_word) == 3:
                    if index < 2:
                        concat_word = word
                        index = 3
                    elif index == 2:
                        concat_word = concat_word[2:] + word
                        four_grams.append(concat_word)
                        concat_word = word
                        index = 3
                    elif index == 21:
                        concat_word = concat_word[2:] + word
                        four_grams.append(concat_word)
                        concat_word = concat_word[1:]
                        index = 3
                elif len(concat_word) == 0:
                    concat_word = word
            elif len(word) == 2:
                if len(concat_word) == 2:
                    concat_word = concat_word + word
                    four_grams.append(concat_word)
                    if index == 0:
                        concat_word = word
                    elif index == 1:
                        concat_word = concat_word[1:]
                    elif index == 11:
                        concat_word = concat_word[1:]
                        index = 1
                    elif index == 2:
                        concat_word = word
                        index = 2
                elif len(concat_word) == 1:
                    concat_word = concat_word + word
                    index = 1
                elif len(concat_word) == 3:
                    if index == 1:
                        concat_word = concat_word[1:]
                        concat_word = concat_word + word
                        four_grams.append(concat_word)
                        concat_word = word
                        index = 2
                    elif index == 11:
                        concat_word = concat_word[1:]
                        concat_word = concat_word + word
                        four_grams.append(concat_word)
                        concat_word = concat_word[1:]
                        index = 1
                    elif index == 21:
                        concat_word = concat_word[2:] + word
                        index = 1
                    elif index == 2:
                        concat_word = concat_word[2:] + word
                        index = 1
                    elif index == 3:
                        concat_word = word
                        index = 2
                    elif index == 0:
                        concat_word = word
            elif len(word) == 1:
                if len(concat_word) == 3:
                    concat_word = concat_word + word
                    four_grams.append(concat_word)
                    if index == 2:
                        concat_word = concat_word[2:]
                        index = 1
                    elif index == 1:
                        concat_word = concat_word[1:]
                        index = 2
                    elif index == 11:
                        concat_word = concat_word[1:]
                    elif index == 21:
                        concat_word = concat_word[2:]
                        index = 1
                    elif index == 3:
                        concat_word = word
                        index = 1
                    elif index == 0:
                        concat_word = word
                        index = 1
                elif len(concat_word) == 2:
                    if index == 0:
                        index = 2
                    elif index == 1:
                        index = 11
                    elif index == 2:
                        index = 21
                    concat_word = concat_word + word
                elif len(concat_word) == 1:
                    if index == 0:
                        index = 1
                    elif index == 1:
                        index = 11
                    concat_word = concat_word + word
                elif len(concat_word) == 0:
                    concat_word = word
                    index = 1
        return four_grams

    def seq_collect_4gram(self,sentence):
        four_grams = [sentence[index:index+4] for index in range(0,len(sentence)-3,1)]
        return four_grams