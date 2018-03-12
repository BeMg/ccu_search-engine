from elasticsearch import Elasticsearch
import json

def query(keyword):
    es = Elasticsearch()
    tmp = es.search(index='hw1', body={
        "query": {
            "multi_match": {
                "query" : keyword,
                "fields" : ["title", "body"]
        }   
    }
    })
    tmp = tmp['hits']['hits']
    res = []
    for i in tmp:
       res.append(i['_source'])
    return res