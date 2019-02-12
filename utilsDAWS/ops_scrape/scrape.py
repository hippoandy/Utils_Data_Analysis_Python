''' README

This class access list of URLs simultaneously using multi-thread.
Required to specify the parsing functions for web-scraping!

Input: list of URLs to be tested on

Return: data file commitments.
'''

import threading
import textwrap
import queue
import os
import pickle
import requests

from utilsDAWS.ops_file import write_to_json

from traceback import format_exc

class scraper():
    ''' multi-threading scraper '''
    def __init__(self, name='scrape', concurrent=500, base='./data', \
                 timeout=30, parse_func=lambda res: res.text):
        '''
            name: job name, prefix for all data files
            url_lst: all urls to scrape
            res_tmp_lst: temporarily holds response object for urls in url_lst
            parse_func: parsing function, provided by user

            data_base: base directory for all data
            data_path: path for data
            scrape_err_path: path for scrape errors
            parse_err_path: path for parse errors

            job_queue: thread-safe synchronized queue
            lock: Lock for synchronized variable read/write
            concurrent: number of threads
            timeout: timeout for each request
            job_finished: tracking scraping progress

            data_lst: final data, after scraping, all data should be here
            scrape_err_lst: scrape errors, [{'url': <failed url>, 'err': <error msg>}]
            parse_err_lst: parsing errors, [{'url': <failed url>, 'err': <error msg>}]
        '''
        self.name = name
        self.url_lst = []
        self.res_tmp_lst = []
        self.parse_func = parse_func

        self.data_base = base
        self.data_path = os.path.join(self.data_base, f'{name}.json')
        self.scrape_err_path = os.path.join(self.data_base, f'{name}_scrape_err.json')
        self.parse_err_path = os.path.join(self.data_base, f'{name}_parse_err.json')

        self.job_queue = queue.Queue()
        self.lock = threading.Lock()
        self.concurrent = concurrent
        self.timeout = timeout
        self.job_finished = 0

        self.data_lst, self.scrape_err_lst, self.parse_err_lst, self.res_tmp_lst = [], [], [], []

        self._spawn_threads()

    def name_with(self, name):
        ''' consume name and reconfigure paths '''
        self.name = name
        self.data_path = os.path.join(self.data_base, f'{name}.json')
        self.scrape_err_path = os.path.join(self.data_base, f'{name}_scrape_err.json')
        self.parse_err_path = os.path.join(self.data_base, f'{name}_parse_err.json')
        return self

    def urls_with(self, url_lst_to_add):
        ''' consume url list passed by user '''
        if not self.url_lst:
            self.url_lst = url_lst_to_add
        elif self.url_lst:
            self.url_lst.extend(url_lst_to_add)
        return self

    def parse_with(self, parse_func):
        ''' comsume parsing function passed by user '''
        self.parse_func = parse_func
        return self

    def run_once(self):
        ''' run once '''
        pass

    def run_until_done(self):
        ''' run until no scrape_err_lst or parse_err_lst or stuck '''
        pre_url_lst_sorted = None
        self.job_finished = 0
        while self.url_lst or self.scrape_err_lst or self.parse_err_lst:
            if self.scrape_err_lst:
                self.url_lst.extend(list(map(lambda x: x['url'], self.scrape_err_lst)))
            if self.parse_err_lst:
                self.url_lst.extend(list(map(lambda x: x['url'], self.parse_err_lst)))
            if pre_url_lst_sorted and sorted(self.url_lst) == pre_url_lst_sorted:
                self._save()
                print(textwrap.dedent(f'''\
                    stuck, please check scrape_err or parse_err
                    saved result:
                        len(data_lst): {len(self.data_lst)}
                        len(scrape_err_lst): {len(self.scrape_err_lst)}
                        len(parse_err_lst): {len(self.parse_err_lst)}
                '''))
                # added by Andy ----------
                self.job_finished = 0
                self._reset()
				# ---------- added by Andy
                return
            pre_url_lst_sorted = sorted(self.url_lst)

            self.scrape_err_lst.clear()
            self.parse_err_lst.clear()
            print(f'loop started with len(url_lst): {len(self.url_lst)}')
            for url in self.url_lst:
                self.job_queue.put(url)
            self.job_queue.join()
            self.url_lst = []
            self._parse()
            self.res_tmp_lst = []
            self.job_finished = 0

        self._save()
        print(textwrap.dedent(f'''\
            finished
            saved result:
                len(data_lst): {len(self.data_lst)}
                len(scrape_err_lst): {len(self.scrape_err_lst)}
                len(parse_err_lst): {len(self.parse_err_lst)}
        '''))
        self._reset()

    def _save(self):
        ''' save final data. data_lst, scrape_err_lst, parse_err_lst '''
        write_to_json(self.data_path, self.data_lst)
        write_to_json(self.scrape_err_path, self.scrape_err_lst)
        write_to_json(self.parse_err_path, self.parse_err_lst)

    def _reset(self):
        ''' reset all results, clean for another run '''
        # modified by Andy ----------
        self.data_lst.clear()
        self.scrape_err_lst.clear()
        self.parse_err_lst.clear()
        self.res_tmp_lst.clear()
        # ---------- modified by Andy

    def _job(self):
        ''' job for each thread, makes res_tmp_lst '''
        while True:
            url = self.job_queue.get()
            try:
                res = requests.get(url, timeout=self.timeout)
                self.lock.acquire()
                self.res_tmp_lst.append(res)
            except Exception as err:
                self.lock.acquire()
                self.scrape_err_lst.append({'url': url, 'err': str(err)})
            finally:
                self.job_finished += 1
                print(f'process: {100 * self.job_finished / len(self.url_lst):.2f}%', end='\r')
                self.lock.release()
                self.job_queue.task_done()

    def _spawn_threads(self):
        ''' start threads as daemons '''
        for _ in range(0, self.concurrent):
            thread = threading.Thread(target=self._job)
            thread.daemon = True
            thread.start()

    def _parse(self):
        ''' parse res using parse_func '''
        i = 0
        # added by Andy ----------
        print( '\n' )
        # ---------- added by Andy
        for res in self.res_tmp_lst:
            try:
                data = self.parse_func(res)
                self.data_lst.extend(data)
            except Exception as err:
                self.parse_err_lst.append({'url': res.url, 'err': repr(err), 'trace': format_exc() })
                # self.parse_err_lst.append({'url': res.url, 'err': str(err)})
            i += 1
            print(f'parsing... {i}', end='\r')

if __name__ == '__main__':
    pass
