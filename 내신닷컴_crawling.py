import re
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from selectolax.parser import HTMLParser 
import requests
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tqdm import tqdm


url = "https://www.nesin.com/html/?dir1=menu01&dir2=Ipsi_result_data&gubun=1"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_timeout(3)
    prev_year_btn = page.locator('body > div.content > div.tab > div > div:nth-child(2) > div.year-select-btns > ul > li.changeHakyear[data-hakyear="2025"]')
    prev_year_btn.click()

    search_btn=page.locator('body > div.content > div.tab > div > div.tabs > div > div.detailed_search > div:nth-child(1) > div.search-submit.search_btn')
    search_btn.click()

    table_format=page.locator('body > div.content > div.tab > div > div.tabs > div > div.detailed_search > div.v-table-outline.margin-mobile > table')

    #HTML 분석가 : 전달받은 HTML 코드 문자열을 분석

    parser=HTMLParser(table_format.evaluate("e => e.outerHTML"))
    #table의 HTML을 가져오는 것
    #parser.css는 무엇??
    
    browser.close()



