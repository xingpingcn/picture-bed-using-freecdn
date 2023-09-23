<h1 align="center" style="font-weight: bold" > picture-bed-using-freecdn </h1>

---

需要环境
```yaml
urllib3: 1.25.11
nodejs:  16.10.0
freecdn: 0.3.1
```

freecdn-js能提高网站稳定性，如果其中一个cdn链接不可用则启用另一个链接。博客图床使用到的cdn.jsdelivr.net不太稳定需要备用链接，所以用到了freecdn-js。但是freecdn-js对本身就在服务器端的文件不太友好（因为需要`sha256`），例如我把github作为图床而上传的图片（图片不在本地），故写了一个python脚本处理hash和生成freecdn-js所需要的配置文件。

需要使用安装[freecdn-js](https://github.com/EtherDream/freecdn)。本脚本为python脚本（因为不会写gulp），需要安装python。若报错或许需要1.25.11版本的`urllib3`。

经过验证，nodejs16.10.0能运行freecdn-js，如果有安装旧版本nodejs的需要请使用nvm工具安装。


## 使用方法

只需要把放在github的图片的url（以.xxx结尾，如.png、.css、.js）放在`urls.txt`，每行放一个url，并在同一个文件夹内运行`generate_custom_conf.py`，即可生成`custom.conf`（可以用`freecdn manifest --merge path_to_custom.conf`合并到`freecdn-manifest.txt`），`custom.conf`由几个内置的cdn模板生成。

`url`的格式为`http(s)://cdn/user/repo@your_branch/xxx`。其中`cdn`可以是`cdn.jsdelivr.net/gh/`这种免费cdn。

`url`的格式也可以为`http(s)://raw.githubusercontent.com/user/repo/your_branch/xxx`。

`url`也可以不带有`your_branch`，或许不能生成`raw.githubusercontent.com`的cdn链接，但是能生成`类cdn.jsdelivr.net/gh/`的cdn链接。可以看到下面`.conf`的示例中最后一个`url`只生成了4个cdn链接。

示例
 > https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo (2).ln5ua8psy9s.webp
 > https://raw.githubusercontent.com/xingpingcn/picx-images-hosting/master/20230420/image.7grs1emx5ok0.png
 > https://jsd.cdn.zzko.cn/gh/xingpingcn/website.comments/app.js

<font color=#808080 >*注：脚本未支持其他url格式和生成其他图床url。*</font>

输出的最终`.conf`会类似这样。[示例](https://github.com/xingpingcn/picture-bed-using-freecdn/blob/main/pic.conf)

<details> <summary>点击查看示例</summary>

```typescript
    @global
        open_timeout=0
    https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
        https://jsd.cdn.zzko.cn/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
        https://cdn.jsdelivr.us/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
        https://cdn.jsdelivr.ren/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
        https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
        https://raw.githubusercontent.com/xingpingcn/picx-images-hosting/master/20230525/logo%20(2).ln5ua8psy9s.webp
        hash=53vmPtDi0FDFXfMGWxx4vfPICcg1nY8rLgmQh7wjZow=
    https://raw.githubusercontent.com/xingpingcn/picx-images-hosting/master/20230420/image.7grs1emx5ok0.png
        https://jsd.cdn.zzko.cn/gh/xingpingcn/picx-images-hosting@master/20230420/image.7grs1emx5ok0.png
        https://cdn.jsdelivr.us/gh/xingpingcn/picx-images-hosting@master/20230420/image.7grs1emx5ok0.png
        https://cdn.jsdelivr.ren/gh/xingpingcn/picx-images-hosting@master/20230420/image.7grs1emx5ok0.png
        https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230420/image.7grs1emx5ok0.png
        https://raw.githubusercontent.com/xingpingcn/picx-images-hosting/master/20230420/image.7grs1emx5ok0.png
        hash=D5Po8oLWNGQ5bk13Tr54ewGI6lcRU22JKIiCnwmKP0w=
    https://jsd.cdn.zzko.cn/gh/xingpingcn/website.comments/app.js
        https://jsd.cdn.zzko.cn/gh/xingpingcn/website.comments/app.js
        https://cdn.jsdelivr.us/gh/xingpingcn/website.comments/app.js
        https://cdn.jsdelivr.ren/gh/xingpingcn/website.comments/app.js
        https://cdn.jsdelivr.net/gh/xingpingcn/website.comments/app.js
        hash=xWPhZXLUcZFkPltRZW5UXuzEnLlNlkcIx55vlu5SB7M=
```
</details>
<font color=#808080 >*注：脚本会自动urlencode，将不是url元字符的字符转义以兼容freecdn-js。脚本会生成`.bak.conf`，可以删除。*</font>

或者你也用hexo博客（如果你也使用hexo博客，需要把三个`.py`文件放在博客根目录），那么可以使用`generate_pic.conf_without_urls_txt.py`根据`.md`（博客写作使用markdown）文件直接生成`pic.conf`（作用和`custom.conf`一样，可以用`--merge`合并到`freecdn-manifest.txt`），无需手动把url添加到`urls.txt`。`.md`放在`source\_posts`，或根据需要自行修改。`.py`文件中的正则表达需要根据自己的需求更改。如果你也使用[hexo-volantis](https://github.com/volantis-x/community)可以试着直接运行。脚本匹配了`![img](url)`、`{%link%}`、`{%image%}`、`headimg`四个`tag`。

如果你像我一样把文件（图片和某些js）放在github（我使用[picx.xpoet.cn](https://picx.xpoet.cn/)作为管理工具，上传图片的同时能够自动生成cdn链接），能十分方便生成cdn链接。

在`.py`文件头部可以设置是否使用代理（v2ray），需要自行设置。

`generate_external_manifest_file.py`用于生成`freecdn-manifest.txt`，`.txt`储存用于加速`manifest-full.txt`的cdn链接。详见[这里](https://github.com/EtherDream/freecdn/tree/master/examples/ext-manifest)

生成的`freecdn-manifest.txt`[示例](https://github.com/xingpingcn/picture-bed-using-freecdn/blob/main/freecdn-manifest.txt)如下

<details> <summary>点击查看</summary>

```typescript
    @include
        /manifest-full.txt
    @global
        open_timeout=0
    /manifest-full.txt
        https://jsd.cdn.zzko.cn/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://cdn.jsdelivr.us/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://cdn.jsdelivr.ren/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://cdn.jsdelivr.net/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        hash=izgWMFIdMtd29Zy7kWt3rWohTm7WQsZ9003qUATHdFo=
```

</details>



## 脚本运行逻辑

脚本会先判断`urls.txt`（或`.md`文件）中的url是否在`custom.conf`（或`pic.conf`）中，如果已经存在则直接写入到新的`.conf`，从而节省流量和时间。

如果url不在`.conf`中，则判断本地是否存储`urls.txt`（`generate_pic.conf_without_urls_txt.py`无需`urls.txt`，脚本内自动处理）中的文件，如果没有则下载文件。如果有则计算hash并写入`.conf`。

下载文件储存在`dir_for_custom_conf`文件夹中，在生成`.conf`后可以删除，下次生成`.conf`会根据`.bak.conf`查询。

内置了几个`类cdn.jsdelivr.net`的cdn。其中jsd.cdn.zzko.cn的GitHub地址是[这里](https://github.com/54ayao/Chinajsdelivr)


## 和hexo配合使用

我的博客用的hexo，因而可以使用以下命令行生成对应文件。

```powershell
    cd f:/blog
    hexo clean && hexo g
    python ./generate_custom_conf.py
    python ./generate_pic.conf_without_urls_txt.py #如果是hexo博客
    cd f:/blog/public
    freecdn find --save
    freecdn manifest --merge ../custom.conf
    freecdn manifest --merge ../pic.conf #如果是hexo博客
    freecdn js --make
    gulp && hexo d
```

如果你也使用hexo，同时也希望通过`cdn`加速`freecdn-manifest.txt`，使用以下命令行。

```powershell
    f:
    cd f:/blog
    hexo clean && hexo g
    python ./generate_custom_conf.py
    python ./generate_pic.conf_without_urls_txt.py #如果是hexo博客
    cd f:/blog/public
    freecdn find --save
    freecdn manifest --merge ../custom.conf
    freecdn manifest --merge ../pic.conf -o manifest-full.txt #用于生成外置的freecdn-manifest.txt
    python ../generate_external_manifest_file.py 
    freecdn js --make --cdn "https://jsd.cdn.zzko.cn/gh/user/repo@main/freecdn-internal/ver/freecdn-main.min.js unpkg jsdelivr elemecdn " #此命令为配置cdn链接用于加速.min.js文件，详细请查看freecdn项目的GitHub
    gulp && hexo d
```

## 感谢

* [EtherDream/freecdn](https://github.com/EtherDream/freecdn)