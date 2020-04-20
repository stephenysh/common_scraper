import argparse
from pathlib import Path

from tqdm import tqdm

from processor.asr.yitu_asr_processor import yitu_asr_wrapper
from util.log_util import getLogger
from util.redis_util import getRedisClient
from util.util import mapLineCount

logger = getLogger('read_selenium_output')

from postprocess.line_processors import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--pattern')
    parser.add_argument('--postfix')

    args = parser.parse_args()

    input_path = Path(args.input)

    assert input_path.exists()

    if input_path.is_dir():
        assert args.pattern is not None
        logger.info(f'find files in {input_path}/{args.pattern}')
        files = [file for file in input_path.rglob(args.pattern)]
    else:
        files = [input_path]

    output_path = input_path.parent.joinpath(f'{input_path.stem}{args.postfix}')
    fw = output_path.open('w')
    logger.info(f'write file into {output_path}')

    if len(files) == 0:
        logger.warning(f'no file found, exit')
        exit(1)

    redis_cli = getRedisClient(db=0)

    for file in files:
        total_line_num = mapLineCount(str(file))
        fw = file.parent.joinpath(f'{file.name}_{args.postfix}').open('w')

        with file.open('rb') as fr:
            for lineno, line in tqdm(enumerate(fr, start=1), total=total_line_num):

                line = line.decode('utf-8', errors='ignore')
                line = line.strip()
                if line == '':
                    continue

                line_key = f"{file}:{lineno}"

                redis_line = redis_cli.get(line_key)
                if redis_line is not None:
                    continue

                res = yitu_asr_wrapper(line, line_key)

                fw.write(res + '\n')
