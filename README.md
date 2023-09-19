# picture-bed-use-freecdn

freecdn-js能提高网站稳定性，如果其中一个链接不可用则启用另一个链接。cdn.jsdelivr.net不太稳定需要备用链接，所以用到了freecdn-js。但是freecdn-js对本身就在服务器端的文件不太友好（因为需要`sha256`），例如我把github作为图床而上传的图片，故写了一个python脚本处理hash和生成freecdn-js所需要的配置文件。

需要使用安装[freecdn-js](https://github.com/EtherDream/freecdn)。本脚本为python脚本（因为不会写gulp），需要安装python。报错或许需要1.25.11版本的`urllib3`。

经过验证，nodejs16.10.0能运行freecdn-js，如果有需要安装旧版本nodejs请使用nvm工具安装。


## 使用方法

只需要把放在github的图片url（以.xxx结尾，如.png、.css、.js）放在`urls.txt`，每行放一个url，并在同一个文件夹内运行`generate_custom.conf.py`，即可生成`custom.conf`。

或者你也用hexo博客，那么可以使用`generate_pic.conf_without_urls.txt.py`根据`.md`（博客写作使用markdown）文件直接生成`pic.conf`，无需手动把url添加到`urls.txt`。`.md`放在`source\_posts`，或根据需要自行修改。`.py`文件中的正则表达需要根据自己的需求更改。如果你也使用[hexo-volantis](https://github.com/volantis-x/community)可以试着直接运行。

如果你像我一样把文件（图片和某些js）放在github，需要在`.py`文件头部设置`user`变量为你的github id（用于定位你的github图床）。例如我就是xingpingcn

在`.py`文件头部可以设置是否使用代理（v2ray），需要自行设置。

`urls.txt`的格式为http(s)://website/user/repo/xxx

其中website可以是raw.githubusercontent.com或者cdn.jsdelivr.net这种免费cdn。

示例
 > https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp   
https://raw.githubusercontent.com/xingpingcn/picx-images-hosting/master/20230420/image.1anm5qwvdhnk.png

脚本未支持其他url格式和生成其他图床url。

## 脚本运行逻辑

脚本会先判断`urls.txt`（或`.md`文件）中的url是否在`custom.conf`（或`pic.conf`）中，如果已经存在则直接写入到新的`.conf`，从而节省流量和时间。

如果url不在`.conf`中，则判断本地是否存储`urls.txt`（`generate_pic.conf_without_urls.txt.py`无需`urls.txt`，脚本内自动处理）中的文件，如果没有则下载文件。如果有则计算hash并写入`.conf`。

内置了几个`类cdn.jsdelivr.net`的cdn。其中jsd.cdn.zzko.cn的GitHub地址是[这里](https://github.com/54ayao/Chinajsdelivr)

最终`.conf`会类似这样

```typescript
    @global
	    open_timeout=0
    https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
	    https://jsd.cdn.zzko.cn/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
	    https://cdn.jsdelivr.us/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
	    https://cdn.jsdelivr.ren/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
	    https://cdn.jsdelivr.net/gh/xingpingcn/picx-images-hosting@master/20230525/logo%20(2).ln5ua8psy9s.webp
	    hash=53vmPtDi0FDFXfMGWxx4vfPICcg1nY8rLgmQh7wjZow=
```
脚本会生成`.bak.conf`，可以删除。
## 和hexo配合

我的博客用的hexo，因而可以使用以下命令行生成对应文件。

```powershell
    cd f:/blog
    hexo clean && hexo g
    python ./generate_custom.conf.py
    cd f:/blog/public
    freecdn find --save
    freecdn manifest --merge ../custom.conf
    freecdn manifest --merge ../pic.conf #如果是hexo博客
    freecdn js --make
    gulp && hexo d
```