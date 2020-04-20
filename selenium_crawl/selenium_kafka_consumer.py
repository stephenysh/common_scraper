import argparse
import json
import os
import time
import urllib
from pathlib import Path

import jsonlines
import selenium.webdriver as webdriver
import selenium.webdriver.support.expected_conditions as EC
from kafka import KafkaConsumer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from util import mapLineCount


class TransResult(dict):
    def __init__(self, ar_sen, en_sen, url, err=None):
        dict.__init__(self, ar_sen=ar_sen, en_sen=en_sen, url=url, err=err)

def get_translate(driver: webdriver, input: str) -> tuple:
    try:
        # if random.random() < 1:
        #     raise RuntimeError('Test ERROR')

        assert input is not None
        assert len(input) != 0

        src_elem = WebDriverWait(driver, 10).until(
            lambda d: d.find_element_by_css_selector("textarea[id='source']"))

        src_elem.clear()
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element_by_css_selector("div[class='tlid-results-container results-container empty']"))

        src_elem.send_keys(input)

        time.sleep(3)

        out_elem = WebDriverWait(driver, 10).until(
            lambda d: d.find_element_by_css_selector("span[class='tlid-translation translation'] span"))

        return out_elem.text, urllib.parse.unquote(driver.current_url)

    except Exception as e:
        return None, e


parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--out_dir', default='/hdd/kafka_selenium_google_translate')

args = parser.parse_args()
consumer_id = int(args.id)

consumer = KafkaConsumer('google', group_id='google_group', bootstrap_servers='10.111.137.118:9092')

metrics = consumer.metrics()
print(metrics)


idx_output_saved = 0
idx_error_saved = 0

output_lines = []
error_lines = []

file_save_period = 100  # lines save once

t = time.time()


save_path = Path(args.out_dir)
os.makedirs(str(save_path), exist_ok=True)

out_filename = str(save_path / f'consumer_{consumer_id:02d}_output.jsonl')
err_filename = str(save_path / f'consumer_{consumer_id:02d}_error.jsonl')

fw_out = jsonlines.open(out_filename, 'a')
fw_err = jsonlines.open(err_filename, 'a')

line_fw = mapLineCount(out_filename)
line_err = mapLineCount(err_filename)

with webdriver.Chrome() as driver:
    driver.get("https://translate.google.com/")
    assert "Google Translate" in driver.title

    button_elem = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='sl-more tlid-open-source-language-list']")))

    button_elem.click()

    ar_bnt = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='language_list_item language_list_item_language_name'][text()='Arabic']")
        )
    )
    ar_bnt.click()

    try:
        for idx, msg in enumerate(consumer, start=line_fw + line_err + 1):
            if len(output_lines) == file_save_period:
                fw_out.write_all(output_lines)
                print(f'saved to output file {out_filename}')
                idx_output_saved += 1
                output_lines = []

            if len(error_lines) == file_save_period:
                fw_err.write_all(error_lines)
                print(f'saved to error file {err_filename}')
                idx_error_saved += 1
                error_lines = []

            json_str = msg.value.decode('utf-8').strip()

            json_obj = json.loads(json_str)

            input_idx = json_obj.get('idx')
            ar_sen = json_obj.get('text')

            if ar_sen == '':
                continue

            en_sen, url = get_translate(driver, ar_sen)

            if en_sen is not None:
                print(f'[{idx}] SUCCESS msg at input_idx={input_idx}, partition={msg.partition}, offset={msg.offset}')
                output_lines.append(TransResult(ar_sen, en_sen, url))
            else:
                print(
                    f'[{idx}] ERROR   msg at input_idx={input_idx}, partition={msg.partition}, offset={msg.offset}, e={url.__class__.__name__}')
                error_lines.append(TransResult(ar_sen, None, None, url.__class__.__name__))

    except KeyboardInterrupt:

        print('Terminating...')

        if len(output_lines) > 0:
            print(f'Writing [{len(output_lines)}] lines into out file...')

            fw_out.write_all(output_lines)

        if len(error_lines) > 0:
            print(f'Writing [{len(error_lines)}] lines into err file...')
            fw_err.write_all(error_lines)

    fw_out.close()
    fw_err.close()
