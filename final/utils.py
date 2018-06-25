from elasticsearch import Elasticsearch
import json
import sqlite3

def sqlite2json(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute('SELECT * FROM data')
    Data = c.fetchall()
    conn.close()
    rst = []
    for data in Data:
        link = data[0]
        name = data[1]
        price = data[2]
        tags = data[3]
        if name == None:
            pass
        else:
            rst.append(dict({
                'link': link,
                'name': name,
                'price': price,
                'tags': tags
            }))
    return rst

def load2elastic(filename):
    es = Elasticsearch()

    action = ''
    cnt = 0
    for data in sqlite2json(filename):
        query = '{"index": {"_index": "final", "_type": "game"}}\n' + json.dumps(data, ensure_ascii=False)
        action += query + '\n'
        cnt += 1
        print(cnt)
        if cnt % 1000 == 0:
            es.bulk(body=action)
            action = ''

    es.bulk(body=action)


def query(keyword, start = 0, rows = 10):
    es = Elasticsearch()

    tmp = es.search(index='final', body={
        "from" : start, "size": rows,
        "query": {
            "multi_match": {
                "query" : keyword,
                "fields" : ["tags", "name"]
            }
        },

    })
    return tmp

if __name__=='__main__':
    load2elastic('merge.db')