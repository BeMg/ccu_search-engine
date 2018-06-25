from crawl import crawl
import re

c = crawl()
c.set_root_link('https://www.gog.com/')
c.set_filename('gogData.db')
c.set_link_checker(lambda s: '/game/' in s)
c.set_link_rule(
    lambda link: re.search(".*www\.gog\.com.*", link) is not None
)
c.set_content_rule(
    'name',
    lambda s: s.find('h1', {'class': 'header__title'}).text
)
c.set_content_rule(
    'price',
    lambda s: str(float(re.search('<span\ class="_price">(\ |\n)+([0-9]|\.)+(\ |\n)+</span>', s.prettify()).group()[21:-7].strip())*30)
)
c.set_content_rule(
    'discount',
    lambda s: str(float(s.find('span', {'class': 'buy-price__new'}).text)*30)
)
c.set_content_rule(
    'feature',
    lambda s: ", ".join([i.text.strip() for i in s.findAll('span', {'class': 'game-features__title'})])
)

c.run(1)

