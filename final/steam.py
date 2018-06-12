from crawl import crawl
import re

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
