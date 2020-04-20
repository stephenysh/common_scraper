import json

from util.redis_util import getRedisClient

labels = [i + 1 for i in range(15)]
fws = [open(f"/hdd/crawl_result/ysh/classificaiton_label_{label}.json", "w") for label in labels]

redis_cli = getRedisClient(db=15)


def split_domain_processor(line: str, line_key: str):
    jobj = json.loads(line)

    try:

        label = jobj.get("label_id")
        if label not in labels:
            return None

        lines = redis_cli.get(f"label:{label}")

        if lines is None:
            lines = 0
        else:
            lines = int(lines)

        # if lines >= 10:
        #     return None

        if len(jobj.get("paragraphs")) == 0:
            return None

        fw = fws[label - 1]
        fw.write(line + '\n')
        redis_cli.set(f"label:{label}", lines + 1)

    except Exception as e:
        print(e)
        print(jobj.get("label_id"))

    return None
