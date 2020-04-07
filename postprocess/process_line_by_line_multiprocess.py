import argparse
from pathlib import Path

from tqdm import tqdm

from postprocess.pool_wrapper import PoolWrapper
from processor.html_processor import htmlResponseToLines
from util.log_util import getLogger
from util.redis_util import getRedisClient
from util.util import mapLineCount

if __name__ == '__main__':
    logger = getLogger('process_line_by_line_multiprocess')

    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--pattern')
    parser.add_argument('--postfix', required=True)
    parser.add_argument('--save_result', action='store_true')
    parser.add_argument('--save_redis', action='store_true')
    parser.add_argument('--redis_db', type=int, default=0)

    args = parser.parse_args()

    save_result = args.save_result

    save_redis = args.save_redis

    redis_cli = getRedisClient(db=args.redis_db)

    input_path = Path(args.input)

    assert input_path.exists()

    print(args)

    pw = PoolWrapper(htmlResponseToLines, poolsize=1)

    if input_path.is_dir():
        assert args.pattern is not None
        logger.info(f'find files in {input_path}/{args.pattern}')
        files = [file for file in input_path.rglob(args.pattern)]
        files = sorted(files, key=lambda x: str(x))
    else:
        files = [input_path]

    if len(files) == 0:
        logger.warning(f'no file found, exit')
        exit(1)

    for file in files:
        if save_result:
            output_path = file.parent.joinpath(f'{file.name}_{args.postfix}')
            fw = output_path.open('w')
            logger.info(f'write file into file: {output_path}')

        total_line_num = mapLineCount(str(file))

        with file.open('rb') as fr:
            for lineno, line in tqdm(enumerate(fr), total=total_line_num):
                line = line.decode('utf-8', errors='ignore')
                line = line.strip()

                line_key = f'{file}:{lineno}'
                if line == '':
                    continue

                processed, res_list = pw.maybeProcessIfFull()

                if processed:
                    if save_result:
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
                if save_result:
                    for res in res_list:
                        if res is None:
                            continue

                        if type(res) == str:
                            fw.write(res + '\n')
                        elif type(res) == list:
                            fw.writelines(l + '\n' for l in res)
                        else:
                            raise RuntimeError('Unknown return type')
