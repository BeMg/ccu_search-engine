# 網際網路資料檢索 作業一

## 要求

建立一個搜尋引擎。並且滿足下列需求。

- 使用elaticsearch 作為 search engine 的 backend
- 建立一個可以使用的UI界面

## elasticsearch 

### 簡介

基於java，所以要先裝`java >= 8`。跑起來之後長的很像一台server，並且透過REST API進行資料的增減與搜尋的`query`。

傳送給elastic的資料格式以`JSON`為主。

elastic search 運作起來很像是database 下面簡單列出與database之間的對應關係。

- Node <-> DB server
- Index <-> database
- Type <-> Table
- document <-> row
- Field <-> column

### 使用

不經修改，預設`elasticsearch`會使用`localhost:9200`作為他的接口。所以可以藉由這個路徑進行操作。

> 官方推薦在`terminal`使用`curl`進行操作

- 查看目前有的`index`
```
GET /_cat/indices?v
```
```
health status index uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   hw1   l8nmMoxjSYypWv0LZ0IWpA   5   1     530278            0      1.2gb          1.2gb
```
- 加入一筆index
```
curl -XPOST 'locjson't:9200/test/news' -d "{ \"title\": \"yee\", \"body\": 1234 }" -H 'Content-Type: application/
```
```
{"_index":"test","_type":"news","_id":"LCmeGWIBVfCh6W9Xihub","_version":1,"result":"created","_shards":{"total":2,"successful":1,"failed":0},"_seq_no":0,"_primary_term":1}
```
> 如果不填入id的話，它會自動給一個隨機的id
- 移除整個index
```
DELETE /index_name
```
```
成功回傳true
```

- 執行多筆指令(bulk)
```
curl -XPOST 'localhost:9200/_bulk' -d {query}
```

> 一次只加入一筆資料速度挺慢的，初步推測是因為頻繁進行硬碟I/O的緣故，故一次新增多筆index。有效的解決這個問題

### elasticsearch-py

網路上有人將上訴的`REST API`，包裝成python的`module`。所以可以藉由此套件對elastic進行操作。

```python
from elasticsearch import Elasticsearch
es = Elasticsearch()

# 我只有使用到兩個指令 bulk, search

es.bulk(body=action)
es.search(index='hw1', body={
     "query": {

     "multi_match": {

     "query" : keyword,

     "fields" : \["title", "body"\]
    }
}

```

## JSON 操作

由於elasticsearch多使用JSON傳遞資料，在此紀錄一下一些常用的操作。

- 寫入JSON到檔案
```python
with open(filename, "w") as f:
    json.dump(data, f, ensure_ascii=False)
```
> ensure_ascii -> 設定為False，中文字才會顯示正常，不然會變成一串不是給人看的英文與數字
- 讀取JSON從檔案
```python
with open(filename, "r") as f:
    data = json.load(f)
```
- 從object生成JSON
```python
j = json.dumps(data)
```
- 從JSON字串生成object
```python
data = json.loads(j)
```

## 從原始資料到前端

- 從原始資料到JSON檔
```python
import os
import json
import glob

filename = glob.glob("ettoday*.rec")

data = \[\]
for fn in filename:
    cnt = 0
    with open(fn, "r") as f:
        while True:
            cnt += 1
            pos = f.tell()
            useless = f.readline()
            url = f.readline()
            url = url\[3:\]
            url = url.strip('\\n')
            title = f.readline()
            title = title\[3:\]
            title = title.strip('\\n')
            useless = f.readline()
            maintext = f.readline()
            maintext = maintext.strip()
            after_pos = f.tell()
            print("{}: {}".format(fn, cnt))
            \# print("{}:{}:{}".format(url, title, maintext))
            if pos == after_pos:
                break
            else:
                data.append({
                    'url':url, 
                    'title':title, 
                    'body':maintext})

with open('news.json', "w") as f:
    json.dump(data, f, ensure_ascii=False)
```

- 從json讀取進elastic
```python
from elasticsearch import Elasticsearch
import json

with open('./news_data/news.json') as f:
    Data = json.load(f)

es = Elasticsearch()
    
action = ''
cnt = 0
for data in Data:
    query = '{"index": {"\_index": "hw1", "\_type": "news"}}\\n' + json.dumps(data, ensure_ascii=False)
    action += query + '\\n'
    cnt += 1
    print(cnt)
    if cnt % 1000 == 0:
        es.bulk(body=action)
        action = ''

es.bulk(body=action)
```

- 對elastic執行query
```python
def query(keyword): 
    es = Elasticsearch() 
    tmp = es.search(index='hw1', body={ "query": { "multi_match": { "query" : keyword, "fields" : ["title", "body"] } } }) 
    tmp = tmp['hits']['hits'] 
    res = [] 
    for i in tmp: 
        res.append(i['_source']) 
    return res
```

## 網頁的部份

![](https://i.imgur.com/n4NnHvQ.png)

![](https://i.imgur.com/FyEvQ6g.png)

- 利用jquery進行網頁更新