import asyncio
from pyppeteer import launch
from random import shuffle
import bs4
import queue
import sqlite3
import re


async def get(link):
    try:
        browser = await launch({
            'headless': True
        })
        page = await browser.newPage()
        try:
            await page.goto(link, timeout=30000)
        except Exception as e:
            print(str(e))
            print('{} Fail'.format(link))
            return None
        html = await page.content()
        elements = await page.querySelectorAll('a[href]')
        href = []
        for element in elements:
            tmp_href = await page.evaluate('(element) => element.href', element)
            href.append(tmp_href)
        await browser.close()
        print("{} Done".format(link))
        return link, html, href
    except Exception as e:
        print(str(e))
        return None


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
            print(str(rst)[:100])
            return tuple(rst)
        else:
            raise ValueError('content ERROR')


# Maybe default add link in db
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
        tag_name = [i + ' text' for i in tag_name]
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

    def get_content(self, link, cnt, f, p, q):
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

    def run(self, n_core=4, counter_limit=1500):
        s = storage()
        s.set_filename(self.filename)
        s.set_table_name('data')
        s.create_db(['link'] + self.tag_name)

        p = parser()
        p.set_root_link(self.root_link)
        p.set_link_rule(self.link_rule)
        p.set_tag_rule(self.tag_rule)

        for start_link in self.start_links:
            self.wait_q.put(start_link)
            self.used_link.add(start_link)

        cnt = 0

        while not self.wait_q.empty():
            curr_link = []
            for i in range(n_core):
                if self.wait_q.empty():
                    break
                else:
                    curr_link.append(self.wait_q.get())
            task = [get(i) for i in curr_link]
            cnt += len(curr_link)
            try:
                rst = asyncio.get_event_loop().run_until_complete(asyncio.wait(task))
            except Exception as e:
                print(str(e))
                for i in curr_link:
                    self.wait_q.put(i)
                continue

            curr_rst = [i.result() for i in list(rst[0])]
            for curr in curr_rst:
                if curr is None:
                    continue
                l, h, new_l = curr
                new_l = p.link_filter(new_l)
                for i in new_l:
                    if i in self.used_link:
                        pass
                    else:
                        self.wait_q.put(i)
                        self.used_link.add(i)
                try:
                    if self.link_checker(l):
                        content = p.anaysis_content(bs4.BeautifulSoup(h, 'lxml'))
                        s.insert_db([tuple([l] + list(content))])
                except Exception as e:
                    print(str(e))
                    continue

            if cnt > counter_limit:
                cnt = 0
                self.used_link.clear()
                tmp = [self.wait_q.get() for x in range(self.wait_q.qsize())]
                shuffle(tmp)
                for x in range(counter_limit // 10):
                    self.used_link.add(tmp[x])
                    self.wait_q.put(tmp[x])



if __name__ == '__main__':
    c = crawl()
    c.set_root_link('https://store.steampowered.com/')
    c.set_start_link('https://store.steampowered.com/app/365450/Hacknet/')
    c.set_start_link('https://store.steampowered.com/app/415660/Tiger_Knight/')
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
        'price',
        lambda s: re.search('[A-Z]+\$.([0-9]|\,)+', s.find('div', id='game_area_purchase').prettify()).group()
    )
    c.set_content_rule(
        'discount',
        lambda s: s.find('div', id='game_area_purchase').find('div', {'class': 'discount_final_price'}).text
    )
    c.set_content_rule(
        'all_text',
        lambda s: s.get_text()
    )
    c.run(1)
