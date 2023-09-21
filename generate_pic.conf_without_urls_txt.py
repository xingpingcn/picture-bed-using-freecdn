'''
urllib3   1.25.11
nodejs    16.10.0
freecdn   0.3.1
requests
'''
from generate_custom_conf import url_encode, write_file
# 写到后面发现把多线程写成class会方便很多，但是快写完了就懒得改了，，，，

import re
import sys
import os
from concurrent.futures import ThreadPoolExecutor, wait
import threading
cdn_list = ['https://jsd.cdn.zzko.cn/gh/', 'https://cdn.jsdelivr.us/gh/',
            'https://cdn.jsdelivr.ren/gh/', 'https://cdn.jsdelivr.net/gh/', 'https://raw.githubusercontent.com/']

os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.

is_use_proxy = True
proxies_dict = {'http': 'socks5://127.0.0.1:10808',
                        'https': 'socks5://127.0.0.1:10808'}
dir_for_custom_conf = 'dir_for_custom_conf'  # 储存下载文件的文件夹名称
blog_md_file_dir = './source/_posts'  # md文件位置

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Sec-Ch-Ua-Platform': "Windows",
    'Cache-Control': 'no-cache',
}


def is_vaild_url(url):
    '''
    判断是否合法url
    '''
    if re.match(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', url):
        return True
    else:
        print('非法url！如果是urls.txt文件结尾或开头的空白符请忽略这条警告。')
        print(f'url为：{url}')
        return False


def get_urls_in_md_file_and_generate(md_file: str, re_obj_list, bak_file, url_list, pool_for_write_file, threading_list, file_to_w, lock):
    for re_obj in re_obj_list:
        re_res_link_tag = re_obj.findall(md_file)  # 读取文件中的url
        for res_url in re_res_link_tag:
            res_url = res_url.replace('\n', '')
            if is_vaild_url(res_url) and res_url not in url_list:
                res_url = url_encode(res_url)
                with lock:
                    url_list.append(res_url)
                threading_list.append(pool_for_write_file.submit(write_file, bak_file, res_url,
                                                                 file_to_w, lock, cdn_list=cdn_list))


def main():
    re_obj_for_link_tag = re.compile(
        r'\{\s*%\s*link\s*.*::.*?::(.*?)\s*%\s*\}')
    re_obj_for_image_tag = re.compile(
        r'\{\s*%\s*image\s*(https://[^:]*).*\s*%\s*\}')
    re_obj_for_headimg_tag = re.compile(r'headimg:\s*(.*)\s*')
    re_obj_for_pic_tag = re.compile(r'!\[.*?\].*?\((.*)\)')
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
        file_to_w.write('@global\n\topen_timeout=0')  # 通用文件
        bak_file = None
        if os.path.isfile('./pic.bak.conf'):
            # 备份文件储存上一个custom.conf的信息，如果存在hash就不下载
            with open('./pic.bak.conf', 'r', encoding='utf8') as custom_bak_conf:
                bak_file = custom_bak_conf.read()

        for filename in os.listdir(f'{blog_md_file_dir}'):  # 读取每个md文件
            if re.match(r'.*\.md', filename):
                with open(os.path.join(f'{blog_md_file_dir}', filename), 'r', encoding='utf8') as f:
                    md_file = f.read()
            pool.submit(get_urls_in_md_file_and_generate, md_file, [re_obj_for_link_tag, re_obj_for_image_tag, re_obj_for_headimg_tag, re_obj_for_pic_tag],
                        bak_file, url_list, pool_for_write_file, threading_list, file_to_w, lock)  # 读取md文件后写入custom.conf

        pool.shutdown()
        wait(threading_list)
    print('pic.conf generated.')


if __name__ == '__main__':
    main()
