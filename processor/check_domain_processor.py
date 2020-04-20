import json
import re


def check_domain(line: str, line_key: str):
    m = re.match(r"^/hdd/crawl_result/ysh/classificaiton_label_(\d+)\.json:(\d+)$", line_key)
    if not m:
        print("not match")

    label = int(m.group(1))

    jobj = json.loads(line)

    if jobj.get("label_id") != label:
        print("invalid label")

    if len(jobj.get("paragraphs")) == 0:
        print("empty paragraphs")

    return None
