# -*- coding: utf-8 -*-
# @FileName:
# @Author: qian qian
# @Create date:
# @Description:

from nltk.tokenize import StanfordSegmenter
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser

import jieba
import time

class NLPTools():

    def define_stanford_segmenter(self,java_class="edu.stanford.nlp.ie.crf.CRFClassifier",
                                  path_to_model="/Library/Tools/stanford/segmenter/data/pku.gz",
                                  path_to_dict="/Library/Tools/stanford/segmenter/data/dict-chris6.ser.gz",
                                  path_to_sihan_corpora_dict="/Library/Tools/stanford/segmenter/data/"):
        _stanford_segmenter = StanfordSegmenter(java_class=java_class,path_to_model=path_to_model,path_to_dict=
                                                path_to_dict,path_to_sihan_corpora_dict=path_to_sihan_corpora_dict)
        return _stanford_segmenter

    def define_stanford_ner_tagger(self,model_file_path=
                                        '/Library/Tools/stanford/ner/classifiers/chinese.misc.distsim.crf.ser.gz'):
        _stanford_ner_tagger = StanfordNERTagger(model_filename=model_file_path)
        return _stanford_ner_tagger

    def define_stanford_pos_tagger(self,model_file_path=
                                        '/Library/Tools/stanford/postagger/models/chinese-distsim.tagger'):
        _stanford_pos_tagger = StanfordPOSTagger(model_filename=model_file_path)
        return _stanford_pos_tagger

    def define_stanford_parser(self,path_to_models_jar=
                                    '/Library/Tools/stanford/parser/stanford-parser-models.jar',
                                    model_path=
                                    u"edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz"):
        _stanford_parser = StanfordParser(path_to_models_jar=path_to_models_jar,model_path=model_path)
        return _stanford_parser

    def define_stanford_dependency_parser(self,path_to_models_jar=
                                               '/Library/Tools/stanford/stanford-corenlp-full/' \
                                               'stanford-chinese-corenlp-2017-06-09-models.jar',
                                               model_path=
                                               u'edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz'):
        _stanford_dependency_parser = StanfordDependencyParser(path_to_models_jar=path_to_models_jar,
                                                               model_path=model_path)
        return _stanford_dependency_parser

    def parse_dependency_treenodes(self,nodes):
        for node in nodes[0].triples():
            first_word = node[0][0]
            relation = node[1]
            second_word = node[2][0]
        return (first_word,second_word,relation)


if __name__ == "__main__":
    sentence1 = "晚上做一些关注噢只是在网上看过然后呢就说对不了解呢是我这边是先了解一下然后可能这周或者下周可能会在领导层面一块过来看一看也不是我自己要那个就说是领导他们那边讲过来看但看呢主要是看那个嗯公寓或者是left资本形式的大概呢是在四十左右到五十左右这种平方的"
    sentence2 = "生活品质就需要环境好一些那您这边就是区域有没有要求呢因为我看到您关注的是河西区还是说比如说你是只关注核心还是说其他的区域也能接受"

    stanford_segmenter_start = time.time()
    segmenter = NLPTools().define_stanford_segmenter()
    res1 = segmenter.segment(unicode(sentence1,'utf-8'))
    res2 = segmenter.segment(unicode(sentence2,'utf-8'))
    print res1.encode("utf-8")
    print res2.encode("utf-8")
    stanford_segmenter_end = time.time()
    print "stanford segmenter uses " + str((stanford_segmenter_end - stanford_segmenter_start)) + ' seconds.'

    jieba_start = time.time()
    seg_list1 = jieba.cut(sentence1)
    seg_list2 = jieba.cut(sentence2)
    print " ".join(seg_list1)
    print " ".join(seg_list2)
    jieba_end = time.time()
    print "jieba segmenter uses " + str((jieba_end - jieba_start)) + ' seconds.'

    seg_sentence2 = "晚上 做 一些 关注 噢 只是 在 网上 看过 然后 呢 就 说 对 不 了解 呢 是 我 这边 是 先 了解 一下 然后 可能 这 周 或者 下周 可能 会 在 领导 层面 一块 过来 看一看 也 不是 我 自己 要 那个 就 说 是 领导 他们 那边 讲过来 看 但 看 呢 主要 是 看 那个 嗯 公寓 或者 是 left 资本 形式 的 大概 呢 是 在 四十左右 到 五十 左右 这种 平方 的"
    seg_sentence1 = "生活 品质 就 需要 环境 好 一些 那 您 这边 就 是 区域 有 没 有 要求 呢 因为 我 看到 您 关注 的 是 河西区 还是 说 比如说 你 是 只 关注 核心 还是 说 其他 的 区域 也 能 接受"
    stanford_dparser_start = time.time()
    chi_dependency_parser = StanfordDependencyParser(
        path_to_models_jar='/Library/Tools/stanford/stanford-corenlp-full/stanford-chinese-corenlp-2017-06-09-models.jar',
        model_path=u'edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz')
    res_node_list1 = list(chi_dependency_parser.parse(unicode(seg_sentence1,'utf-8').split()))
    for row in res_node_list1[0].triples():
        type(row)
        first_word = row[0][0].encode('utf-8')
        relation = row[1].encode('utf-8')
        second_word = row[2][0].encode('utf-8')
        print first_word,relation,second_word
    res_node_list2 = list(chi_dependency_parser.parse(unicode(seg_sentence2,'utf-8').split()))
    for row in res_node_list2[0].triples():
        type(row)
        first_word = row[0][0].encode('utf-8')
        relation = row[1].encode('utf-8')
        second_word = row[2][0].encode('utf-8')
        print first_word,relation,second_word
    stanford_dparser_end = time.time()
    print "stanford dependency parser uses " + str((stanford_dparser_end - stanford_dparser_start)) + ' seconds'

