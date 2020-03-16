import selenium
import os
import sys
import random
from pathlib import Path
import time
import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)

args = parser.parse_args()

def get_translate(driver: webdriver, input: str) -> tuple:

    assert input is not None
    assert len(input) != 0
    src_elem = driver.find_element_by_css_selector("textarea[id='source']")
    src_elem.clear()
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector("div[class='tlid-results-container results-container empty']"))

    src_elem.send_keys(input)
    out_elem = WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector("span[class='tlid-translation translation'] span"))

    return out_elem.text


input_file = Path(args.input).resolve()
input_folder_path = input_file.parent
input_name = input_file.name
num_lines = sum(1 for line in open(str(input_file), 'r'))

fr = open(str(input_file), 'r', encoding='utf-8')
fw = open(str(input_folder_path / '{input_name}_selenium_outpout.txt'), 'w', encoding='utf-8')
fe = open(str(input_folder_path / '{input_name}_selenium_error.txt'), 'w', encoding='utf-8')

idx = 0

t = time.time()

with webdriver.Chrome() as driver:

    driver.get("https://translate.google.com/")
    assert "Google Translate" in driver.title

    while True:


        ar_sen  = 'ﻡﺍﺫﺍ ﻝﻭ ﻚﻨﺗ ﺎﻟﺮﺌﻴﺳ؟ ... ﺍﻸﻣﺮﻴﻜﻳﻮﻧ ﻲﺠﻴﺑﻮﻧ'

        en_sen = get_translate(driver, ar_sen)

        time.sleep(100000)

        print(en_sen)

        # line = fr.readline()
        #
        # if line == '':
        #     break
        #
        # ar_sen = line.strip()
        #
        # try:
        #     en_sen = get_translate(driver, ar_sen)
        #
        #     fw.write(str(idx) + '|' + ar_sen + '|' + en_sen + '\n')
        #
        # except Exception as e:
        #
        #     print(f'ERROR in line [{idx}]: {e}')
        #
        #     fe.write(str(idx) + ar_sen + '\n')
        #
        # idx += 1
        #
        # if idx % 10 == 0:
        #     used_time = time.time()-t
        #     print(f'line current/total [{idx}]/[{num_lines}], time used/expected [{used_time: .2f}]/[{(num_lines-idx)/idx*used_time: .2f}]')

    driver.close()


