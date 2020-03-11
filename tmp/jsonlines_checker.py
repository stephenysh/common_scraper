from pathlib import Path

import logging
logging.basicConfig(format='[%(asctime)s %(name)s %(filename)s %(funcName)s %(lineno)d %(levelname)s] %(message)s', level=logging.DEBUG)

from typing import List

from multiprocessing import Pool
import multiprocessing

from MyScraper.postprocess.timer import Timer

from MyScraper.postprocess.line_checkers import *

valid_json_line_checker = ValidJsonLineChecker()
redis_duplicate_line_checker = RedisDuplicateLineChecker()
extract_lines_line_checker = ExtracLinesLineChecker()
def multiprocess_linecheck(line, json_file, line_count_per_file):
    try:
        obj = line
        for line_checker in [valid_json_line_checker, redis_duplicate_line_checker, extract_lines_line_checker]:
            res, obj = line_checker.checkline(obj)
            
    except Exception as e:
        res = False
        print(f'ERROR in file {json_file.name} line [{line_count_per_file}]: {e}')

    return res


class JsonLinesChecker:

    def __init__(self,
                 json_files_folder: str = None,
                 json_files: List[str] = None,
                 line_checkers: List[AbstractLineChecker] = [],
                 **kwargs):
        self.logger = logging.getLogger('JsonLinesChecker')

        if json_files is not None:
            if json_files_folder is not None:
                self.logger.warning('Use given json_files, will ignore json_files_folder.')
            self.json_files_path = None
            self.json_files = [Path(item) for item in json_files]
            self.json_files = sorted(self.json_files, key=lambda f: f.name)
        else:
            if json_files_folder is not None:
                self.json_files_path = Path(json_files_folder)
                self.json_files = [item for item in self.json_files_path.iterdir()]
                self.json_files = sorted(self.json_files, key=lambda f: f.name)
            else:
                raise RuntimeError('Either json_files or json_files_folder should be assigned.')

        self.timer = Timer()

        self.save_no_error_line = False

        self.pool_size = multiprocessing.cpu_count() * 3
        self.pool = Pool(self.pool_size)
        self.logger.info(f'starting pool with size {self.pool_size}')

    def check(self):
        line_count_total = 0

        map_args_list = []
        self.timer.tick('total_time')
        for json_file in self.json_files:

            line_count_per_file = 0
            self.logger.debug(f'Strating file: {json_file}')

            result = []
            with open(str(json_file), 'r', encoding='utf-8') as f:
                while True:
                    try:
                        line = f.readline()
                    except Exception as e:
                        self.logger.error(f'ERROR in file {json_file.name} line [{line_count_per_file}]: {e}')

                        continue

                    if not line:
                        break

                    if len(map_args_list) == self.pool_size:
                        self.pool.starmap(multiprocess_linecheck, map_args_list)
                        map_args_list = []

                    map_args_list.append((line, json_file, line_count_per_file))

                    ############################### real process

                    if line_count_total % 10000 == 0:
                        for res in result:
                            res.get()
                        self.logger.debug(f'reading line [{line_count_total}]')

                    line_count_per_file += 1
                    line_count_total += 1


            self.logger.debug(f'Finish file: {json_file}, total line no [{line_count_per_file}]')

        self.logger.debug(
            f'Total line no [{line_count_total}]')

        self.logger.debug(f'total process time: {self.timer.tock("total_time")}')

        if self.save_no_error_line:
            self.save_file.close()




if __name__ == '__main__':

    jc = JsonLinesChecker(
        # json_files=['/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/bbc_redis_ar_jsons/bbc_redis_ar_08.json'],
        json_files_folder='/media/shihangyu/302b5584-4afe-4898-8d79-e12f41fd7cc6/result/aleqt_redis_ar_jsons',
    )
    
    jc.check()

    
    