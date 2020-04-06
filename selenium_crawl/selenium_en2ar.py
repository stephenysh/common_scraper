import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(format='[%(asctime)s %(filename)s %(lineno)d %(levelname)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__file__)

import time

import selenium.webdriver as webdriver
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()

driver.get("https://translate.google.com/")
assert "Google Translate" in driver.title

button_elem = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='tl-more tlid-open-target-language-list']")))

button_elem.click()

ar_bnt = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (By.XPATH, "(//div[@class='language_list_item language_list_item_language_name'][text()='Arabic'])[3]")
    )
)

ar_bnt.click()


def get_web_translation(input: str) -> tuple:
    try:
        # if random.random()< 0.5:
        #     raise RuntimeError('TESTERROR')

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
            lambda d: d.find_element_by_css_selector("span[class='tlid-translation translation']"))

        return out_elem.text, None

    except Exception as e:
        return None, e


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--pattern')

    args = parser.parse_args()

    input_path = Path(args.input)

    assert input_path.exists()

    if input_path.is_dir():
        assert args.pattern is not None
        logger.info(f'find files in {input_path}/{args.pattern}')
        files = [file for file in input_path.rglob(args.pattern)]
    else:
        files = [input_path]

    output_path = input_path.parent.joinpath(f'{input_path.stem}_en2ar.json')

    fw = output_path.open('w', encoding='utf-8')
    logger.info(f'write result into new file:{output_path}')

    if len(files) == 0:
        logger.warning(f'no file found, exit')
        exit(1)

    for file in files:
        with file.open('rb') as fr:
            for lineno, line in enumerate(fr, start=1):

                line = line.decode('utf-8', errors='ignore')
                line = line.strip()
                if line == '':
                    continue

                res, err = get_web_translation(line)

                if res is None:
                    logger.error(f"file {file} lineno {lineno} ERROR {err.__class__.__name__}")
                    success = False
                    error_msg = err.__class__.__name__
                else:
                    logger.info(f"file {file} lineno {lineno} SUCCESS")
                    success = True
                    error_msg = None

                json_str = json.dumps(dict(success=success,
                                           ar_sen=res,
                                           en_sen=line,
                                           idx=f'{file}:{lineno}',
                                           error=error_msg),
                                      ensure_ascii=False)
                fw.write(json_str + '\n')
    fw.close()
    driver.close()
