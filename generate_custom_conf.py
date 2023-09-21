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
            'https://cdn.jsdelivr.ren/gh/', 'https://cdn.jsdelivr.net/gh/', 'https://raw.githubusercontent.com/']

os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.

is_use_proxy = True
proxies_dict = {'http': 'socks5://127.0.0.1:10808',
                        'https': 'socks5://127.0.0.1:10808'}
dir_for_custom_conf = 'dir_for_custom_conf'  # 储存文件的文件夹名称
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
    return urllib.parse.quote(url, safe='/()@:?.$#%')


def url_split(url: str):
    '''
    分离url
    xxx/gh/user/aaa or xxx/user/aaa -> user/aaa
    xxx/gh/aaa -> aaa 
    param url 为url encode后的url
    return user/aaa or aaa 
    '''
    re_obj = re.compile(
        f'http.*?(?:(?<=/gh/)|(?=raw.githubusercontent.com/))(.*)\s*')
    res = re_obj.search(url)
    if res:
        if not 'raw.githubusercontent.com' in res.group(1):
            return res.group(1)
        else:
            res = res.group(1).replace('raw.githubusercontent.com/', '')
            re_res = re.search(r'.*?/.*?/(.*?)/.*', res).group(1)
            res = res.replace(f'/{re_res}', f'@{re_res}')
            return res
    else:
        print(f'unsupported url\n({url})')


def download_file_return_hash(line: str, headers=headers):
    res_url = url_split(line)  # 定位文件的url
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
    hash256 = CalcFileSha256_with_base64(
        f'{dir_for_custom_conf}/{path_url}')  # 计算hash
    return hash256, res_url


def write_file(bak_file, line: str, file_to_w, lock, cdn_list=cdn_list):
    if bak_file:  # 如果存在bak_conf文件
        line_formated = re.escape(line)  # 格式化url
        re_obj = re.compile(f'{line_formated}.*?\thash=(.*?)\n', flags=re.S)
        re_res = re_obj.search(bak_file)
        if re_res:
            # 如果在custom.bak.conf文件中存在url和hash，那么就不下载。
            hash256 = re_res.group(1)
            res_url = url_split(line)  # 定位文件的url
        else:
            hash256, res_url = download_file_return_hash(line)
    else:
        hash256, res_url = download_file_return_hash(line)
    with lock:
        file_to_w.write('\n'+line)

        for cdn in cdn_list:
            if not cdn == 'https://raw.githubusercontent.com/':
                file_to_w.write(f'\n\t{cdn}{res_url}')
            else:
                try:
                    res_url2 = re.search(r'@(.*?)/', f'{res_url}').group(1)
                    res_url = res_url.replace(f'@{res_url2}', f'/{res_url2}')
                    file_to_w.write(f'\n\t{cdn}{res_url}')
                except:
                    pass
        file_to_w.write('\n\t'+'hash='+str(hash256))  # 写入hash


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
        try:
            file_of_urls = open('./urls.txt', 'r', encoding='utf8') 

            for line in file_of_urls.readlines():  # 读取需要处理的url
                line = line.replace('\n', '')
                # 验证是否是合法url
                if not re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', line):
                    print('非法url！如果是urls.txt文件结尾或开头的空白符请忽略这条警告。')
                    print(line)
                    continue
                else:

                    pool.submit(write_file, bak_file, url_encode(line),
                                file_to_w, cdn_list=cdn_list, lock=lock)
            pool.shutdown()
            print('custom.conf generated.')
        except FileNotFoundError as e:
            print('warning: there exists no file named \'urls.txt\'. if you don\'t need to generate a custom.conf file from urls.txt, please ignore this warning.')
        else:
            file_of_urls.close()

    


if __name__ == '__main__':
    main()
