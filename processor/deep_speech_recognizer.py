# https://github.com/mozilla/DeepSpeech
# pip install deepspeech
# pip install deepspeech-gpu
# brew install sox / apt-get install sox

import shlex
import subprocess
import wave
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from deepspeech import Model

try:
    from shhlex import quote
except ImportError:
    from pipes import quote

from util.log_util import getLogger


class DeepSpeechRecognizer:

    def __init__(self):

        self.file_path = Path(__file__).parent

        self.model = Model('/Users/shihangyu/Scripts/python/stt_server/model/deepspeech-0.6.1-models/output_graph.pbmm',
                           aBeamWidth=500)

        self.desired_sample_rate = self.model.sampleRate()

        self.logger = getLogger(self.__module__)

        self.tmp_path = self.file_path / 'tmp.wav'

    def __convert_samplerate(self, audio_path):
        sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(
            quote(audio_path), self.desired_sample_rate)
        try:
            output = subprocess.check_output(shlex.split(sox_cmd), stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
        except OSError as e:
            raise OSError(e.errno,
                          'SoX not found, use {}hz files or install it: {}'.format(self.desired_sample_rate,
                                                                                   e.strerror))

        return self.desired_sample_rate, np.frombuffer(output, np.int16)

    def inference(self, audio_path):

        try:
            fin = wave.open(audio_path, 'rb')
        except Exception as e:

            x, _ = librosa.load(str(audio_path), sr=16000)

            sf.write(str(self.tmp_path), x, 16000)

            fin = wave.open(str(self.tmp_path), 'rb')

        fs = fin.getframerate()

        if fs != self.desired_sample_rate:
            self.logger.warning(f'Warning: original sample rate ({fs}) is different than {self.desired_sample_rate}hz. '
                                f'Resampling might produce erratic speech recognition.')
            fs, audio = self.__convert_samplerate(audio_path)
        else:
            audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

        fin.close()

        output = self.model.stt(audio)

        self.logger.debug(f"DeepSpeechRecognizer inference output: {output}")

        return output


if __name__ == "__main__":
    ds = DeepSpeechRecognizer()

    print(ds.inference('/Users/shihangyu/Scripts/python/stt_server/audio_files/derek.wav'))
    print(ds.inference('/Users/shihangyu/Scripts/python/stt_server/audio_files/derek.wav'))
