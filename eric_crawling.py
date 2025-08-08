import re
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from tqdm import tqdm


def read_jsonl(file) -> list[dict]:
    with open(Path(file), mode='r') as f:
        data = [json.loads(line) for line in f]
    return data


def parse_text(text):
    text = text.strip()
    text = re.sub(r'\n\s*', '\t', text)
    return text


def fetch_univ_metadata():
    url = "https://www.nesin.com/html/?dir1=menu01&dir2=Ipsi_result_data&gubun=1"
    output_path = Path('내신닷컴/results/univ_metadata_2025.jsonl')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        prev_year_btn = page.locator('body > div.content > div.tab > div > div:nth-child(2) > div.year-select-btns > ul > li.changeHakyear[data-hakyear="2025"]')
        prev_year_btn.click()
        
        btn = page.locator('body > div.content > div.tab > div > div.tabs > div > div.detailed_search > div:nth-child(1) > div.search-submit.search_btn')
        btn.click()

        table = page.locator('body > div.content > div.tab > div > div.tabs > div > div.detailed_search > div.v-table-outline.margin-mobile > table')

        parser = LexborHTMLParser(table.evaluate("e => e.outerHTML"))
        
        columns = ['대학명', '전형명', '학과명', '수능최저', 'daehak', 'indexCode']
        values = []
        for tr in tqdm(parser.css('body > table > tbody > tr')[:-1]):
            info = re.split(r'\n+', tr.text(separator='\n', strip=True))
            info = [x for x in info if x]
            info.pop(3)
            meta_td = tr.css_first('td.u-major > div')
            daehak = meta_td.attributes['valid.daehak']
            indexcode = meta_td.attributes['valid.indexcode']
            values.append([*info, daehak, indexcode])
        
        df = pd.DataFrame(data=values, columns=columns, dtype='string')
        df.to_json(output_path, orient='records', lines=True, force_ascii=False)
        browser.close()


def req_http(url, row):
    query_params = {
        'daehak': '',
        'indexCode': '',
        'hakyear': 2026,
    }
    query_params['daehak'] = row.pop('daehak')
    query_params['indexCode'] = row.pop('indexCode')

    res = requests.get(url, params=query_params)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, parser='lxml')
    result = {}
    for i, table in enumerate(soup.find_all('table')):
        if i == 1: # 선택학과 기본정보
            tds = table.select('tbody > tr > td')
            result['전형유형'] = tds[0].get_text(strip=True)
            result['전년도모집인원'] = tds[1].get_text(strip=True)
            result['전년도경쟁률'] = tds[2].get_text(strip=True)
            result['추가합격'] = tds[5].get_text(strip=True)
        elif i == 3: # 수능최저
            tds = table.css('tbody > tr > td')
            result['수능최저'] = tds[1].get_text(strip=True)
    result = row | result
    return result


def fetch_detail():
    url = 'https://www.nesin.com/menu01/ipsiDetail.html'
    data = read_jsonl('내신닷컴/results/univ_metadata_2025.jsonl')

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for row in data:
            futures.append(executor.submit(req_http, url, row))

        with open('내신닷컴/results/입결상세_2025.jsonl', mode='w') as f:
            for future in tqdm(as_completed(futures), total=len(futures)):
                try:
                    result = future.result()
                except Exception as e:
                    continue
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                

def main():
    # fetch_univ_metadata()
    # fetch_detail()
    pass
    

if __name__ == '__main__':
    main()