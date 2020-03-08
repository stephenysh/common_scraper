import json
import re
import time

times = 5000000

t1 = time.time()
text = '[{"url":"dasdasd","content":"ggdsfdsffds"}]'
for _ in range(times):
    json_obj = json.loads(text)
    content = json_obj[0]["content"]
print(f"time1: {time.time() - t1}")


re_json = re.compile(r'"content":"([^\"]+)"')

t2 = time.time()
for _ in range(times):
    m = re.findall(re_json, text)
print(f"time2: {time.time() - t2}")

