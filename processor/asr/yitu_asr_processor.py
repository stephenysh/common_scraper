import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from pathlib import Path

import librosa
import numpy as np
import requests
import scipy.io.wavfile as wavfile
import soundfile as sf

from util.log_util import getLogger
from util.redis_util import getRedisClient
from util.time_util import get_utc_timestamp

logger = getLogger("YiTUASR")


def get_HmacSha256(message, secret_key):
    return hmac.new(bytes(secret_key, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256).hexdigest()


def check_amend_wav(filename: str, amend_after_check):
    assert Path(filename).is_file(), "input file not exists"

    tmpfiles = []

    audio_file = sf.SoundFile(filename)
    audio_seconds = len(audio_file) / audio_file.samplerate

    try:
        assert audio_seconds < 30, "input should be shorter than 30 seconds"

        assert audio_file.subtype == 'PCM_16', "input should be PCM_16"

        assert audio_file.samplerate == 16000, "input sample rate should be 16KHz"

        tmpfiles = [filename]
    except AssertionError as e:
        if amend_after_check:
            input_path = Path(filename)
            sr = 16 * 1000
            data, _ = librosa.load(str(input_path), sr=sr)
            # convert sample precision
            data = (data * 32768).astype(np.int16)

            duration_second = data.shape[0] / sr
            split_second = 30
            split_num = int(duration_second / split_second) + 1

            logger.warning(f'convert input to 16KHz PCM_16 maxlen {split_second}s wav files')

            for idx, split_data in enumerate(np.array_split(data, split_num)):
                split_name = f"/tmp/{uuid.uuid1()}{input_path.suffix}"
                wavfile.write(split_name, sr, split_data)
                tmpfiles.append(split_name)
        else:
            raise e

    return tmpfiles


def getYituASR(filename: str, timeout=60, amend_after_check=False):
    tmpfiles = check_amend_wav(filename, amend_after_check)

    dev_id = "6688"
    dev_key = "8f36fc68a4da4da3b8563e57b0e971b8"

    res_list = []
    for tmpfile in tmpfiles:

        audio_file = sf.SoundFile(tmpfile)
        audio_seconds = len(audio_file) / audio_file.samplerate

        timestamp = f"{get_utc_timestamp()}"
        signature = get_HmacSha256(message=f'{dev_id}{timestamp}', secret_key=dev_key)
        logger.debug(f"dev_id: {dev_id}")
        logger.debug(f"dev_key: {dev_key}")
        logger.debug(f"timestamp: {timestamp}")
        logger.debug(f"signature: {signature}")

        with open(str(tmpfile), 'rb') as fr:
            data = fr.read()
            encoded_bytes = base64.b64encode(data)
            encoded_str = encoded_bytes.decode('utf-8')

        url = "http://asr-prod-english.yitutech.com/v2/asr"
        json_obj = {
            "data": encoded_str,
        }
        headers = {
            "x-dev-id": dev_id,
            "x-signature": signature,
            "x-request-send-timestamp": timestamp,
            "Content-Type": "application/json",
        }
        logger.debug(f"headers: {headers}")
        logger.debug(f"json_obj: {json_obj}")

        t0 = time.time()
        res = requests.post(url, json=json_obj, headers=headers, timeout=timeout)
        request_time = time.time() - t0

        if res.status_code != 200:
            res_list.append(res)
            continue

        result = json.loads(res.text)
        result['request_time'] = request_time
        result['input_length'] = audio_seconds
        result['status_code'] = res.status_code

        res_list.append(result)
        if tmpfile.startswith('/tmp'):
            os.remove(tmpfile)
    return res_list


def yitu_asr_wrapper(line: str, line_key: str) -> str:
    redis_cli = getRedisClient(db=0)
    redis_infer = redis_cli.get(line_key)

    parts = line.split('|')
    wavname = parts[0]
    wavpath = Path('/Users/shihangyu/Data/LJSpeech-1.1/wavs').joinpath(f'{wavname}.wav')
    label1 = parts[1]
    label2 = parts[2]

    if redis_infer is not None:
        return json.dumps(dict(wavname=wavname, label1=label1, label2=label2, yitu_infer=redis_infer))
    else:
        try:
            yitu_infer = getYituASR(str(wavpath))['text']
            redis_cli.set(line_key, yitu_infer)
        except Exception as e:
            logger.error(f'{line_key}: {e}')
            yitu_infer = None
        return json.dumps(dict(wavname=wavname, label1=label1, label2=label2, yitu_infer=yitu_infer))


def request_ljspeech():
    wav_path = '/Users/shihangyu/Data/LJSpeech-1.1/wavs'
    wavs = Path(wav_path).glob("*.wav")
    wavs = [wav for wav in wavs]

    from util.redis_util import getRedisClient
    redis_cli = getRedisClient(db=2)

    for idx, wav in enumerate(wavs):
        redis_result = redis_cli.get(wav.stem)
        if redis_result is not None:
            logger.warning(f"[{idx}] wav {wav} already have result in redis")
            continue
        else:
            try:
                res_list = getYituASR(str(wav), timeout=2000, amend_after_check=True)
                logger.info(f"[{idx}] wav {wav}: res {res_list}")
                redis_cli.set(wav.stem, json.dumps(res_list))
            except Exception as e:
                logger.error(f"[{idx}] wav {wav}: error {e}")


def request_LibriSpeech():
    wav_path = '/Users/shihangyu/Downloads/LibriSpeech_merged/test-clean/flac/'
    wavs = Path(wav_path).glob("*.flac")
    wavs = [wav for wav in wavs]
    wavs = sorted(wavs, key=lambda w: w.name)

    from util.redis_util import getRedisClient
    redis_cli = getRedisClient(db=4)

    for idx, wav in enumerate(wavs):
        redis_result = redis_cli.get(wav.stem)
        if redis_result is not None:
            # logger.warning(f"[{idx}] wav {wav} already have result in redis")
            continue
        else:
            try:
                res_list = getYituASR(str(wav), timeout=2000, amend_after_check=True)
                logger.info(f"[{idx}] wav {wav}: res {res_list}")
                if 403 in [res.status_code for res in res_list if isinstance(res, requests.Response)]:
                    return -1

                redis_cli.set(wav.stem, json.dumps(res_list))
            except Exception as e:

                logger.error(f"[{idx}] wav {wav}: error {e}")

    return 0


if __name__ == '__main__':
    # pprint(getYituASR("/Users/shihangyu/Data/LJSpeech-1.1/wavs/LJ001-0001.wav", amend_after_check=True))
    # pprint(getYituASR("/Users/shihangyu/Scripts/python/common_scraper/processor/out_30.wav", timeout=2000, amend_after_check=True))
    request_LibriSpeech()
