import time
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='0.0.0.0:9092')

input = '/home/shihangyu/news_3.txt'

idx = 0
with open(input, 'r', encoding='utf-8') as fr:
    while True:

        sentence = fr.readline()
        if sentence == '':
            break
        sentence = sentence.strip()
        future = producer.send('google', sentence.encode('utf-8'))
        result = future.get(timeout=60)
        print(result)

        # idx += 1
        #
        # if idx >= 10:
        #     break