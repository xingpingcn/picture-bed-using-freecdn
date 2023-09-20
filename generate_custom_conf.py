'''
urllib3   1.25.11
nodejs    16.10.0
freecdn   0.3.1
requests
'''
# 写到后面发现把多线程写成class会方便很多，但是快写完了就懒得改了，，，，

import re
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
import base64
import requests
import urllib
cdn_list = ['https://jsd.cdn.zzko.cn/gh/', 'https://cdn.jsdelivr.us/gh/',
            'https://cdn.jsdelivr.ren/gh/', 'https://cdn.jsdelivr.net/gh/']

os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.

is_use_proxy = True
proxies_dict = {'http': 'socks5://127.0.0.1:10808',
                        'https': 'socks5://127.0.0.1:10808'}
user = 'xingpingcn'
dir_for_custom_conf = 'dir_for_custom_conf' #储存文件的文件夹名称
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Ch-Ua-Platform': "Windows",
    'Cache-Control': 'no-cache',
}


def CalcFileSha256_with_base64(filname):
    ''' calculate file sha256 '''
    with open(filname, "rb") as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        hash_value = sha256obj.digest()
        return base64.b64encode(hash_value).decode()



def url_encode(url):
    return urllib.parse.quote(url,safe='/()@:?.$#%')

def download_file_return_hash(line: str, headers=headers):
    res_url = f'{user}/'+line.split(f'/{user}/')[-1]
    path_url = res_url.replace('/', '')
    # print('start download')
    if not os.path.exists(f'{dir_for_custom_conf}/{path_url}'):  # 下载图片，用于计算hash
        r = requests.session()
        if is_use_proxy:
            r.proxies = proxies_dict
        res_img = r.get(line, stream=True, headers=headers)
        if res_img.status_code == 200:
            with open(f'{dir_for_custom_conf}/{path_url}', 'wb') as image_download:
                for chunk in res_img.iter_content(chunk_size=32):
                    image_download.write(chunk)
            print(f'download completed.\n{line}')
        else:
            print(
                f"\033[5;30;45mdownload one of the pictures failed\n{line}\033[0m")
    hash256 = CalcFileSha256_with_base64(f'{dir_for_custom_conf}/{path_url}')  # 计算hash
    return hash256, res_url


def write_file(bak_file, line: str, file_to_w, lock,cdn_list=cdn_list):
    if bak_file:  # 如果存在bak_conf文件
        line_formated = re.escape(line)  # 格式化url
        re_obj = re.compile(f'{line_formated}.*?\thash=(.*?)\n', flags=re.S)
        re_res = re_obj.search(bak_file)
        if re_res:
            # 如果在custom.bak.conf文件中存在url和hash，那么就不下载。
            hash256 = re_res.group(1)
            res_url = f'{user}/'+line.split(f'/{user}/')[-1]
        else:
            hash256, res_url = download_file_return_hash(line)
    else:
        hash256, res_url = download_file_return_hash(line)
    with lock:
        file_to_w.write(line+'\n')
        
        for cdn in cdn_list:
            file_to_w.write('\t'+cdn+res_url+'\n')  # 写入cdn列表
        file_to_w.write('\t'+'hash='+str(hash256)+'\n')  # 写入hash

def main():

    try:
        os.remove('./custom.bak.conf')
    except:
        pass
    try:
        os.rename('./custom.conf', './custom.bak.conf')
    except:
        pass
    lock = threading.Lock()
    pool = ThreadPoolExecutor(16)
    if not os.path.exists(f'{dir_for_custom_conf}'):
        os.makedirs(f'{dir_for_custom_conf}')
    with open('./custom.conf', 'w', encoding='utf8') as file_to_w:
        file_to_w.write('@global\n\topen_timeout=0\n')  # 通用文件
        bak_file = None
        if os.path.isfile('./custom.bak.conf'):
            # 备份文件储存上一个custom.conf的信息，如果存在hash就不下载
            with open('./custom.bak.conf', 'r') as custom_bak_conf:
                bak_file = custom_bak_conf.read()
        with open('./urls.txt', 'r', encoding='utf8') as file_of_urls:

            for line in file_of_urls.readlines():  # 读取需要处理的url
                line = line.replace('\n', '')
                # 验证是否是合法url
                if not re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', line):
                    print('非法url！如果是urls.txt文件结尾或开头的空白符请忽略这条警告。')
                    print(line)
                    continue
                else:

                    pool.submit(write_file, bak_file, url_encode(line),
                                file_to_w, cdn_list=cdn_list,lock=lock)
            pool.shutdown()
    print('done!')
if __name__ == '__main__':
    main()
