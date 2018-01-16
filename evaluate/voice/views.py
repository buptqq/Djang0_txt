# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from django.http import HttpResponse

from django.shortcuts import render

from collections import Counter
import json
import re
import jieba
import jieba.analyse
import sys
import os
import logging
import jieba.analyse
import math
import os
import chardet

abs = os.path.abspath('.')
if not os.path.exists(abs + "/upload"):
    os.mkdir(abs+"/upload")
# Create your views here.
similarity = 0
txt = ""
# jieba fenci
def fenci(content):
    seg_list = jieba.cut(content, cut_all=False)  # jingque model
    return ' '.join(seg_list)


# jieba get key words tfidf
def get_keywords(content):
    tags = jieba.analyse.extract_tags(content, topK=20)
    jieba.analyse.set_stop_words("stop_words.txt")
    return ' '.join(tags)


# mate chinese ,return list
def regex(src):
    chinese = re.compile(ur'[\u4e00-\u9fa5]+')
    pattern = re.compile(chinese)
    typ = chardet.detect(src)['encoding']
    #print json.dumps("".join(pattern.findall(src.decode(typ))),ensure_ascii=False)
    return "".join(pattern.findall(src.decode(typ)))


# cosine similarity
def cossim(list1, list2):
    return sum(map(lambda (a, b): a * b, zip(list1, list2))) / \
           math.sqrt(sum([x ** 2 for x in list1]) * sum([x ** 2 for x in list2]))

def voice_evaluate(src,tmp):
    try:
        # print sys.argv[0],sys.argv[1]
        one = src.read()
        two = tmp.read()
        txt = src.name
        global txt
        keywords_one = get_keywords(regex(one)).split(' ')
        keywords_two = get_keywords(regex(two)).split(' ')
        Count_one = dict(Counter(keywords_one))
        Count_two = dict(Counter(keywords_two))
        Count_A = {}
        Count_B = {}
        for key in keywords_one + keywords_two:
            Count_A[key] = 0
            Count_B[key] = 0
            if key in Count_one.keys(): Count_A[key] = Count_one[key]
            if key in Count_two.keys(): Count_B[key] = Count_two[key]
        list_A = []
        list_B = []
        for key, value in Count_A.items():
            list_A.append(value)
        for key, value in Count_B.items():
            list_B.append(value)
        #print json.dumps(Count_A,encoding='utf-8',ensure_ascii=False)
        #print json.dumps(Count_B,encoding='utf-8',ensure_ascii=False)
        similarity = '%.3f' % (cossim(list_A, list_B))
        global similarity
    finally:
        pass

def choose(request):
    if request.method == 'POST':
        meth = request.POST['meth']
        if meth == u'None': return HttpResponse(u"请选择计算算法")
        src = request.FILES.get("file_src", None)
        if not src:
            return HttpResponse(u"源文件未上传")
        tmp = request.FILES.get("file_tmp", None)
        if not tmp:
            return HttpResponse(u"测试文件未上传")
        if meth == u'cos':
            voice_evaluate(src,tmp)
    return render(request, 'voice/voice.html', {'similarity': similarity, 'name': txt})