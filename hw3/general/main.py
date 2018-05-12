import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import queue
import sqlite3


class fetcher:

    def __init__(self, timeout=5):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.timeout = timeout
        self.driver.set_page_load_timeout(timeout)

    def __del__(self):
        self.driver.close()

    def getsoup(self, link):
        self.driver.get(link)
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
        self.driver.set_page_load_timeout(self.timeout)

class parser:

    def __init__(self, root_link='', _link_rule = None, _content_rule=None):
        self.link_rule = _link_rule
        self.content_filter = _content_filter
        self.root_link = root_link

    # Some website href is not absolute link, but relative link
    def link_complete(self, link):
        if 'http' in link:
            rst = link
        elif self.root_link[8:] in link:
            rst = 'https://' + link
        else:
            rst = self.root_link + link
        return rst

    def anaysis_link(self, soup):
        link = soup.findAll(attrs = {'href' : self.link_rule})
        link = [self.link_complete(i) for i in link]
        return link

    def anaysis_content(self, soup):
        pass


class storage:

    def __init__(self):
        self.filename = ''
        self.tag_name = []
        self.tag_rule = []

    def set_filename(self, filename):
        self.filename = filename

    def set_tag(self, tag):
        self.tag_name = [i[0] for i in tag]
        self.tag_rule = [i[1] for i in tag]

    def create_db(self, table_name):


    def store_as_single_file(self, filename, content):
        pass

class crawl:

    def __init__(self):
        self.content_rule = []
        self.root_link = ''
        self.filename = ''
        self.link_rule = None
        self.wait_q = queue.Queue()
        self.core_nunber = 1

    def set_root_link(self, link):
        self.root_link = link

    # rule will be one function
    def set_link_rule(self, rule):
        self.link_rule = rule

    # content rule could be many, and it also define the tag of data
    # rule format look like as tag_name, tag_rule->Be a function which f(soup)->string
    def set_content_rule(self, tag_name, tag_rule):
        self.content_rule += (tag_name, tag_rule)

    def set_filename(self, filename):
        self.filename = filename

    def run(self):
        s = storage()
        s.create_db()



if __name__=='__main__':

