import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import queue
import sqlite3
import time
import re

class fetcher:

    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_page_load_timeout(5)

    def __del__(self):
        self.driver.close()

    def getsoup(self, link, sleep_time=0):
        self.driver.get(link)
        time.sleep(sleep_time)
        s = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
        return s

    def getsoup_with_wait(self, link, wait_function):
        self.driver.get(link)
        wait_function(self.driver)
        s = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
        return s

    def restart(self):
        self.driver.close()
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_page_load_timeout(5)

class parser:

    def __init__(self):
        self.link_rule = None
        self.tag_rule = []
        self.root_link = ''

    def set_link_rule(self, link_rule):
        self.link_rule = link_rule

    def set_tag_rule(self, tag_rule):
        self.tag_rule = tag_rule

    def set_root_link(self, root_link):
        self.root_link = root_link

    # Some website href is not absolute link, but relative link
    def link_complete(self, link):
        if 'http' in link:
            rst = link
        elif self.root_link[10:] in link:
            rst = 'https:' + link
        else:
            rst = self.root_link + link
        return rst

    def anaysis_link(self, soup):
        link = self.link_rule(soup)
        link = [i['href'] for i in link]
        link = [self.link_complete(i) for i in link]
        return link

    def anaysis_content(self, soup):
        rst = [i(soup) for i in self.tag_rule]
        return tuple(rst)

class storage:

    def __init__(self):
        self.filename = ''
        self.tag_name = []
        self.table_name = ''

    def set_filename(self, filename):
        self.filename = filename

    def set_table_name(self, table_name):
        self.table_name = table_name

    def create_db(self, tag_name):
        self.tag_name = tag_name
        tag_name = [i+' text' for i in tag_name]
        tag_element = ", ".join(tag_name)
        conn = sqlite3.connect(self.filename)
        c = conn.cursor()
        c.execute('CREATE TABLE if not exists {} ( {} )'.format(self.table_name, tag_element))
        conn.commit()
        conn.close()

    def insert_db(self, data):
        conn = sqlite3.connect(self.filename)
        c = conn.cursor()
        element = ','.join(['?' for i in range(len(self.tag_name))])
        c.executemany('INSERT INTO {} VALUES ( {} )'.format(self.table_name, element), data)
        conn.commit()
        conn.close()

    def drop_db(self, table_name):
        conn = sqlite3.connect(self.filename)
        c = conn.cursor()
        c.execute('drop table if exists {}'.format(table_name))
        conn.commit()
        conn.close()

    def store_as_single_file(self, filename, content):
        pass

class crawl:

    def __init__(self):
        self.tag_name = []
        self.tag_rule = []
        self.root_link = ''
        self.filename = ''
        # f(soup) -> list of link
        self.link_rule = None
        # f(link) -> have content in this page
        self.link_checker = None
        self.wait_q = queue.Queue()
        self.used_link = set()
        self.core_nunber = 1

    def set_root_link(self, link):
        self.root_link = link

    # rule will be one function
    def set_link_rule(self, rule):
        self.link_rule = rule

    # content rule could be many, and it also define the tag of data
    # rule format look like as tag_name, tag_rule->Be a function which f(soup)->string
    def set_content_rule(self, tag_name, tag_rule):
        self.tag_name.append(tag_name)
        self.tag_rule.append(tag_rule)

    def set_filename(self, filename):
        self.filename = filename

    # check this link is for
    def set_link_checker(self, checker):
        self.link_checker = checker

    def run(self):
        s = storage()
        s.set_filename(self.filename)
        s.set_table_name('data')
        s.create_db(self.tag_name)

        f = fetcher()
        p = parser()
        p.set_root_link(self.root_link)
        p.set_link_rule(self.link_rule)
        p.set_tag_rule(self.tag_rule)

        self.wait_q.put(self.root_link)

        while not self.wait_q.empty():
            curr = self.wait_q.get()
            print(curr)
            try:
                soup = f.getsoup(curr)

                if self.link_checker(curr):
                    data = p.anaysis_content(soup)
                    s.insert_db(data)
                else:
                    pass

                link = p.anaysis_link(soup)
                for i in link:
                    if i in self.used_link:
                        pass
                    else:
                        self.wait_q.put(i)
                        self.used_link.add(i)
            except:
                print("FAIL")
                f.restart()
                self.wait_q.put(curr)

if __name__=='__main__':
    c = crawl()
    c.set_root_link('https://24h.pchome.com.tw/')
    c.set_filename('pchomeData.db')
    c.set_link_checker(lambda s: '/prod/' in s)
    c.set_link_rule(
        lambda soup: soup.findAll('a', attrs={"href": re.compile(".*region.*|.*store.*|.*sign.*|.*prod.*")})
    )
    c.set_content_rule('name',
                       lambda s: s.find('h5', {"id" : "NickContainer"}).text)
    c.set_content_rule('price',
                       lambda s: s.find('span', {"id" : "PriceTotal"}).text)
    c.run()