import os
import sys
from generate_custom_conf import CalcFileSha256_with_base64

cdn_list = ['https://jsd.cdn.zzko.cn/gh/', 'https://cdn.jsdelivr.us/gh/',
            'https://cdn.jsdelivr.ren/gh/', 'https://cdn.jsdelivr.net/gh/','https://raw.githubusercontent.com/']
def main():
    os.chdir(sys.path[0])  # os.chdir(sys.path[0])把当前py文件所在路径设置为当前运行路径.
    with open(os.path.join('./public', 'freecdn-manifest.txt'), 'w', encoding='utf8') as f:
        hash256 = CalcFileSha256_with_base64(
            os.path.join('./public', 'manifest-full.txt'))
        f.write('@include\n\t/manifest-full.txt\n@global\n\topen_timeout=0\n/manifest-full.txt')
        for cdn in cdn_list:
            if  not cdn  == 'https://raw.githubusercontent.com/':
                f.write(f'\n\t{cdn}xingpingcn/xingpingcn.github.io@main/manifest-full.txt')
            else:
                f.write(f'\n\t{cdn}xingpingcn/xingpingcn.github.io/main/manifest-full.txt')
        # f.write(f'''@include\n\t/manifest-full.txt\n@global\n\topen_timeout=0\n/manifest-full.txt\n\thttps://jsd.cdn.zzko.cn/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt\n\thttps://cdn.jsdelivr.us/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt\n\thttps://cdn.jsdelivr.ren/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt\n\thttps://cdn.jsdelivr.net/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt\n\thash={hash256}''')
        f.write(f'\n\thash={hash256}')
    print('manifest_file generaeted.')
if __name__ == '__main__':
    main()