from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

from numpy import random

def setOptions():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--mute-audio')
    options.add_argument('--window-size=1200,800')
    options.add_argument('--disable-notifications')
    options.add_argument('--enable-popup-blocking')
    return options

def seleniumWindow(url):
    driver = webdriver.Chrome(options=setOptions(), service=Service(ChromeDriverManager().install()))
    driver.get(url)
    return driver

def goToBottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        scroll_down = 0
        while scroll_down < 10:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            rr = random.rand()/10.
            time.sleep(0.3+rr)
            scroll_down += 1

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height