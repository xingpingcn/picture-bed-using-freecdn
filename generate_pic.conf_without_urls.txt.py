'''
urllib3   1.25.11
nodejs    16.10.0
freecdn   0.3.1
requests
'''

import re
import sys
import os
from concurrent.futures import ThreadPoolExecutor, wait
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
dir_for_custom_conf = 'dir_for_custom_conf'  # 储存下载文件的文件夹名称
blog_md_file_dir = './source/_posts'  #md文件位置

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
    return urllib.parse.quote(url,safe='/()@:?.#%')
def download_file_return_hash(line: str, headers=headers):
    res_url = f'{user}/'+line.split(f'/{user}/')[-1]
    path_url = res_url.replace('/', '')

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


def write_file(bak_file, line: str, file_to_w, cdn_list=cdn_list):
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

def is_vaild_url(url):
    if re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', url):
        return True
    else:
        print('非法url！如果是urls.txt文件结尾或开头的空白符请忽略这条警告。')
        print(url)
        return False


def get_urls_in_md_file_and_generate(md_file: str, re_obj_list, re_obj_for_gallery_tag, re_obj_for_pic_tag,bak_file):
    for re_obj in re_obj_list:
        re_res_link_tag = re_obj.findall(md_file) #读取文件中的url
        for res_url in re_res_link_tag:
            res_url = res_url.replace('\n', '')
            if is_vaild_url(res_url) and res_url not in url_list:
                res_url =url_encode(res_url)
                url_list.append(res_url)
                threading_list.append(pool_for_write_file.submit(write_file,bak_file, res_url,
                                file_to_w, cdn_list=cdn_list)) 
    re_res_gallery_tag = re_obj_for_gallery_tag.findall(md_file) #读取文件中的url
    for res in re_res_gallery_tag:
        re_res_pic_tag = re_obj_for_pic_tag.findall(res)
        for res_url in re_res_pic_tag:
            res_url = res_url.replace('\n', '')
            res_url =url_encode(res_url)
            if is_vaild_url(res_url) and  res_url not in url_list:
                url_list.append(res_url)
                threading_list.append(pool_for_write_file.submit(write_file,bak_file, res_url,
                                file_to_w, cdn_list=cdn_list)) 
    
        


re_obj_for_link_tag = re.compile(r'\{%\s*link\s*.*::.*?::(.*?)\s*\%\}')
re_obj_for_image_tag = re.compile(r'\{%\s*image\s*(https://[^:]*).*\s*\%\}')
re_obj_for_headimg_tag = re.compile(r'headimg:\s*(.*)')
re_obj_for_gallery_tag = re.compile(r'\{\s*%\s*gallery([\s\S]*?)endgallery\s*%\s*\}')
re_obj_for_pic_tag = re.compile(r'!.*\((.*)\)')
url_list = []
threading_list = []
try:
    os.remove('./pic.bak.conf')
except:
    pass
try:
    os.rename('./pic.conf', './pic.bak.conf')
except:
    pass
lock = threading.Lock()
pool = ThreadPoolExecutor(16)
pool_for_write_file = ThreadPoolExecutor(16)
if not os.path.exists(f'{dir_for_custom_conf}'):
    os.makedirs(f'{dir_for_custom_conf}')
with open('./pic.conf', 'w', encoding='utf8') as file_to_w:
    file_to_w.write('@global\n\topen_timeout=0\n')  # 通用文件
    bak_file = None
    if os.path.isfile('./pic.bak.conf'):
        # 备份文件储存上一个custom.conf的信息，如果存在hash就不下载
        with open('./pic.bak.conf', 'r',encoding='utf8') as custom_bak_conf:
            bak_file = custom_bak_conf.read()

    for filename in os.listdir(f'{blog_md_file_dir}'): #读取每个md文件
        if re.match(r'.*\.md', filename):
            with open(os.path.join(f'{blog_md_file_dir}', filename), 'r',encoding='utf8') as f:
                md_file = f.read()
        pool.submit(get_urls_in_md_file_and_generate,md_file, [re_obj_for_link_tag, re_obj_for_image_tag,re_obj_for_headimg_tag],
                            re_obj_for_gallery_tag, re_obj_for_pic_tag,bak_file) #读取md文件后写入custom.conf

    pool.shutdown()
    wait(threading_list)
print('done!')
