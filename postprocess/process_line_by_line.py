import sys
import argparse
from pathlib import Path

from util import getLogger
from postprocess.line_processors import *
logger = getLogger('read_selenium_output')


class PatternAction(argparse.Action):
     def __init__(self, option_strings, dest, nargs=None, **kwargs):
         if nargs is not None:
             raise ValueError("nargs not allowed")
         super(PatternAction, self).__init__(option_strings, dest, **kwargs)
     def __call__(self, parser, namespace, values, option_string=None):
         print('%r %r %r' % (namespace, values, option_string))
         setattr(namespace, self.dest, values)


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


for file in files:
    with file.open('rb') as fr:
        for lineno, line in enumerate(fr):
            line = line.decode('utf-8', errors='ignore')
            line = line.strip()
            if line == '':
                continue

            line = extract_ar_sen(line)
            if line is None:
                # logger.error(f'file {file} lineno {lineno}')
                continue

            fw.write(line + '\n')