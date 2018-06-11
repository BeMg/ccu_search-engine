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
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_page_load_timeout(20)

    def __del__(self):
        self.driver.quit()

    def getsoup(self, link, sleep_time=0):
        self.driver.get(link)
        time.sleep(sleep_time)
        s = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
        return s

    def getsoup_with_newtab(self, link):
        self.driver.execute_script('window.open("{}", "_blank")'.format(link))

    def get_curr_windos_handles(self):
        return self.driver.window_handles

    def get_curr_link(self):
        return self.driver.current_url

    def get_all_href(self):
        elements = self.driver.find_elements_by_xpath('//a[@href]')
        result = []
        for element in elements:
            link = element.get_attribute('href')
            result.append(link)
        return result

    def close_alert(self):
        alert = self.driver.switch_to_alert()
        alert.accept()

    def get_curr_page_source(self):
        return self.driver.page_source

    def switch_to_windows(self, h):
        self.driver.switch_to_window(h)

    def getsoup_with_wait(self, link, wait_function):
        self.driver.get(link)
        wait_function(self.driver)
        s = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
        return s

    def close_brower(self):
        handles = self.driver.window_handles
        for handle in handles:
            self.driver.switch_to_window(handle)
            self.driver.close()

    def restart(self):
        self.driver.quit()
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
    # def link_complete(self, link):
    #     if 'http' in link[:30]:
    #         rst = link
    #     elif self.root_link[10:] in link:
    #         rst = 'https:' + link
    #     else:
    #         rst = self.root_link + link
    #     return rst
    #
    # def anaysis_link(self, soup):
    #     link = self.link_rule(soup)
    #     link = [i['href'] for i in link]
    #     link = [self.link_complete(i) for i in link]
    #     return link

    def link_filter(self, link):
        rst = []
        for i in link:
            if self.link_rule(i) == True:
                rst.append(i)
            else:
                pass
        return rst

    def anaysis_content(self, soup):
        rst = []
        for i in self.tag_rule:
            try:
                rst.append(i(soup))
            except:
                rst.append(None)
        if any(rst):
            print(rst)
            return tuple(rst)
        else:
            raise ValueError('content ERROR')

# Maybe default add link in db
class storage:

    def __init__(self):
        self.filename = ''
        self.tag_name = []
        self.table_name = ''

    def set_filename(self, filensame):
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
        self.start_links = []
        self.filename = ''
        # f(soup) -> list of link
        self.link_rule = None
        # f(link) -> have content in this page
        self.link_checker = None
        self.wait_q = queue.Queue()
        self.used_link = set()
        self.core_nunber = 1
        self.n_page = 0

    def set_root_link(self, link):
        self.root_link = link
        self.start_links.append(link)

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
        self.start_links.append(link)
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


    def run(self, n_core=MP.cpu_count()):
        s = storage()
        s.set_filename(self.filename)
        s.set_table_name('data')
        s.create_db(self.tag_name)

        p = parser()
        p.set_root_link(self.root_link)
        p.set_link_rule(self.link_rule)
        p.set_tag_rule(self.tag_rule)

        for start_link in self.start_links:
            self.wait_q.put(start_link)
            self.used_link.add(start_link)

        while not self.wait_q.empty():

            f = fetcher()
            curr_handle = f.get_curr_windos_handles()[0]
            curr_request = []
            cnt = 0
            link_tmp = []

            try:
                for i in range(n_core):
                    if self.wait_q.empty():
                        break
                    else:
                        curr = self.wait_q.get()
                        curr_request.append(curr)
                        print(curr)
                        f.getsoup_with_newtab(curr)

                handles = [i for i in f.get_curr_windos_handles() if i != curr_handle]
                data = []
                curr_request.reverse()

                for i, handle in enumerate(handles):
                    f.switch_to_windows(handle)
                    link_tmp += f.get_all_href()
                    try:
                        data.append((curr_request[i], f.get_curr_page_source()))
                    except:
                        self.wait_q.put(curr_request[i])
                        print("Load page time out")
                        n_core = max(n_core-2, 1)
                    cnt+=1
                n_core = min(n_core+1, 20)
            except Exception as e:
                print(str(e))
                print("Browser Crash")
                n_core = max(n_core//2, 1)
                for i in curr_request:
                    self.wait_q.put(i)
                f.close_brower()
                continue

            for d in data:
                link = d[0]
                soup = bs4.BeautifulSoup(d[1], 'lxml')
                try:
                    if self.link_checker(link):
                        content = p.anaysis_content(soup)
                        s.insert_db([content])
                    else:
                        pass

                    new_link = p.link_filter(link_tmp)
                    for nl in new_link:
                        if nl not in self.used_link:
                            self.used_link.add(nl)
                            self.wait_q.put(nl)
                        else:
                            pass
                    self.n_page += 1
                except Exception as e:
                    print(str(e))
                    print("FAIL {}".format(link))
                    self.wait_q.put(link)
            print("Already crawl {} page".format(self.n_page))

if __name__=='__main__':
    c = crawl()
    c.set_root_link('https://store.steampowered.com/')
    c.set_filename('steamData.db')
    c.set_link_checker(lambda s: '/app/' in s)
    c.set_link_rule(
        lambda link: re.search(".*store\.steampowered\.com.*", link) is not None
    )
    c.set_content_rule(
        'name',
        lambda s: s.find('h1').text[4:]
    )
    c.set_content_rule(
        'about',
        lambda s: s.find('div', id='game_area_description').text
    )
    c.run(10)s