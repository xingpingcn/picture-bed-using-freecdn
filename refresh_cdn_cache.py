import requests,re
import os
from config import *
from concurrent.futures import ThreadPoolExecutor, wait
import threading
def main():
    pool = ThreadPoolExecutor(32)
    lock = threading.Lock()
    ThreadPool_list = []
    url_list = []
    re_obj = re.compile(r'cdn.jsdelivr.net/gh/(.*)')
    with open(os.path.join('./public','manifest-full.txt'),'r',encoding='utf8') as f:
        f_content = f.read()
        with open(os.path.join('./public','freecdn-manifest.txt'),'r',encoding='utf8') as f:
            f_content = f_content+'\n'+f.read()
        re_res = re_obj.findall(f_content)
        for res in re_res:
            if res not in url_list:
                with lock:
                    url_list.append(res)
                    ThreadPool_list.append(pool.submit(refresh_cdn_cache,res)) 
    wait(ThreadPool_list) 
    print('refresh cdn cache complete.')
def refresh_cdn_cache(url):
    requests.get('https://purge.jsdelivr.net/gh/'+url, proxies=proxies_dict)
if __name__ ==  '__main__':
    main()