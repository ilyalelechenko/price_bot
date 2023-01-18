import time
from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By


def parse_wb(url, browser):
    try:
        browser.get(url)
        time.sleep(5)
        name = browser.find_element(By.CLASS_NAME, 'product-page__header')
        price = browser.find_elements(By.CLASS_NAME, "product-page__price-block")
        all_text = [name.text.replace('\n', ' '), price[1].text.replace("\n", ' / ')]
        return all_text
    except:
        print('error on parseWB')
        browser.close()
        return None


def parse_wb2(txt, browser, match='60'):
    wonna = txt.replace(' ', '+')
    url = f"https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort=priceup&search={wonna}"
    browser.get(url)
    time.sleep(1)
    browser.execute_script("window.scrollTo(0,200);")
    browser.execute_script("window.scrollTo(0,400);")
    try:
        time.sleep(2)
        all_find2 = browser.find_elements(By.CLASS_NAME, 'product-card__main')
        for i in all_find2:
            ref = i.get_attribute('href')
            i = i.text.split('\n')
            name = i[-3].replace('/ ', '')
            price = i[-4]
            if fuzz.partial_ratio(txt.lower(), name.lower()) >= int(match) and 'Уценка' not in name:
                break
        else:
            return None
        return [ref, price]
    except all as er: #Да не правильно, но что поделать, ловлю все ошибки
        print("Error on parseWB2")
        print(er)
        return None
