from elasticsearch import Elasticsearch
import json

with open('./news_data/news.json') as f:
    Data = json.load(f)


es = Elasticsearch()
    
action = ''
cnt = 0
for data in Data:
    query = '{"index": {"_index": "hw1", "_type": "news"}}\n' + json.dumps(data, ensure_ascii=False)
    action += query + '\n'
    cnt += 1
    print(cnt)
    if cnt % 1000 == 0:
        es.bulk(body=action)
        action = ''

es.bulk(body=action)