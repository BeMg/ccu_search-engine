import jieba
import requests
import json

jieba.load_userdict('term.txt')

def text_seg(origin_seg):
    seg_list = jieba.cut(origin_seg, cut_all=False)
    seg = ['"{}"'.format(i) for i in seg_list]
    return ", ".join(seg)

def query(keyword, start=0, rows=10):
    seg = text_seg(keyword)
    r = requests.get('http://localhost:8983/solr/news/select?hl.fl=body&hl=on&q='+seg+"&rows={}&start={}".format(rows, start))
    res = json.loads(r.text)
    return res