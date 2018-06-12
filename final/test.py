import asyncio
from pyppeteer import launch

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

link = [
    'https://store.steampowered.com/app/365450/Hacknet/'
]

task = [get(i) for i in link]

rst = asyncio.get_event_loop().run_until_complete(asyncio.wait(task))

curr = [i.result() for i in list(rst[0])]

print(curr)

s = bs4.BeautifulSoup(curr[0][1], 'lxml')

print(re.search('discount_final_price', s.prettify()))

print(s.find('div', {'class': 'discount_final_price'}).text)
