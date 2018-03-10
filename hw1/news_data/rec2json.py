import os
import json
import glob

filename = glob.glob("ettoday*.rec")

data = []
for fn in filename:
    cnt = 0
    with open(fn, "r") as f:
        while True:
            cnt += 1
            pos = f.tell()
            useless = f.readline()
            url = f.readline()
            url = url[3:]
            url = url.strip('\n')
            title = f.readline()
            title = title[3:]
            title = title.strip('\n')
            useless = f.readline()
            maintext = f.readline()
            maintext = maintext.strip()
            after_pos = f.tell()
            print("{}: {}".format(fn, cnt))
            # print("{}:{}:{}".format(url, title, maintext))
            if pos == after_pos:
                break
            else:
                data.append({
                    'url':url, 
                    'title':title, 
                    'body':maintext})


with open('news.json', "w") as f:
    json.dump(data, f, ensure_ascii=False)