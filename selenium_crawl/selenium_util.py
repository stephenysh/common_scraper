import selenium.webdriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait

def get_translate(driver: webdriver, input: str) -> tuple:

    assert input is not None
    assert len(input) != 0

    src_elem = WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector("textarea[id='source']"))

    src_elem.clear()
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector("div[class='tlid-results-container results-container empty']"))

    src_elem.send_keys(input)
    out_elem = WebDriverWait(driver, 10).until(
        lambda d: d.find_element_by_css_selector("span[class='tlid-translation translation'] span"))

    return out_elem.text
