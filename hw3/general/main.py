import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import queue
import sqlite3
import time
import re
import multiprocessing as MP


class fetcher:

    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_page_load_timeout(5)

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
        self.drop_db(self.table_name)
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

class crawl:

    def __init__(self):
        self.tag_name = []
        self.tag_rule = []
        self.root_link = ''
        self.start_link = ''
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
        self.start_link = link

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

    def set_start_link(self, link):
        self.start_link = 'http://www.books.com.tw/products/0010637918'

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

        self.wait_q.put(self.start_link)
        self.used_link.add(self.start_link)

        while not self.wait_q.empty():
            curr = self.wait_q.get()
            print(curr)
            try:
                soup = f.getsoup(curr)

                if self.link_checker(curr):
                    data = p.anaysis_content(soup)
                    s.insert_db([data])
                else:
                    pass

                link = p.anaysis_link(soup)
                for i in link:
                    if i in self.used_link:
                        pass
                    else:
                        self.wait_q.put(i)
                        self.used_link.add(i)
            except :
                print("FAIL")
                f.restart()
                self.wait_q.put(curr)

    def get_content(self, link, cnt , f, p, q):
        try:
            rst = p.anaysis_content(f.getsoup(link))
            q.put((link, cnt, rst))
        except:
            q.put((link, cnt, None))
        print("{} DONE".format(cnt))


    def get_link(self, link, cnt, f, p, q):
        try:
            rst = p.anaysis_link(f.getsoup(link))
            q.put((link, cnt, rst))
        except:
            q.put((link, cnt, None))
        print("{} DONE".format(cnt))

    def run_with_parallel(self, n_core=MP.cpu_count()):
        s = storage()
        s.set_filename(self.filename)
        s.set_table_name('data')
        s.create_db(self.tag_name)

        p = parser()

        p = []
        f = []
        for i in range(n_core):
            tmp_p = parser()
            tmp_p.set_root_link(self.root_link)
            tmp_p.set_link_rule(self.link_rule)
            tmp_p.set_tag_rule(self.tag_rule)
            p.append(tmp_p)
            f.append(fetcher())

        self.wait_q.put(self.start_link)
        self.used_link.add(self.start_link)

        while not self.wait_q.empty():
            cnt = 0
            P = []
            content_q = MP.Queue()
            link_q = MP.Queue()
            for i in range(n_core):
                if self.wait_q.empty():
                    break
                else:
                    curr = self.wait_q.get()
                    print(curr)
                    if self.link_checker(curr):
                        P.append(MP.Process(target=self.get_content,
                                            args=(curr, cnt, f[cnt], p[cnt], content_q)))
                        cnt += 1
                    else:
                        P.append(MP.Process(target=self.get_link,
                                            args=(curr, cnt, f[cnt], p[cnt], link_q)))
                        cnt += 1

            for tmp_p in P:
                tmp_p.start()
                print(tmp_p.pid)

            for tmp_p in P:
                tmp_p.join(8)

            for tmp_p in P:
                if tmp_p.is_alive():
                    tmp_p.terminate()

            data = []
            while not content_q.empty():
                link, ct, rst = content_q.get()
                if rst == None:
                    print("FAIL IN {}".format(link))
                    self.wait_q.put(link)
                    f[ct].restart()
                else:
                    data.append(rst)

            while not link_q.empty():
                link, ct, rst = link_q.get()
                if rst == None:
                    print("FAIL IN {}".format(link))
                    self.wait_q.put(link)
                    f[ct].restart()
                else:
                    for i in rst:
                        if i not in self.used_link:
                            self.wait_q.put(i)
                            self.used_link.add(i)
                        else:
                            pass


if __name__=='__main__':

    c = crawl()
    c.set_root_link('http://www.books.com.tw')
    c.set_filename('booksData.db')
    c.set_link_checker(lambda s: '/products/' in s)
    c.set_link_rule(
        lambda soup: soup.findAll('a', attrs={"href": re.compile(".*books.com.tw.*")})
    )
    c.set_content_rule(
        'name',
        lambda s: s.find('h1', itemprop='name').text
    )
    c.set_content_rule(
        'author',
        lambda s: s.find('li', itemprop='author').find('a', attrs={'href': re.compile('.*search.*')}).text
    )
    c.set_content_rule(
        'publisher',
        lambda s: s.find('span', itemprop='brand').text
    )
    c.set_content_rule(
        'price',
        lambda s: s.find('b', itemprop='price').text
    )
    c.run_with_parallel()


    # c = crawl()
    # c.set_root_link('http://www.books.com.tw')
    # c.set_filename('booksData.db')
    #
    # def f1(s):
    #     return '/products/' in s
    #
    # def f2(s):
    #     return s.findAll('a', attrs={"href": re.compile(".*books.com.tw.*")})
    #
    # def f3(s):
    #     return s.find('h1', itemprop='name').text
    #
    # def f4(s):
    #     return s.find('li', itemprop='author').find('a', attrs={'href': re.compile('.*search.*')}).text
    #
    # def f5(s):
    #     return s.find('span', itemprop='brand').text
    #
    # def f6(s):
    #     return s.find('b', itemprop='price').text
    #
    # c.set_link_checker(f1)
    # c.set_link_rule(
    #     f2
    # )
    #
    # c.set_content_rule(
    #     'name',
    #     f3
    # )
    # c.set_content_rule(
    #     'author',
    #     f4
    # )
    # c.set_content_rule(
    #     'publisher',
    #     f5
    # )
    # c.set_content_rule(
    #     'price',
    #     f6
    # )
    # c.run_with_parallel()
