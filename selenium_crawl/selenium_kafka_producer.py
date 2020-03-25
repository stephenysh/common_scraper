import json
from kafka import KafkaProducer
import json

from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='0.0.0.0:9092')

# input = '/home/shihangyu/news_3_tail20.txt'
input = '/home/shihangyu/test_100K_ar_v_3.txt'

idx = 0
with open(input, 'r', encoding='utf-8') as fr:
    while True:

        sentence = fr.readline()
        if sentence == '':
            break
        sentence = sentence.strip()
        json_obj = dict(idx=idx, text=sentence)
        json_str = json.dumps(json_obj)
        future = producer.send('google', json_str.encode('utf-8'))
        result = future.get(timeout=60)
        print(f'[{idx}]: {result}')

        idx += 1
        # if idx >= 10:
        #     break