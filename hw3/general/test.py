from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=options)
driver.set_page_load_timeout(5)

driver.get('https://store.steampowered.com/')

elements = driver.find_elements_by_xpath("//a[@href]")

for element in elements:
    print(element.get_attribute('href'))