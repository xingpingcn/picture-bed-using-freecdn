from concurrent.futures import ThreadPoolExecutor, wait
import threading
import os
import sys
import re
import urllib
import requests
import hashlib
import base64
import sqlite3,json
from config import *
os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.


class main():
    def __init__(self, name_of_conf_to_write) -> None:
        if not os.path.exists(f'{dir_for_custom_conf}'):
            os.makedirs(f'{dir_for_custom_conf}')
        self.name_of_conf_to_writ = name_of_conf_to_write
        self.pool = ThreadPoolExecutor(32)
        self.lock = threading.Lock()
        self.thread_list = []
        self.lock_for_write_file = threading.Lock()
    def is_vaild_url(self,url,re_obj = None):
        '''
        判断是否合法url
        '''
        if re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', url):
            return True
        else:
            print('非法url！如果是urls.txt文件结尾或开头的空白符请忽略这条警告。')
            print(f'url为：\'{url}\', {re_obj}')
            return False
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
            f'http(.*?)(?:(?<=/gh/)|(?=raw.githubusercontent.com/)|(?<=/npm/))(.*)\s*')
        res = re_obj.search(url)
        if res:
            if not 'raw.githubusercontent.com' in res.group(2):
                if 'gh' in res.group(1):
                    web_space = 'github'
                elif 'npm' in res.group(1):
                    web_space = 'npm'
                return res.group(2), web_space
            else:
                res = res.group(2).replace('raw.githubusercontent.com/', '')
                web_sapce = 'github'
                re_res = re.search(r'.*?/.*?/(.*?)/.*', res).group(2)
                res = res.replace(f'/{re_res}', f'@{re_res}')
                return res, web_sapce
        else:
            print(f'unsupported url\n({url})')

    def get_latest_version_of_npm_hosting(self):
        self.pic_bed_hosting_latest_ver = ''
        self.html_hosting_latest_ver = ''
        if npm_name_of_pic_bed:
            r = requests.get(f'https://registry.npmjs.org/{npm_name_of_pic_bed}',proxies=proxies_dict)
            if r.status_code == 200:
                self.pic_bed_hosting_latest_ver = r.json()["dist-tags"]["latest"]
            
        if npm_name_of_html_package:
            try:
                with open(f'{path_of_package_json}','r',encoding='utf8') as f:
                    self.html_hosting_latest_ver = json.load(f)['version']
            except:
                r = requests.get(f'https://registry.npmjs.org/{npm_name_of_html_package}',proxies=proxies_dict)
                if r.status_code == 200:
                    self.html_hosting_latest_ver = r.json()["dist-tags"]["latest"]

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
    def write_url_to_db(self,url,hash256,cursor= None,sqlite3_conn= None):
        # 写入url hash到db
        if not cursor == None:
            with self.lock:
                cursor.execute(
                    f'insert into table_urls (hash, url) values (\'{hash256}\', \'{url}\')')
                sqlite3_conn.commit()
            print(f'[success] import {url} to db')

    def write_file(self,url,cursor=None,res_url=None,hash256 = None,web_sapce=None):
        '''
        res_url的格式应该为.*?/.*?@.*?/(.*)$
        web_sapce为none的时候表示从md文件中写入，不为none表示从urls.txt中写入
        '''
        
        with self.lock_for_write_file:
            self.f_to_w.write(f'\n{url}')
            for k,v in cdn_list.items():
                for cdn in v:
                    if  k == 'github':
                        if web_sapce == 'github' or web_sapce == None:
                            self.f_to_w.write(f'\n\t{cdn}{res_url}')
                    elif k == 'raw':
                        if web_sapce == 'github' or web_sapce == None:
                            try:
                                res_url2 = re.search(
                                    r'@(\S+?)/', f'{res_url}').group(1)
                                res_url3 = res_url.replace(
                                    f'@{res_url2}', f'/{res_url2}')
                                self.f_to_w.write(f'\n\t{cdn}{res_url3}')
                            except:
                                pass
                    elif k == 'npm':
                        if web_sapce == 'npm':
                            self.f_to_w.write(f'\n\t{cdn}{res_url}')
                            continue
                        if f'{user}' in res_url :
                            try:
                                extension = re.search(r'.*\.(.*)$',res_url).group(1)
                                if extension.lower() in ['png','webp','gif','jpg','jpge','svg','raw'] and not npm_name_of_pic_bed == '':
                                    # 如果是图片则使用npm的图片仓库
                                    resource_path = re.search(r'.*?/.*?@.*?/(.*)$',res_url).group(1)
                                    self.f_to_w.write(f'\n\t{cdn}{npm_name_of_pic_bed}@{self.pic_bed_hosting_latest_ver}/{resource_path}')
                                elif extension.lower() in ['htm','html'] and not npm_name_of_html_package=='':
                                    # 如果是html则使用npm的html仓库
                                    resource_path = re.search(r'.*?/.*?@.*?/(.*)$',res_url).group(1)
                                    self.f_to_w.write(f'\n\t{cdn}{npm_name_of_html_package}@{self.html_hosting_latest_ver}/{resource_path}')
                            except Exception as e:
                                print('[warning] '+str(e), f', when writing npm cdn')

            if not cursor == None:
                self.f_to_w.write(
                    f'\n\thash={self.get_hash_in_db(url,cursor)}')
            else:
                self.f_to_w.write(f'\n\thash={hash256}')
                self.f_to_w.write(f'\n\tmime=text/html')
                
    def import_url_to_file(self, url):
        try:
            sqlite3_conn = sqlite3.connect(os.path.join(
                os.path.expanduser('~'), '.freecdn\custom.db'))
            cursor = sqlite3_conn.cursor()
            if not self.is_url_in_db(url, cursor):
                res_url,web_sapce = self.url_split(url)
                path_url = res_url.replace('/', '')  # 下载文件命名
                if not os.path.exists(f'{dir_for_custom_conf}/{path_url}'):
                    self.down_file(url, path_url)
                hash256 = self.CalcFileSha256_with_base64(
                    f'{dir_for_custom_conf}/{path_url}')  # 计算hash
                # 写入数据库
                self.write_url_to_db(url,hash256,cursor,sqlite3_conn)
                
        except Exception as e:
            print(e, '↓\nurl: '+url)
        else:
            try:
                res_url, web_sapce = self.url_split(url)
                self.write_file(url,cursor,res_url,web_sapce=web_sapce)
            except Exception as e:
                print(e)
        finally:
            cursor.close()
            sqlite3_conn.close()

    def run(self):
        with open(f'{path_of_url_txt}', 'r', encoding='utf8') as f:
            try:
                self.f_to_w = open(
                    f'./{self.name_of_conf_to_writ}', 'w', encoding='utf8')
                self.f_to_w.write('@global\n\topen_timeout=0s')
                self.get_latest_version_of_npm_hosting()
                for url in f.readlines():
                    url = url.replace('\n', '')
                    # 验证是否是合法url
                    if not self.is_vaild_url(url):
                        continue
                    else:

                        self.thread_list.append(self.pool.submit(
                            self.import_url_to_file, self.url_encode(url)))
                
            except Exception as e:
                print(e)

        wait(self.thread_list)
        self.f_to_w.close()


if __name__ == '__main__':
    main('custom.conf').run()
