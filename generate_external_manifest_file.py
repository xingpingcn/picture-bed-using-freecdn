import os
import sys,base64,hashlib,requests

from config import *
os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.
'''
从freecdn-manifest.txt中生成manifest-full.txt和用于引入外部manifest的freecdn-manifest.txt。需要填写user、token等信息。

is_refresh_tag = True 会刷新tag，此tag用于即时更新cdn缓存（间接）。需要填写user、token（personal access token）等信息。
'''



headers = {
   "Accept" : "application/vnd.github+json",
   "Authorization": f"Bearer {token}",
   "X-GitHub-Api-Version": "2022-11-28"
}

def try_func(func):
   def wrapper():
         try:
            return func()
         except Exception :
            print('[error] check your network or uesr, repo and token')
            raise
   return wrapper
@try_func
def get_release_id():

   r = requests.get(f'https://api.github.com/repos/{user}/{repo}/releases/latest',headers=headers,proxies=proxies_dict)
   json = r.json()
   if r.status_code == 200:
      id = json["id"]
      print(f'[info] latest release id: {id}.')
      return id, json["tag_name"]
   else:
        if json["message"] == "Not Found":
            print("[warning] status_code: "+str(r.status_code))
            print('[info] would get 404 status_code if there were no release. or check your network.')
            return None, None
        else:
            print('[error] '+r.status_code)
@try_func
def get_branch_sha():
  
   r = requests.get(f'https://api.github.com/repos/{user}/{repo}/branches/{branch}',headers=headers,proxies=proxies_dict)
   json = r.json()
   return json['commit']['sha'][0:10]

# 取当前head commit的sha-id的前10位作为tag和release的名称
branch_sha = get_branch_sha()
data_of_new_release= {
   "tag_name":f"{branch_sha}",
   "target_commitish":f"{branch}",
   "name":f"{branch_sha}",
   "body":"update blog",
   "draft": False
}
def post_new_release():
   release_id,tag_name = get_release_id()
   if  release_id :
        #delete release
        r1 = requests.delete(f'https://api.github.com/repos/{user}/{repo}/releases/{release_id}',headers=headers,proxies=proxies_dict)
        if r1.status_code == 204 :
            print('[success] old release deleted.')
        else:
            print('[error] '+r1.content)
        r2 = requests.delete(f'https://api.github.com/repos/{user}/{repo}/git/refs/tags/{tag_name}',headers=headers,proxies=proxies_dict)
        if r1.status_code == 204 :
            print('[success] old tag deleted.')
        else:
            print('[error] '+r2.content)
   #create a new one
   r = requests.post(f'https://api.github.com/repos/{user}/{repo}/releases',headers=headers,json=data_of_new_release,proxies=proxies_dict)
   if r.status_code == 201:
      print('[success] new release created.')
   elif r.status_code == 404:
      print('[error] Not Found if the discussion category name is invalid.')
      print(r.json())
   elif r.status_code == 422:
      print('[error] Validation failed, or the endpoint has been spammed.')
      print(r.json())
   else:
      print('[error] status_code: '+str(r.status_code)+'. when post a new release.')
def CalcFileSha256_with_base64(filname):
    ''' calculate file sha256 '''
    with open(filname, "rb") as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        hash_value = sha256obj.digest()
        return base64.b64encode(hash_value).decode()

def main():
    os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.
    with open(os.path.join(f'{blog_deploy_dir}/{path_of_static_resoure_relative_to_root_of_repo}', 'freecdn-manifest.txt'), 'w', encoding='utf8') as f:
        hash256 = CalcFileSha256_with_base64(
            os.path.join(f'{blog_deploy_dir}/{path_of_static_resoure_relative_to_root_of_repo}', 'manifest-full.txt'))
        f.write('/manifest-full.txt')
        if is_refresh_tag:
            post_new_release()
        for k,v in cdn_list.items():
            for cdn in v:
                if  k  == 'github':
                    if is_refresh_tag:
                        f.write(f'\n\t{cdn}{user}/{repo}@{branch_sha}/{path_of_static_resoure_relative_to_root_of_repo}manifest-full.txt')
                    else:
                        f.write(f'\n\t{cdn}{user}/{repo}@{branch}/{path_of_static_resoure_relative_to_root_of_repo}manifest-full.txt')
                elif k == 'raw':
                    f.write(f'\n\t{cdn}{user}/{repo}/{branch}/{path_of_static_resoure_relative_to_root_of_repo}manifest-full.txt')
        f.write(f'\n\thash={hash256}')
        f.write('\n@include\n\t/manifest-full.txt\n@global\n\topen_timeout=0s')
    print('[success] manifest_file generaeted.')
if __name__ == '__main__':
    main()