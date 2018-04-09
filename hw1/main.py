from elasticsearch import Elasticsearch
import json

def query(keyword, start = 0, rows = 10):
    es = Elasticsearch()

    tmp = es.search(index='hw2', body={
        "from" : start, "size": rows,
        "query": {
            "multi_match": {
                "query" : keyword,
                "fields" : ["title", "body"]
            }
        },
        "highlight" : {
            "fields" : {
                "body" : {}
            }
        }   
    })

    print(len(tmp['hits']['hits']))

    return tmp