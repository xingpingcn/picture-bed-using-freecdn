from import_to_db_with_urls_txt import *
import re,os
os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.

class main2(main):
    def __init__(self,name_of_conf_to_write) -> None:
        super().__init__(name_of_conf_to_write)
        self.pool_for_write_db = ThreadPoolExecutor(32)
        self.get_latest_version_of_npm_hosting()

    def get_urls_in_md_file_and_generate(self,md_file: str, re_obj_list:list):
        for re_obj in re_obj_list:
            re_res_link_tag = re_obj.findall(md_file)  # 读取文件中的url
            for res_url in re_res_link_tag:
                res_url = res_url.replace('\n', '')
                res_url = self.url_encode(res_url)
                if self.is_vaild_url(res_url, re_obj) and res_url not in self.url_list:
                    
                    with self.lock:
                        self.url_list.append(res_url)
                    self.thread_list.append(self.pool_for_write_db.submit(self.import_url_to_file,res_url))
    def import_html_to_file(self,filename):
        try:
            filename_encode = self.url_encode(filename)
            url = '/'+filename_encode
            
            hash256 = self.CalcFileSha256_with_base64(os.path.join(f'{blog_public_dir}',filename))
            
        except Exception as e:
            print(e, '↓\nurl: '+url)
        else:
            try:
                res_url = f'{user}/{repo}@{branch}/{path_of_static_resoure_relative_to_root_of_repo}{filename_encode}'
                self.write_file(url,res_url=res_url,hash256=hash256)
            except Exception as e:
                print(e, '↓\n[error] in writing file - url: '+url)
    
    def run(self):
        re_obj_for_link_tag = re.compile(
        r'\{\s*%\s*link\s*.*::.*?::(.*?)\s*%\s*\}')
        re_obj_for_image_tag = re.compile(
            r'\{\s*%\s*image\s*(https://[^:]*).*\s*%\s*\}')
        re_obj_for_headimg_tag = re.compile(r'headimg:\s*(.*)\s*')
        re_obj_for_pic_tag = re.compile(r'!\[.*?\].*?\((.*)\)')
        self.url_list = []
        self.f_to_w = open(f'./{self.name_of_conf_to_writ}','w',encoding='utf8')
        self.f_to_w.write('@global\n\topen_timeout=0')

        for filename in os.listdir(f'{blog_md_file_dir}'):  # 读取每个md文件
            if re.match(r'.*\.md', filename):
                with open(os.path.join(f'{blog_md_file_dir}', filename), 'r', encoding='utf8') as f:
                    md_file = f.read()
                self.pool.submit(self.get_urls_in_md_file_and_generate, md_file, [re_obj_for_link_tag, re_obj_for_image_tag, re_obj_for_headimg_tag, re_obj_for_pic_tag])
        if is_import_html_to_conf:
            for filename in os.listdir(f'{blog_public_dir}'):
                if re.match(r'.*\.html', filename):
                    if not filename in html_file_to_ignore:
                        self.pool.submit(self.import_html_to_file,filename)
        self.pool.shutdown()
        wait(self.thread_list)
        if is_output_to_txt:
            with open('./urls_in_md.txt','w',encoding='utf8') as f_to_w:
                for url in self.url_list:
                    f_to_w.write(url+'\n')
        self.f_to_w.close()
if __name__ == '__main__':
    main2('pic.conf').run()