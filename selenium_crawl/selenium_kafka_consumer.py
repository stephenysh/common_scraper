import os
import time
import urllib
import jsonlines
import argparse
from pathlib import Path
from kafka import KafkaConsumer
import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By

class TransResult(dict):
    def __init__(self, ar_sen, en_sen, url, err=None):
        dict.__init__(self, ar_sen=ar_sen, en_sen=en_sen, url=url, err=err)

def get_translate(driver: webdriver, input: str) -> tuple:

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

parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--out_dir', default='/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/kafka_selenium_google_translate')

args = parser.parse_args()
consumer_id = int(args.id)

consumer = KafkaConsumer('google', group_id='google_group', bootstrap_servers='10.111.137.118:9092')

metrics = consumer.metrics()
print(metrics)


idx_output_saved = 0
idx_error_saved = 0

output_lines = []
error_lines = []

file_save_period = 1000 #lines save once

t = time.time()


save_path = Path(args.out_dir)
os.makedirs(str(save_path), exist_ok=True)

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

        for msg in consumer:

            if len(output_lines) == file_save_period:
                with jsonlines.open(str(save_path / f'consumer_{consumer_id:02d}_output_{idx_output_saved:06d}.jsonl'),
                                    'w') as fw:
                    fw.write_all(output_lines)
                print(f'saveing to output file consumer_{consumer_id:02d}_output_{idx_output_saved:06d}.txt')
                idx_output_saved += 1
                output_lines = []

            if len(error_lines) == file_save_period:
                with jsonlines.open(str(save_path / f'consumer_{consumer_id:02d}_error_{idx_error_saved:06d}.jsonl'),
                                    'w') as fw:
                    fw.write_all(error_lines)
                print(f'saveing to error file consumer_{consumer_id:02d}_output_{idx_error_saved:06d}.txt')
                idx_error_saved += 1
                error_lines = []

            try:
                ar_sen = msg.value.decode('utf-8').strip()

                if ar_sen == '':
                    continue

                en_sen, url = get_translate(driver, ar_sen)

                output_lines.append(TransResult(ar_sen, en_sen, url))

                print(f'[{len(output_lines)}] SUCCESS msg at partition={msg.partition}, offset={msg.offset}, timestamp={msg.timestamp}')
            except Exception as e:

                print(f'[{len(error_lines)}] ERROR msg at partition={msg.partition}, offset={msg.offset}, timestamp={msg.timestamp}, e={e.__class__.__name__}')
                print(e)

                error_lines.append(TransResult(ar_sen, None, None, e.__class__.__name__))

    except Exception as e:

        if len(output_lines) > 0:
            with jsonlines.open(str(save_path / f'consumer_{consumer_id:02d}_output_{idx_output_saved:06d}.jsonl'), 'w') as fw:
                fw.write_all(output_lines)


        if len(error_lines) > 0:
            with jsonlines.open(str(save_path / f'consumer_{consumer_id:02d}_error_{idx_error_saved:06d}.jsonl'), 'w') as fw:
                fw.write_all(error_lines)

        print(e)

        driver.close()
