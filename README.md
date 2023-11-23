<h1 align="center" style="font-weight: bold" > picture-bed-using-freecdn </h1>

---

# 亮点

* 你是否由于在博客中使用到的免费cdn不稳定而烦恼？现在只需要在`urls.txt`放入url，并运行`import_to_db_with_urls_txt.py`，之后再在博客中插入一行[freecdn-js](https://github.com/EtherDream/freecdn)提供的js代码，则能够同时加载每个备用cdn连接，哪个先加载完就用哪个，并停止未加载完的cdn。
* 如果你使用`md`编写博客，也能提取`.md`文件中的图片等`url`并生成所需文件。目前脚本适配了`![img](url)`、`{%link%}`、`{%image%}`、`headimg`四个`tag`；同时能够自定义需要匹配的`tag`。

十分建议您先查看源码中的几个`.txt`文件，看看此脚本是否适合你。

# 需要环境

```yaml
urllib3: 1.25.11
nodejs:  16.10.0
freecdn: 0.3.1
```

# 为什么编写这个脚本

freecdn-js能提高网站稳定性，如果其中一个cdn链接不可用则启用另一个链接。博客图床使用到的cdn.jsdelivr.net不太稳定需要备用链接，所以用到了freecdn-js。但是freecdn-js对本身就在服务器端的文件不太友好（因为需要`sha256`），例如我把github作为图床而上传的图片（图片不在本地），故写了一个`python`脚本处理hash和生成freecdn-js所需要的配置文件。

需要使用安装[freecdn-js](https://github.com/EtherDream/freecdn)。本脚本为`python`脚本（因为不会写js），需要安装`python`。若报错或许需要1.25.11版本的`urllib3`。

经过验证，`nodejs16.10.0`能运行freecdn-js，如果有安装旧版本nodejs的需要请使用nvm工具安装。

# 使用方法

## 根据urls.txt生成

只需要把放在github的图片的url（以.xxx结尾，如.png、.css、.js）放在`urls.txt`，每行放一个url，并在同一个文件夹内运行`import_to_db_with_urls_txt.py`，即可生成`custom.conf`（可以用`freecdn manifest --merge $path_to_custom.conf`合并到`freecdn-manifest.txt`），`custom.conf`由几个内置的cdn模板生成。

> * `url`的格式为`http(s)://cdn/user/repo@your_branch/xxx`。其中`cdn`可以是`cdn.jsdelivr.net/gh/`，`cdn.jsdelivr.net/npm/`这种免费cdn。
> * `url`的格式也可以为`http(s)://raw.githubusercontent.com/user/repo/your_branch/xxx`。
> * `url`也可以不带有`your_branch`，或许不能生成`raw.githubusercontent.com`的cdn链接，但是能生成`类cdn.jsdelivr.net/gh/`的cdn链接。可以看到下面`.conf`的示例中的`https://jsd.cdn.zzko.cn/gh/xingpingcn/website.comments/app.js`只生成了4个cdn链接。

<font color=#808080>*注：若要成功生成`raw.githubusercontent.com`请确保原始url中在`@your_branch`之前不存在`@`*</font>

`urls.txt`示例
 > <https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo> (2).ln5ua8psy9s.webp
 > <https://raw.githubusercontent.com/xingpingcn/picx-images-hosting/master/20230420/image.7grs1emx5ok0.png>
 > <https://jsd.cdn.zzko.cn/gh/xingpingcn/website.comments/app.js>

<font color=#808080>*注：脚本未支持其他url格式和生成其他图床url。*</font>

输出的最终`.conf`会类似这样[[示例]](https://github.com/xingpingcn/picture-bed-using-freecdn/blob/main/pic.conf)

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
    // 如果`is_import_html_to_conf` = `True`
    /index.html
        https://jsd.cdn.zzko.cn/gh/xingpingcn/xingpingcn.github.io@main/index.html
        https://cdn.jsdelivr.us/gh/xingpingcn/xingpingcn.github.io@main/index.html
        https://cdn.jsdelivr.ren/gh/xingpingcn/xingpingcn.github.io@main/index.html
        https://cdn.jsdelivr.net/gh/xingpingcn/xingpingcn.github.io@main/index.html
        https://raw.githubusercontent.com/xingpingcn/xingpingcn.github.io/main/index.html
        hash=98HPGpSw/VfpGXiGFurKmHAC76gR5n2R2KNTWrisOTg=
        mime=text/html

```

</details>

<font color=#808080 >*注：脚本会自动urlencode，将不是url元字符的字符转义以兼容freecdn-js。*</font>

## 根据博客内容生成

或者你也用hexo博客（如果你也使用hexo博客，需要把对应的`.py`文件放在博客根目录），那么可以使用`import_to_db_with_hexo_blog.py`根据`.md`（博客写作使用markdown）文件的内容直接生成`pic.conf`（作用和`custom.conf`一样，可以用`--merge`合并到`freecdn-manifest.txt`），无需手动把url添加到`urls.txt`。`.md`放在`source\_posts`，或根据需要自行修改。`.py`文件中的正则表达需要根据自己的需求更改。如果你也使用[hexo-volantis](https://github.com/volantis-x/community)可以试着直接运行。

脚本适配了四个`tag`，为：
* `![img](url)`
* `{%link%}`
* `{%image%}`
* `headimg`

> P.S. 如果你像我一样把文件（图片和某些js）放在github（我使用[picx.xpoet.cn](https://picx.xpoet.cn/)作为管理工具，上传图片的同时能够自动生成cdn链接），能十分方便生成cdn链接。

### config.py

* 在`config.py`文件可以设置是否使用代理（v2ray代理，默认开启），需要自行设置。

* `is_import_html_to_conf`为`True`时会把html文件也导入到`pic.conf`。

> P.S. 如果你使用windows可能有些坑，请看这篇[文章](https://www.xingpingcn.top/%E4%BD%BF%E7%94%A8freecdn-js%E6%8F%90%E9%AB%98hexo%E5%8D%9A%E5%AE%A2%E7%9A%84cdn%E7%A8%B3%E5%AE%9A%E6%80%A7.html#Windows%E7%9A%84%E5%A4%A7%E5%9D%91%EF%BC%81)

* `is_refresh_tag`为 `True`时，并运行`generate_external_manifest_file.py`，这样可以刷新博客的release`tag`从而达到即时更新cdn缓存的目的。

* `config.py`中可以设置是否启用npm空间，只要填写npm空间名字就可以，详见[教程](https://xingpingcn.top/npm%E5%9B%BE%E5%BA%8A%EF%BC%88%E4%B8%8D%E9%9C%80%E8%A6%81%E6%9C%AC%E5%9C%B0%E9%83%A8%E7%BD%B2%EF%BC%89.html)。需要添加Token。

<font color=#808080 >*注：若在没有更新repo资源的时候重复刷新tag可能会生成多个`draft` release；使用该.py文件需要上传两次博客，见[和hexo配合使用](#和hexo配合使用)的第二个示例*</font>

> Github账户中添加Token:
>1. Github任意页面中，依次点击：右上角头像 -> Settings -> Developer Settings -> Personal access tokens
>1. 点击Generate new token
>1. Notes中随便输入个名字，Select scopes中，确保repo及其子项目全部选中，然后点击Generate Token
>1. 把产生的token，一个40位的16进制字符串记住。重要：此token只显示这一次，如果没记住只能删除重建

### refresh_cdn_cache.py

> P.S. 官方进行了限制，需要用邮箱申请权限才能生效，比较麻烦（可以设置`config.py`中的`is_refresh_tag`为 `True`，并运行`generate_external_manifest_file.py`，这样可以刷新博客的release`tag`从而达到即时更新cdn缓存的目的）

在上传hexo博客后使用`refresh_cdn_cache.py`进行刷新。通过访问`purge.jsdelivr.net/resource`来刷新`cdn.jsdelivr.net/resource`缓存。

### generate_external_manifest_file.py

外部`manifest`(manifest-full.txt)详见[EtherDream/freecdn](https://github.com/EtherDream/freecdn/tree/master/examples/ext-manifest)

* `generate_external_manifest_file.py`用于生成`freecdn-manifest.txt`，此`.txt`储存用于加速`manifest-full.txt`的cdn链接。需要在`config.py`文件中填写`user`、`repo`等信息。

* `generate_external_manifest_file.py`中的`is_refresh_tag`为 `True`（config.py中设置）时能刷新博客的release`tag`从而达到即时更新cdn缓存的目的（仅刷新`freecdn-manifest.txt`中加速`manifest-full.txt`的cdn）。需要填写`user`、`token`等信息。


> P.S. cdn有缓存，如果freecdn失效请通过访问cdn的`freecdn-manifest.txt`或`manifest-full.txt`来检验是否和在`repo`中对应原文件一致。

生成的`freecdn-manifest.txt`[示例](https://github.com/xingpingcn/picture-bed-using-freecdn/blob/main/freecdn-manifest.txt)如下

<details> <summary>点击查看示例</summary>

```typescript
    @include
        /manifest-full.txt
    @global
        open_timeout=0
    /manifest-full.txt
        // `is_refresh_tag`为 `True` 时候@main变为@{tag_name}
        https://jsd.cdn.zzko.cn/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://cdn.jsdelivr.us/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://cdn.jsdelivr.ren/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://cdn.jsdelivr.net/gh/xingpingcn/xingpingcn.github.io@main/manifest-full.txt
        https://raw.githubusercontent.com/xingpingcn/xingpingcn.github.io/main/manifest-full.txt
        hash=izgWMFIdMtd29Zy7kWt3rWohTm7WQsZ9003qUATHdFo=
        
```

</details>

### 透明模式

如果需要[透明接入模式](https://github.com/EtherDream/freecdn/tree/master/docs/transparent-mode)，请看[这里](https://xingpingcn.top/%E4%BD%BF%E7%94%A8freecdn-js%E6%8F%90%E9%AB%98hexo%E5%8D%9A%E5%AE%A2%E7%9A%84cdn%E7%A8%B3%E5%AE%9A%E6%80%A7.html#%E6%8E%A5%E5%85%A5%E9%80%8F%E6%98%8E%E6%A8%A1%E5%BC%8F%E3%80%90%E5%8F%AF%E9%80%89%E3%80%91)

# 脚本运行逻辑

脚本会先判断`urls.txt`（或`.md`文件）中的url是否在数据库中（`freecdn`使用`sqlite3`，位置在`~/.freecdn/custom.db`，详见[freecdn db](https://github.com/EtherDream/freecdn/tree/master/docs/cli#import)；同时`python`也内置对应的库；不建议使用freecdn自带的`db`命令写入和读取数据库，运行速度非常低）中，如果已经存在则直接写入到新的`.conf`，从而节省流量和时间。

如果url不在数据库中，则判断本地是否存储了`urls.txt`或`.md`（`import_to_db_with_hexo_blog.py`无需`urls.txt`，脚本内自动处理）中的文件，如果没有则下载文件。如果有则计算`hash`并写入`.conf`（或`pic.conf`）。

下载文件储存在同目录的`dir_for_custom_conf`文件夹中，可以在`config.py`文件修改位置。

内置了几个`类cdn.jsdelivr.net`的cdn。其中jsd.cdn.zzko.cn的GitHub地址是[这里](https://github.com/54ayao/Chinajsdelivr)

`generate_external_manifest_file.py`中的`is_refresh_tag`为 `True`时（在`config.py`中设置），会查询当前的branch是否有release `tag`，如果没有则创建一个新的`tag`（[github API: create-a-release](https://docs.github.com/zh/rest/releases/releases?apiVersion=2022-11-28#create-a-release)），这个`tag`由当前head_commit的`sha_id`的前10位组成。如果有则删除，然后创建一个新的`tag`，freecdn-manifest.txt中的url替换成以下样式：

```
https://cdn.jsdelivr.us/gh/xingpingcn/xingpingcn.github.io@{tag}/manifest-full.txt
```

# 和hexo配合使用

我的博客用的hexo，因而可以使用以下命令行生成对应文件。

```powershell
    cd f:/blog
    hexo clean && hexo g
    python ./import_to_db_with_urls_txt.py
    python ./import_to_db_with_hexo_blog.py #如果是hexo博客
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
    cd f:/blog #博客根目录
    hexo clean && hexo g
    python ./import_to_db_with_urls_txt.py
    python ./import_to_db_with_hexo_blog.py #如果是hexo博客
    cd f:/blog/public
    freecdn find --save
    freecdn manifest --merge ../custom.conf
    freecdn manifest --merge ../pic.conf -o manifest-full.txt #用于生成外置的freecdn-manifest.txt
    freecdn js --make --cdn "https://jsd.cdn.zzko.cn/gh/user/repo@main/freecdn-internal/ver/freecdn-main.min.js unpkg jsdelivr elemecdn " #此命令为配置cdn链接用于加速.min.js文件，详细请查看freecdn项目的GitHub
    gulp && hexo d
    python ../generate_external_manifest_file.py #会在.deploy_git生成文件
    cd f:/blog/.deploy_git
    git add --all #如果“is_refresh_tag”为 “True”需要上传两次
    git commit -m "update"
    git push origin main #如果需要添加origin地址，请自行添加
    python ../refresh_cdn_cache.py
```
# 后记

可以的话记得备份`~/.freecdn/custom.db`。

# 感谢

* [EtherDream/freecdn](https://github.com/EtherDream/freecdn)
