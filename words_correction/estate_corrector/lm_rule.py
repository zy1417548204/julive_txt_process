# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

from utils.text_dealer import Converter,Preprocess

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


class CorrectWords():

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
        print u"keyword = " + keyword
        print len(ngram)
        # for item in sorted_candidates:
        #     print type(item[0]),type(item[1])
        #     print item[0],item[1]
        filtered_candidates = self.filter_candidate(sorted_candidates, threshold)
        for item in filtered_candidates:
            print item[0], item[1]

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

    # '''
    # '''
    # def find_keyword_error_candidates(self,wordsinput,keyword,threshold):
    #     ngrams = self.create_keyword_candidates(wordsinput,keyword)
    #     filtered_candidates = self.filter_keyword_candidates(ngrams,keyword,threshold)
    #     return filtered_candidates

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

if __name__ == '__main__':
    preprocessor = Preprocess()
    sentence = u'噢喂你好请问是陈女士吗是吧噢噢陈女士您好我是谈交往的咨询师杨阳嗯因为您在我们官网上是关注了精要谜底这个楼盘吗然后我这边' \
               u'嗯您这边是主要是关注它的一个两个房子吧对对对是这样的这个楼盘呢它是目前在浦东前滩板块然后目前它是有在售的在售的话是一个' \
               u'八十四平的是两方然后其他后勤比如说一百一十六到一百三十九之间都是三方'
    # print sentence
    # print ' '.join(LMRules().seq_collect_4gram(sentence))
    # sentence = preprocessor.remove_useless(sentence)
    # pysequence = preprocessor.create_pysequence(sentence)
    # word_list = preprocessor.segment_sentence(sentence)
    # print type(word_list)
    # segstr = ''
    # for word in word_list:
    #     segstr += word + ' '
    # print segstr
    result = LMRules().seq_collect_3gram(sentence=preprocessor.remove_useless(sentence))
    # print pysequence
    print " ".join(result)
    #
    # print LMRules().normal_leven('beauty','batyu')

    keyword_list = [u'侃家网']
    keyword = u'侃家网'