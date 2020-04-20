import json

import jiwer

transformation = jiwer.Compose([
    jiwer.RemoveMultipleSpaces(),
    jiwer.Strip(),
    jiwer.SentencesToListOfWords(),
    jiwer.RemoveEmptyStrings(),
    jiwer.ToLowerCase(),
    jiwer.RemovePunctuation()
])


def calculate_wer(line: str) -> float:
    json_obj = json.loads(line)

    label2 = json_obj.get('label')
    # label2 = label2.replace('-', ' ')

    infer = json_obj['yitu_infer']
    wer_score = jiwer.wer(infer, label2, truth_transform=transformation, hypothesis_transform=transformation)

    json_obj['wer'] = wer_score

    return json.dumps(json_obj)


def mean_wer(filename: str) -> float:
    wer_total = 0
    with open(filename, 'rb') as f:
        for idx, line in enumerate(f, start=1):
            line.decode('utf-8', errors='ignore')
            json_obj = json.loads(line)
            wer_total += json_obj.get('wer')

    print(f'mean wer {wer_total / idx}')


if __name__ == '__main__':
    mean_wer('/Users/shihangyu/Data/LJSpeech-1.1/metadata_train.csv_yitu.json_wer.json')
    mean_wer("/Users/shihangyu/Data/LJSpeech-1.1/metadata_train.csv_ds.json_wer_partial.json")
    mean_wer("/Users/shihangyu/Scripts/python/common_scraper/processor/LibriSpeech.json_wer.json")
