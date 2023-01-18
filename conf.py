import donotimport
import psycopg2
import os
from selenium import webdriver
from fake_useragent import UserAgent

useragent = UserAgent(browsers=['firefox', 'chrome'])

install_dir = "/snap/firefox/current/usr/lib/firefox"
binary_loc = os.path.join(install_dir, "firefox")
opts = webdriver.FirefoxOptions()
opts.binary_location = binary_loc
opts.add_argument(f'user-agent={useragent.random}')
opts.set_preference("dom.webdriver.enabled", False)
opts.headless = True
conn = psycopg2.connect(donotimport.connect_db)
cur = conn.cursor()
