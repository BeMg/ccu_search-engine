from crawl import crawl
import re

c = crawl()
c.set_root_link('https://store.steampowered.com/')
c.set_filename('steamData.db')
c.set_link_checker(lambda s: '/app/' in s)
c.set_link_rule(
    lambda link: re.search(".*store\.steampowered\.com.*", link) is not None and "?l=" not in link
)
c.set_content_rule(
    'name',
    lambda s: s.find('div', {'class': 'apphub_AppName'}).text
)
c.set_content_rule(
    'price',
    lambda s: re.search('[A-Z]+\$.([0-9]|\,)+', s.find('div', id='game_area_purchase').prettify()).group().strip('NT$ ')
)
c.set_content_rule(
    'discount',
    lambda s: s.find('div', id='game_area_purchase').find('div', {'class': 'discount_final_price'}).text.strip('NT$ ')
)
c.set_content_rule(
    'feature',
    lambda s: ", ".join([t.text.strip() for t in s.findAll('a', {'class': 'app_tag'})])
)
c.run(1)
