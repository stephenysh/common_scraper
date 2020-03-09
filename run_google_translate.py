import requests
from html import unescape
import time
import json
from pathlib import Path

from google.cloud import translate_v2
from google.cloud import translate_v3


def google_trans_v2(input: str, src_lang='ar', dest_lang='en') -> str:
    translate_client = translate_v2.Client()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(input, target_language=dest_lang)

    return unescape(result['translatedText'])


def google_trans_v3(input: str, src_lang='ar', dest_lang='en', project_id='stately-arc-243917') -> str:
    client = translate_v3.TranslationServiceClient()

    parent = client.location_path(project_id, "us-central1")

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        parent=parent,
        contents=[input],
        mime_type="text/plain",  # mime types: text/plain, text/html
        source_language_code=src_lang,
        target_language_code=dest_lang,
    )
    # Display the translation for each input text provided
    return response.translations[0].translated_text


def google_trans_v3_rest(input: str, src_lang='ar', dest_lang='en', project_id='stately-arc-243917') -> str:
    token = 'ya29.c.Ko8BwAfFqMaXoWPcaDB8o-R8Z40RwRB7Gnyz-bxVdL3jgAIGzcx19YTKfbBYRaLgpxFw6Z1JjQE8r2CDesytY5j19sTpUh1OIQgsC_uKGkSjN2_1Z6bb5xkoCKBaVlq995U1cproWR2DkRNcQOfwJIVYQDAou_fVFWbvsyDb7omLQgyrqrCwRkdjeA59xePzbw0'
    url = f'https://translation.googleapis.com/v3/projects/{project_id}:translateText'
    payload = {
        "sourceLanguageCode": src_lang,
        "targetLanguageCode": dest_lang,
        "contents": [input]
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept-Charset': 'UTF-8'}
    res = requests.post(url, data=payload, headers=headers)

    json_obj = json.loads(res.text)

    return unescape(json_obj['translations'][0]['translatedText'])


def get_google_translate(input: str, src_lang='ar', dest_lang='en') -> str:

    time.sleep(15)

    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src_lang}&tl={dest_lang}&dt=t&q={input}"

    try:
        res = requests.get(url)

        json_obj = json.loads(res.text)

        output = ''.join([per_sen[0] for per_sen in json_obj[0]])

    except Exception as e:
        print(e)

        output = None

    return output

if __name__ == '__main__':

    test_sentence = 'وقالت الجماعات والتي ضمت "جبهة النصرة" و"لواء التوحيد" و "كتائب أحرار الشام"، وهي من اكبر المجموعات المقاتلة في شمال سوريا الى جانب غيرها من الفصائل انها توافقت على تأسيس "دولة إسلامية" بحسب '
    print(google_trans_v2(test_sentence))
    # url = f"https://translation.googleapis.com/language/translate/v2?q={sentence}&target={dest_lang}"


    # input_file = Path('/Users/shihangyu/10K_sample.txt')
    #
    # fw = open('10K_sample_ar.txt', 'w', encoding='utf-8')
    #
    # fr = open(str(input_file), 'r', encoding='utf-8')
    #
    # idx = 0
    #
    # t = time.time()
    #
    # while True:
    #     line = fr.readline()
    #
    #     if line == '':
    #         break
    #
    #     ar_sen = line.strip().split('|')[-1]
    #
    #     en_sen_v2 = google_trans_v2(ar_sen)
    #     en_sen_v3 = google_trans_v3_rest(ar_sen)
    #     en_sen_v3_rest = google_trans_v3_rest(ar_sen)
    #
    #     new_line = line.strip() + '|' + en_sen_v2 + '|' + en_sen_v3 + '\n'
    #
    #     fw.write(new_line)
    #
    #     idx += 1
    #
    #     if idx % 1 == 0:
    #         print(f'line [{idx}] v2==v3: {en_sen_v2 == en_sen_v3} v3==v3_rest: {en_sen_v3 == en_sen_v3_rest}')
    #
    # print(f'total time {time.time() - t}')
    #
    #
    #
