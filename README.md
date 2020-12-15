# ComicBook

漫画爬虫、漫画下载工具，支持腾讯漫画、哔哩哔哩漫画、有妖气漫画、快看漫画、漫画柜等站点

[漫画源收录情况](https://github.com/lossme/ComicBook/projects/1)

尊重版权，请支持正版，通过本工具下载或生成的资源**禁止传播分享！禁止利用本项目进行商业活动！**

## 本项目特点

- [x] 漫画批量下载
- [x] 分目录按章节保存
- [x] 支持多个漫画源，易于扩展
- [x] 支持登录
- [x] 支持生成pdf
- [x] 支持发送到邮箱
- [x] 支持设置代理
- [x] 支持API调用 [API-README](API-README.md)

## 安装/升级步骤

### 方式一（推荐）

```sh
# 在线安装/升级
# 由于网络环境不好导致安装失败 可以搜索关键词尝试解决: github host 修改
python3 -m pip install -U git+https://github.com/lossme/ComicBook

# 查看帮助
python3 -m onepiece --help
```

### 方式二（源码安装）

```sh
# clone项目 或从这里下载最新的代码并解压 https://github.com/lossme/ComicBook/releases
git clone git@github.com:lossme/ComicBook.git
# 切换工作目录
cd ComicBook
# 安装
python3 setup.py clean --all install
# 查看帮助
python3 -m onepiece --help
```

如果在使用过程中，发现问题可以先更新代码再试下，说不定已经修复了。

Star防止走丢，欢迎大家提建议和issue，本项目持续更新。

## 常规使用

从腾讯漫画下载：

- 从URL下载漫画的最新一集: `python3 -m onepiece --url "http://ac.qq.com/Comic/ComicInfo/id/505430"`
- 下载漫画 id=505430 最新一集: `python3 -m onepiece --site=qq --comicid=505430`
- 下载所有章节: `python3 -m onepiece --site=qq --comicid=505430 --all`
- 下载第800集: `python3 -m onepiece --site=qq --comicid=505430 --chapter=800`
- 下载倒数第二集: `python3 -m onepiece --site=qq --comicid=505430 --chapter=-2`
- 下载1到5集,7集，9到10集: `python3 -m onepiece --site=qq --comicid=505430 --chapter=1-5,7,9-10`
- 拼接成长图: `python3 -m onepiece --site=qq --comicid=505430 --single-image --quality 95 --max-height 20000`
- 设置代理: `python3 -m onepiece --site=qq --comicid=505430 --proxy "socks5://127.0.0.1:1080"`
- 自定义保存目录: `python3 -m onepiece --site=qq --comicid=505430 --output MyComicBook`
- 下载单行本: `python3 -m onepiece --site=manhuagui --comicid=1128 --ext-name=单行本 --chapter=-1`
- 通过指定的URL文件列表批量下载[【文件示例】](https://github.com/lossme/ComicBook/blob/master/test/test-url-file.txt)：`python3 -m onepiece --url-file test/test-url-file.txt`
- 若不清楚或不记得comicid，可以使用名字来搜索：`python3 -m onepiece --site=qq --name=海贼`
- 推送到邮箱:
```sh
# 注意: 发送到邮箱需预先配置好信息
# 配样例参照 https://github.com/lossme/ComicBook/blob/master/config.ini.example
# 并根据实际情况调整，将配置文件保存为 config.ini
python3 -m onepiece --site=qq --comicid=505430 --pdf --mail --config config.ini
```
- 生成pdf文件:
```sh
# 生成pdf文件需要额外安装依赖，需要先执行 python3 -m pip install img2pdf 或 python3 -m pip install reportlab
python3 -m onepiece --site=qq --comicid=505430 --pdf
```
- 从其它站点下载，注意不同站点的comicid区别
```sh
# 从哔哩哔哩漫画下载:
python3 -m onepiece --site=bilibili --comicid=mc24742 --chapter=1
# 从有妖气漫画下载:
python3 -m onepiece --site=u17 --comicid=195 --chapter=1
```

### 关于登录

1. 安装selenium: `python3 -m pip install selenium`
2. 安装chrome浏览器，或其它浏览器
3. [下载chromedriver](https://chromedriver.chromium.org/downloads)，或其它浏览器的driver
4. 登录，并将cookies保存在本地（保存登录状态）
```sh
# 在弹出的浏览器上完成登录。若登录完浏览器没自动关闭，可以手动把浏览器关了
python3 -m onepiece --site=qq --comicid=505430 --chapter=-1 \
  --login \
  --driver-path="driver路径" \
  --driver-type="Chrome" \
  --cookies-path="data/cookies/qq.json"
```

### 高级批量下载

```sh
# 有些站点不一定支持，其它的通用参数也适用，可自行组合
# 下载最近更新页面的1到10页 所有漫画的最新一集
python3 -m onepiece --site=nvshens --latest-all --latest-page=1-10

# 展示支持的标签
python3 -m onepiece --site=nvshens --show-tags

# 下载标签搜索结果页面的1到10页 所有漫画的全集
python3 -m onepiece --site=nvshens --tag-all --tag=女神 --tag-page=1-10 --all
```

### 高级配置

#### 通过环境变量配置默认参数
```sh
# 可以将以下命令添加到 ~/.bashrc 或 ~/.zshrc 文件末尾
# 配置默认下载目录
export ONEPIECE_DOWNLOAD_DIR="/home/key/Downloads/MyComicBook"

# 配置默认的邮件配置文件路径
export ONEPIECE_MAIL_CONFIG_FILE="/home/key/MyConfig/config.ini"

# 配置默认的 webdriver
export ONEPIECE_DRIVER_TYPE="Chrome"
export ONEPIECE_DRIVER_PATH="/home/key/data/chromedriver_win32/chromedriver.exe"

# 配置默认的cookies存放目录
export ONEPIECE_COOKIES_DIR="/home/key/data/cookies"

# 配置默认的全局代理地址
export ONEPIECE_PROXY="socks5://127.0.0.1:1082"
# 配置腾讯漫画下载代理地址
export ONEPIECE_PROXY_QQ="socks5://127.0.0.1:1082"
# 配置其它站点下载代理地址
export ONEPIECE_PROXY_XXXX="socks5://127.0.0.1:1082"

# 配置默认的长图质量
export DEFAULT_QUALITY=95
# 配置默认的长图最大高度
export DEFAULT_MAX_HEIGHT=20000
```
