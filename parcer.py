import time
from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By
from conf import webdriver, opts


def parcer_ozon(txt, browser, match='75'):
    wonna = txt.replace(' ', '+')
    url = f"https://www.ozon.ru/search/?from_global=true&sorting=ozon_card_price&text={wonna}"
    browser.get(url)
    time.sleep(1)
    browser.execute_script("window.scrollTo(0,200);")
    browser.execute_script("window.scrollTo(0,400);")
    try:
        time.sleep(2)
        all_find2 = browser.find_elements(By.CLASS_NAME, "tile-hover-target")
        for i in all_find2:
            if fuzz.partial_ratio(txt, i.text.lower()) >= int(match) and 'Товар уцененный' not in i.text:
                ref = i.get_attribute('href')
                break
        else:
            return None
        price1 = price(ref).split('/')
        return price1[0], ref
    except all as error:
        print(error)
        print('Error on parcer_ozon')
        return None


def parcer_ozon2(url, browser):
    browser.get(url)
    time.sleep(1)
    name = browser.find_element(By.CSS_SELECTOR, 'div[data-widget="webProductHeading"]')
    prices = browser.find_element(By.CSS_SELECTOR, 'div[slot="content"]')
    prices = prices.text.replace('\u2009', '').replace('\n', ' / ')
    return [prices, name.text]


def price(url):
    browser2 = webdriver.Firefox(options=opts)
    browser2.get(url)
    try:
        time.sleep(1.5)
        prices = browser2.find_element(By.CSS_SELECTOR, 'div[slot="content"]')
        prices = prices.text.replace('\u2009', '').replace('\n', ' / ')
        browser2.quit()
        return prices
    except all as error:
        print(error)
        print('Error on price')
        return None

