#!/usr/bin/python
from sys import argv
import signal 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException, StaleElementReferenceException

from urllib.parse import urlsplit


# options and data
DATA = {}  # crawl data saved as { 'base site 1' : ('url1', 'url2', 'url3', ...), 'base site 2' : (...), ... }
RECUSION_DEPTH = 3  # depth of recusion allowed
IGNORE_CASE = ["#", ".png", ".jpg", ".jpeg", ".pdf"]  # ignore cases in url 


# webdriver init
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--disable-notifications")
OPTIONS.add_argument("--disable-popup-blocking")
OPTIONS.add_argument("--headless")
OPTIONS.add_argument("--disable-gpu")
DRIVER = webdriver.Chrome(options=OPTIONS)
DRIVER.implicitly_wait(10)


def quitHandler(sig, fname):
    print(DATA)
    quit()

def parseUrl(url):
    parsed = urlsplit(url)    
    return parsed.netloc, parsed.path, url


def verifyUrl(url):
    checkCase = lambda i: False if i in url else True
    if url is None:
        return False

    elif False in map(checkCase, IGNORE_CASE):
        return False


    return True

def addRecord(url, dest):
    baseUrl, pathUrl, url = parseUrl(url)
    
    try:
        if url not in dest[baseUrl]:
            dest[baseUrl].add(url)
            
        else:
            return False
        
    except KeyError:
        dest[baseUrl] = {url}
        
    return True


def scrapPage(url, depth):
    global DRIVER, DATA, RECUSION_DEPTH
    targets = {}

    if depth > RECUSION_DEPTH:
        return

    print(f"{depth} scrapping {url}")
    DRIVER.get(url)
    links = DRIVER.find_elements(By.TAG_NAME, "a")           
    for l in links:
        try:
            l = l.get_attribute("href")
            if verifyUrl(l):
                addRecord(l, targets)

        except StaleElementReferenceException:
            pass

    try:
        for baseTarget in targets.values():
            for t in baseTarget:
                if addRecord(t, DATA):
                    scrapPage(t, depth+1)
                    
    except InvalidArgumentException:
        pass


def main():
    signal.signal(signal.SIGINT, quitHandler)

    print("scrapper started")
    try:
        if verifyUrl(argv[1]):
            scrapPage(argv[1], 0)
        else:
            print("invalid url")

    except IndexError:
        print("no url entered")

    print(DATA)
    DRIVER.quit()


if __name__=="__main__":
    main()    




