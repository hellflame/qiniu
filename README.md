# qiniu
七牛云本地调用

### 安装
```bash
    $ sudo pip install qiniumanager --upgrade
```

### 七牛云存储 Qiniu Manager

```
Usage:
  qiniu <your file> [space]		选择文件位置上传，指定空间名或使用默认空间名
  qiniu [option] <file name> [space]	对云空间中文件进行操作
  qiniu [--key|-k] <access key> <secret key>	设置密钥

  --version,-v	当前版本号
  --space,-s	修改或查看当前空间名
  --remove,-r	删除云文件
  --private,-p	返回私有文件下载链接
  --download,-d	下载文件
  --check,-c	查看文件状态
  --rename,-n	重命名
  --key,-k	修改或查看access key，secret key
  --link,-i	返回开放云空间文件下载链接
  --list,-l	文件列表
  --help,-h	帮助
  --clean,-e	清除缓存

首次使用请设置密钥对 qiniu [--key|-k] <access key> <secret key>
必要情况下请设置默认空间名
```

### 具体操作

####显示帮助信息方式
```bash
	qiniu
	qiniu -v # QiniuManager 版本以及SDK版本
```
####基本设置
i.密钥设置
```bash
	qiniu -k <access key> <secret key>	
	qiniu -k # 显示密钥对
```
![这里的AK及SK](https://static.hellflame.net/resource/5ccf929aae10fc0fb5a26a63c28e6d45)
	ii.空间设置(bucket)
```bash
	qiniu -s share # 可以省略测试域名
	qiniu -s share 7xqh1q.dl1.z0.glb.clouddn.com
	qiniu -s # 显示空间信息(bucket)
```
![space & alias](https://static.hellflame.net/resource/e506e9787b0a693da3a4d5be381b28ad)

>好吧，一直用的测试域名，对于对外开放的空间访问的话，并不需要设置这个`alias`，只需要`qiniu -s share`即可（换成自己的空间名），对于私有空间，对于我而言，这个测试域名的使用是必要的

#### 基本操作
i.文件列表
```bash
	qiniu -l # 显示当前空间(bucket)文件列表
	qiniu -l backup # 显示`backup`中的文件列表
```
ii.文件详情
```bash
	qiniu -c <filename> # 显示当前空间(bucket)中<filename>的信息(讲真这个信息炒鸡简略)
	qiniu -c <filename> <space name> # 显示<space name>这个空间(bucket)中<filename>的信息
```
iii.获取下载链接
```bash
	# 获取开放空间的有效链接
	qiniu -i <filename> # 获取当前空间(bucket)中<filename>的下载链接
	qiniu -i <filename> <space name> # 获取<space name>中<filename>的下载链接
	# 获取私有空间的有效链接(expire 3600)
	qiniu -p <filename> # 获取当前空间(bucket)中<filename>的私有下载链接,开放空间返回的链接可下载，但不会被expire限制可下载时间
	qiniu -p <filename> <space name># 获取<space name>中<filename>的私有下载链接，开放空间返回的链接可下载，但不会被expire限制可下载时间
```
> 如果不知道该空间是否为私有空间，直接用`qiniu -p `获取的链接将保证对于开放空间以及私有空间都有效，前提是能够正确设置空间的测试域名(对于作者这样的免费用户而言)
> 当然，还是知道空间的开放和私有属性比较好
![private and public](https://static.hellflame.net/resource/b74f36b5f05569fa005952e5a90561da)

iv.下载
```bash
	qiniu -d <filename> # 下载当前空间(bucket)中的<filename>
	qiniu -d <filename> <space name> # 下载<space name>空间(bucket)中的<filename>
```

> 下载的文件存储在当前目录，与空间中文件名相同
> 正常的话，应该会显示下载进度条

![progress](https://static.hellflame.net/resource/7dc3b5f8d42a49d2233d152c6779b829)
![finished](https://static.hellflame.net/resource/a51952d5e39ab3c3308fced9ed79db1a)

>不正常的话，进度条可能会不能正常显示，不过如果还好的话，最终文件还是会正常下载完毕
>如果崩溃的话，还是老老实实`wget url -O <filename>`好了

v.删除
```bash
	qiniu -r <filename> # 删除当前空间(bucket)中的<filename>
	qiniu -r <filename> <space name> # 删除<space name>空间(bucket)中的<filename>
```

> 想要吐槽的是，无论是七牛SDK的返回值规范性还是七牛服务器的返回值的规范性都不是很一致（与自己所认为的规范性不是很一致）

![confuse](https://static.hellflame.net/resource/8db93d0655185b086dde5ec2a4b8b9b6)

其实个人的做法更倾向于在成功时也返回一个json字符串，给出一个status表示操作成功，然而这里并没有。在查看服务器的返回值时，这个就更清楚了，服务器的response中，body部分的确是空的，`Content-Length: 0`，这也让我需要对这部分请求作特别的处理，比如禁用下载进度条(这是自己写的HTTP报文发送以及接受的方法中需要的)

以及SDK中在使用POST方法的大环境下，调用了少量GET方法接口，于是在生成Token的时候需要对GET的data也进行操作
![](https://static.hellflame.net/resource/053660e4f3d6751c827c2bfe62aaa38c)
于是重写添加了一个和验证POST Token差不多的Token的方式(因为token的生成是与传递的数据实体有关的)

这里也出现了`Content-Type: application/x-www-form-urlencoded`这个一般只在网页上的form表单才出现的content-type。虽然我还不是很清楚这个content-type在这里出现的意义，但是应该是在某个地方处理到了模仿form表单上传数据吧，也说明这部分也许是直接调用了网页端的接口，也许这也是接口规范不一致的表现之一吧

vi.查看单个文件
```bash
	qiniu -c <filename> # 查看当前空间(bucket)中<filename>的一般属性，实际上并没有太详细的信息的样子
	qiniu -c <filename> <space name> # 查看<space name>空间(bucket)中的<filename>的一般信息
```

![qiniu -c](https://static.hellflame.net/resource/ffcf828ae54effbb8bb3e669b43db2ec)

好吧，总觉得这些信息甚至都没有这个文件被下载或者引用的次数什么的，意义看上去不是太大的样子。顺便一说，这里服务器返回的文件上传时间被'精确'了10000000倍，好吧，这里应该说至少精确了1000倍(到达毫秒级)，剩下的应该是随机值吧(自己做的静态文件服务器也有类似的处理)

vii.重命名
```bash
	qiniu -n <target file> <to file> # 将当前空间中的<target file>重命名为<to file>
	qiniu -n <target file> <to file> <space name> # 将<space name>空间中的<target file>重命名为<space name>空间中的<to file>
```

![sdk move](https://static.hellflame.net/resource/45dfd760b9d4dcf54ecd6ea81f32b8a1)
实际上重命名接口在SDK中和移动资源方法是同一个，并且支持在不同的空间之间进行移动，但是作者认为在命令行中输入这么多参数已经很烦了，也并没有需求在不同空间之间进行资源操作，于是`QiniuManager`限制了重命名只能在当前空间

![](https://static.hellflame.net/resource/aef205f6251e8e50e42f034193fe8b26)

如果需要支持在不同空间之间进行资源移动的话，在上述代码中将第二个`space`换成目标space就好了，还有能够看到的是，里面中文翻译都是叫的空间，但是英文名却叫"bucket",表示并不清楚这个翻译的来源

![](https://static.hellflame.net/resource/54fbc0df69cbb8df1296f5712ee23c09)

我是不是应该也把这个叫做不规范讷

#### Issue
1. nodename nor servname provided, or not known
如果测试域名配置如下
![hostname unknown](https://static.hellflame.net/resource/e086339b219f691db1a1052f349deadb)
可能就会报如下错误，因为这个域名无效('7ktpup.com1.z0.glb.clouddn.com')
![hostname not valid](https://static.hellflame.net/resource/748ee73149aa605434221204397b39df)
可能的原因是七牛云没有解析所有的测试域名，处理方法就是在配置域名时，需要将测试域名配置为那个可用的域名,如`qiniu -s whatever whatever.qiniudn.com`，但是实际上并不知道七牛云的域名如何管理的，所以要知道哪个域名是可用的话，在`内容管理`界面查看外链，就知道至少哪一个域名是可用的了



### 历史版本

+   v0.9.12 修复无法上传中文文件名文件的错误
+   v0.9.13 下载输出优化
+   v0.9.14 私有空间文件下载
+   v0.9.15 下载前预判以及输出微调
+   v0.9.16 消除参数获取失败后的报错方式
+   v0.9.17 未安装curl下载失败
+   v1.1.0  基本从底层重写了一遍，尽量直接调用了API链接
+   v1.1.1  urllib.quote