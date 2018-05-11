from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import queue
import bs4

options = Options()
options.add_argument("--headless")
drive = webdriver.Chrome(chrome_options=options)
drive.set_page_load_timeout(5)

def getcontent(link):

    drive.get(link)

    WebDriverWait(drive, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="SloganContainer" and text() != ""]')))

    s = bs4.BeautifulSoup(drive.page_source, 'lxml')

    name = s.find('h5', {"id" : "NickContainer"}).text
    slogan = s.find('div', {"id" : "SloganContainer"}).text
    price = s.find('span', {"id" : "PriceTotal"}).text
    return (name, slogan, price)


if __name__=='__main__':
    q = queue.Queue()

    with open('prod.txt') as f:
        for line in f:
            line = line.replace('\n', '')
            q.put(line)

    f = open('data.rec', 'w')

    while not q.empty():
        curr = q.get()
        print(curr)
        try:
            rst = getcontent(curr)
            f.write('@rec\n')
            f.write('@link'+curr+'\n')
            f.write('@title'+rst[0]+'\n')
            f.write('@slogan'+rst[1]+'\n')
            f.write('@price'+rst[2]+'\n')
            f.flush()
        except:
            print('FAIL')
            q.put(curr)
            drive.close()
            drive = webdriver.Chrome(chrome_options=options)
            drive.set_page_load_timeout(5)

