
blog_md_file_dir = './source/_posts'
blog_public_dir = './public'
blog_deploy_dir ='./.deploy_git'
#储存静态文件的GitHub repo信息
user = 'xingpingcn'
repo = 'xingpingcn.github.io'
branch = 'main'
# 如果要使用npm空间则填写，不使用则留空
npm_name_of_pic_bed = 'p-hosting-for-xp'
npm_name_of_html_package = 'html-hosting-for-xp'

is_refresh_tag = True
token = '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'


cdn_list = {
        'github': ['https://jsd.cdn.zzko.cn/gh/', 'https://cdn.jsdelivr.us/gh/',
            'https://cdn.jsdelivr.ren/gh/', 'https://cdn.jsdelivr.net/gh/'], 
        'raw': ['https://raw.githubusercontent.com/'],
        "npm": ['https://npm.onmicrosoft.cn/','https://jsd.onmicrosoft.cn/npm/','https://cdn.jsdelivr.net/npm/','https://unpkg.com/']
}

is_output_to_txt = False #输出md文件中的url到txt文件urls_in_md.txt

is_import_html_to_conf = True #导入“blog_public_dir”中的html到pic.conf
html_file_to_ignore = ['google4e035139f56cb1e9.html']

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

