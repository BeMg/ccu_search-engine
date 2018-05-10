import bs4
import requests
from queue import Queue
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
drive = webdriver.Chrome(chrome_options=chrome_options)
drive.set_page_load_timeout(5)

def getsoup(link):
    try:
        alert = drive.switch_to_alert()
        alert.accept()
    except:
        pass
    drive.get(link)
    s = bs4.BeautifulSoup(drive.page_source, 'lxml')
    return s

def getusefullink(link):
    s = getsoup(link)
    ss = s.findAll('a', attrs={"href": re.compile(".*pchome.*(.*region.*|.*store.*|.*sign.*|.*prod.*)")})
    new_link = []
    for i in ss:
        new_link.append(i['href'])
    return new_link

def improvelink(link):
    if 'http' in link:
        rst = link
    elif '24h.pchome.com.tw' in link:
        rst = 'https:' + link
    else:
        rst = root_link + link
    return rst

def getcontent(link):
    pass


if __name__=='__main__':
    root_link = 'https://24h.pchome.com.tw/'

    wait_link_q = Queue()
    wait_link_q.put(root_link)

    used_link = set()
    used_link.add(root_link)

    f = open('prod.txt', 'w')
    cnt = 0

    while not wait_link_q.empty():
        curr = wait_link_q.get()
        print(curr)
        try:
            new_link = getusefullink(curr)
            new_link = [improvelink(i) for i in new_link]

            for i in new_link:
                if i in used_link:
                    pass
                else:
                    if '/prod/' in i:
                        f.write(i+'\n')
                        f.flush()
                    used_link.add(i)
                    wait_link_q.put(i)
        except:
            wait_link_q.put(curr)
            print("Fail")
            drive.close()
            drive = webdriver.Chrome(chrome_options=chrome_options)
            drive.set_page_load_timeout(5)

    f.close()


