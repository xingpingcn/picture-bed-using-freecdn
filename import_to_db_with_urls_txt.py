from concurrent.futures import ThreadPoolExecutor, wait
import threading
import os
import sys
import re
import urllib
import requests
import hashlib
import base64
import sqlite3
cdn_list = ['https://jsd.cdn.zzko.cn/gh/', 'https://cdn.jsdelivr.us/gh/',
            'https://cdn.jsdelivr.ren/gh/', 'https://cdn.jsdelivr.net/gh/', 'https://raw.githubusercontent.com/']

blog_md_file_dir = './source/_posts'
is_output_to_txt = False
os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.

is_use_proxy = True
if is_use_proxy:    
    proxies_dict = {'http': 'socks5://127.0.0.1:10808',
                        'https': 'socks5://127.0.0.1:10808'}
else:
    proxies_dict ={}
dir_for_custom_conf = 'dir_for_custom_conf'  # 储存文件的文件夹名称
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Ch-Ua-Platform': "Windows",
    'Cache-Control': 'no-cache',
}


class main():
    def __init__(self, name_of_conf_to_write) -> None:
        if not os.path.exists(f'{dir_for_custom_conf}'):
            os.makedirs(f'{dir_for_custom_conf}')
        self.name_of_conf_to_writ = name_of_conf_to_write
        self.pool = ThreadPoolExecutor(32)
        self.lock = threading.Lock()
        self.thread_list = []
        self.lock_for_write_file = threading.Lock()

    def is_url_in_db(self, url, cursor) -> bool:
        '''
        不存在的话返回fasle
        存在返回ture
        '''

        values = cursor.execute(
            'select * from table_urls where url=?', (f'{url}',)).fetchall()

        return values != []

    def get_hash_in_db(self, url, cursor) -> str:
        values = cursor.execute(
            'select * from table_urls where url=?', (f'{url}',)).fetchall()
        return values[0][0]

    def url_encode(self, url):
        '''
        http请求需要url_encode
        '''
        return urllib.parse.quote(url, safe='/()@:?.$#%')

    def url_split(self, url: str):
        '''
        分离url
        xxx/gh/user/aaa or raw.githubusercontent.com/user/aaa -> user/aaa
        param url 为url encode后的url
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

    def CalcFileSha256_with_base64(self, filname):
        ''' calculate file sha256 '''
        with open(filname, "rb") as f:
            sha256obj = hashlib.sha256()
            sha256obj.update(f.read())
            hash_value = sha256obj.digest()
            return base64.b64encode(hash_value).decode()

    def down_file(self, url: str, path_url):
        r = requests.session()
        if is_use_proxy:
            r.proxies = proxies_dict
        res_img = r.get(url, stream=True, headers=headers)
        if res_img.status_code == 200:
            with open(f'{dir_for_custom_conf}/{path_url}', 'wb') as image_download:
                for chunk in res_img.iter_content(chunk_size=32):
                    image_download.write(chunk)
            print(f'[download completed] {url}')
        else:
            print(
                f"\033[5;30;45m[error] download one of the pictures failed↓\n{url}\033[0m")

    def import_url_to_db(self, url):
        try:
            sqlite3_conn = sqlite3.connect(os.path.join(
                os.path.expanduser('~'), '.freecdn\custom.db'))
            cursor = sqlite3_conn.cursor()
            if not self.is_url_in_db(url, cursor):
                res_url = self.url_split(url)
                path_url = res_url.replace('/', '')  # 下载文件命名
                if not os.path.exists(f'{dir_for_custom_conf}/{path_url}'):
                    self.down_file(url, path_url)
                hash256 = self.CalcFileSha256_with_base64(
                    f'{dir_for_custom_conf}/{path_url}')  # 计算hash

                # 写入url hash到db
                with self.lock:
                    cursor.execute(
                        f'insert into table_urls (hash, url) values (\'{hash256}\', \'{url}\')')
                    sqlite3_conn.commit()
                print(f'[success] import {url} to db')

        except Exception as e:
            print(e, '↓\nurl: '+url)
        else:
            try:
                res_url = self.url_split(url)
                path_url = res_url.replace('/', '')
                with self.lock_for_write_file:
                    self.f_to_w.write(f'\n{url}')
                    for cdn in cdn_list:
                        if not cdn == 'https://raw.githubusercontent.com/':
                            self.f_to_w.write(f'\n\t{cdn}{res_url}')
                        else:
                            try:
                                res_url2 = re.search(
                                    r'@(\S+?)/', f'{res_url}').group(1)
                                res_url = res_url.replace(
                                    f'@{res_url2}', f'/{res_url2}')
                                self.f_to_w.write(f'\n\t{cdn}{res_url}')
                            except:
                                pass
                    self.f_to_w.write(
                        f'\n\thash={self.get_hash_in_db(url,cursor)}')
            except Exception as e:
                print(e)
        finally:
            cursor.close()
            sqlite3_conn.close()

    def run(self):
        with open('./urls.txt', 'r', encoding='utf8') as f:
            try:
                self.f_to_w = open(
                    f'./{self.name_of_conf_to_writ}', 'w', encoding='utf8')
                self.f_to_w.write('@global\n\topen_timeout=0')
                for url in f.readlines():
                    url = url.replace('\n', '')
                    # 验证是否是合法url
                    if not re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', url):
                        print('非法url！如果是urls.txt文件结尾或开头的空白符请忽略这条警告。')
                        print(url)
                        continue
                    else:

                        self.thread_list.append(self.pool.submit(
                            self.import_url_to_db, self.url_encode(url)))
            except Exception as e:
                print(e)

        wait(self.thread_list)
        self.f_to_w.close()


if __name__ == '__main__':
    main('custom.conf').run()
