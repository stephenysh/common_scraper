import argparse
from pathlib import Path

from util import getLogger

logger = getLogger('read_selenium_output')

from postprocess.pool_wrapper import PoolWrapper

from util import htmlResponseToLines
from postprocess.line_processors import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--pattern')
    parser.add_argument('--postfix', required=True)

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

    pw = PoolWrapper(htmlResponseToLines)

    for file in files:
        with file.open('rb') as fr:
            for lineno, line in enumerate(fr):
                line = line.decode('utf-8', errors='ignore')
                line = line.strip()
                if line == '':
                    continue

                processed, res_list = pw.maybeProcessIfFull()

                if processed:
                    for res in res_list:
                        if res is None:
                            continue

                        if type(res) == str:
                            fw.write(res + '\n')
                        elif type(res) == list:
                            fw.writelines(l + '\n' for l in res)
                        else:
                            raise RuntimeError('Unknown return type')

                pw.addSample(line)

            processed, res = pw.mustProcessUnlessEmpty()

            if processed:
                for res in res_list:
                    if res is None:
                        continue

                    if type(res) == str:
                        fw.write(res + '\n')
                    elif type(res) == list:
                        fw.writelines(l + '\n' for l in res)
                    else:
                        raise RuntimeError('Unknown return type')