import argparse
import os
import logging

from .comicbook import ComicBook
from .crawlerbase import CrawlerBase
from .utils import (
    parser_chapter_str,
    ensure_file_dir_exists
)
from .session import SessionMgr
from .worker import WorkerPoolMgr
from .utils.mail import Mail
from . import VERSION

logger = logging.getLogger(__name__)
HERE = os.path.abspath(os.path.dirname(__file__))

DEFAULT_DOWNLOAD_DIR = os.environ.get('ONEPIECE_DOWNLOAD_DIR') or 'download'
DEFAULT_MAIL_CONFIG_FILE = os.environ.get('ONEPIECE_MAIL_CONFIG_FILE') or ''
DEFAULT_DRIVER_TYPE = os.environ.get('ONEPIECE_DRIVER_TYPE') or 'Chrome'
DEFAULT_DRIVER_PATH = os.environ.get('ONEPIECE_DRIVER_PATH') or ''
DEFAULT_COOKIES_DIR = os.environ.get('ONEPIECE_COOKIES_DIR') or ''
DEFAULT_SESSION_DIR = os.environ.get('ONEPIECE_SESSION_DIR') or ''
DEFAULT_PROXY = os.environ.get('ONEPIECE_PROXY') or ''
DEFAULT_QUALITY = int(os.environ.get('ONEPIECE_QUALITY', 95))
DEFAULT_MAX_HEIGHT = int(os.environ.get('DEFAULT_MAX_HEIGHT', 20000))


def parse_args():
    """
    根据腾讯漫画id下载图片,默认下载海贼王最新一集。

    下载海贼王最新一集:
    python3 onepiece.py

    下载漫画 id=505430 最新一集:
    python3 onepiece.py -id 505430

    下载漫画 id=505430 所有章节:
    python3 onepiece.py -id 505430 -m all

    下载漫画 id=505430 第800集:
    python3 onepiece.py -id 505430 -c 800

    下载漫画 id=505430 倒数第二集:
    python3 onepiece.py -id 505430 -c -2

    下载漫画 id=505430 1到5集,7集，9到10集:
    python3 onepiece.py -id 505430 -i 1-5,7,9-10
    """

    parser = argparse.ArgumentParser(prog="onepiece")

    parser.add_argument('-id', '--comicid', type=str,
                        help="漫画id，如海贼王: 505430 (http://ac.qq.com/Comic/ComicInfo/id/505430)")
    parser.add_argument('--url', type=str,
                        help="漫画id，如海贼王: http://ac.qq.com/Comic/ComicInfo/id/505430")
    parser.add_argument('--url-file', type=str, help="漫画URL列表")

    parser.add_argument('--ext-name', type=str, help="如：番外篇、单行本等。具体得看站点支持哪些")

    parser.add_argument('--name', type=str, help="漫画名")

    parser.add_argument('-c', '--chapter', type=str, default="-1",
                        help="要下载的章节, 默认下载最新章节。如 -c 666 或者 -c 1-5,7,9-10")

    parser.add_argument('--worker', type=int, default=4, help="线程池数，默认开启4个线程池")

    parser.add_argument('--all', action='store_true',
                        help="是否下载该漫画的所有章节, 如 --all")

    parser.add_argument('--pdf', action='store_true',
                        help="是否生成pdf文件, 如 --pdf")
    parser.add_argument('--single-image', action='store_true',
                        help="是否拼接成一张图片, 如 --single-image")
    parser.add_argument('--quality', type=int, default=DEFAULT_QUALITY, help="生成长图的图片质量，最高质量100")
    parser.add_argument('--max-height', type=int, default=DEFAULT_MAX_HEIGHT, help="长图最大高度，最大高度65500")

    parser.add_argument('--login', action='store_true',
                        help="是否登录账号，如 --login")

    parser.add_argument('--mail', action='store_true',
                        help="是否发送pdf文件到邮箱, 如 --mail。需要预先配置邮件信息。\
                        可以参照config.ini.example文件，创建并修改config.ini文件")

    parser.add_argument('--receivers', type=str, help="邮件接收列表，多个以逗号隔开")
    parser.add_argument('--zip', action='store_true',
                        help="打包生成zip文件")

    parser.add_argument('--config', default=DEFAULT_MAIL_CONFIG_FILE, help="邮件配置文件路径")

    parser.add_argument('-o', '--output', type=str, default=DEFAULT_DOWNLOAD_DIR,
                        help="文件保存路径，默认保存在当前路径下的download文件夹")

    s = ' '.join(['%s(%s)' % (crawler.SITE, crawler.SOURCE_NAME) for crawler in ComicBook.CRAWLER_CLS_MAP.values()])
    site_help_msg = "数据源网站：支持 %s" % s

    parser.add_argument('-s', '--site', type=str, choices=ComicBook.CRAWLER_CLS_MAP.keys(),
                        help=site_help_msg)

    parser.add_argument('--verify', action='store_true',
                        help="verify")

    parser.add_argument('--driver-path', type=str, help="selenium driver", default=DEFAULT_DRIVER_PATH)

    parser.add_argument('--driver-type', type=str,
                        choices=CrawlerBase.SUPPORT_DRIVER_TYPE,
                        default=DEFAULT_DRIVER_TYPE,
                        help="支持的浏览器: {}. 默认为 {}".format(
                            ",".join(sorted(CrawlerBase.SUPPORT_DRIVER_TYPE)),
                            DEFAULT_DRIVER_TYPE)
                        )

    parser.add_argument('--session-path', type=str, help="读取或保存上次使用的session路径")
    parser.add_argument('--cookies-path', type=str, help="读取或保存上次使用的cookies路径")

    parser.add_argument('--latest-all', action='store_true', help="下载最近更新里的所有漫画")
    parser.add_argument('--latest-page', type=str, help="最近更新的页数，如1-10，默认第1页")

    parser.add_argument('--show-tags', action='store_true', help="展示当前支持的标签")
    parser.add_argument('--tag-all', action='store_true', help="下载标签里的所有漫画")
    parser.add_argument('--tag', type=str, help="标签id")
    parser.add_argument('--tag-page', type=str, help="标签页数，如1-10，默认第1页")

    parser.add_argument('--proxy', type=str,
                        help='设置代理，如 --proxy "socks5://user:pass@host:port"')

    parser.add_argument('-V', '--version', action='version', version=VERSION)
    parser.add_argument('--debug', action='store_true', help="debug")

    args = parser.parse_args()
    return args


def init_logger(level=None):
    level = level or logging.INFO
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(lineno)s [%(levelname)s] %(message)s",
        datefmt='%Y/%m/%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def download_main(comicbook, output_dir, ext_name=None, chapters=None,
                  is_download_all=None, is_gen_pdf=None, is_gen_zip=None,
                  is_single_image=None, quality=None, max_height=None, mail=None, receivers=None, is_send_mail=None):
    is_gen_pdf = is_gen_pdf or mail
    chapter_str = chapters or '-1'
    chapter_number_list = parser_chapter_str(chapter_str=chapter_str,
                                             last_chapter_number=comicbook.get_last_chapter_number(ext_name),
                                             is_all=is_download_all)
    for chapter_number in chapter_number_list:
        try:
            chapter = comicbook.Chapter(chapter_number, ext_name=ext_name)
            logger.info("正在下载 【{}】 {} 【{}】".format(
                comicbook.name, chapter.chapter_number, chapter.title))

            chapter_dir = chapter.save(output_dir=output_dir)
            logger.info("下载成功 %s", chapter_dir)
            if is_single_image:
                img_path = chapter.save_as_single_image(output_dir=output_dir, quality=quality, max_height=max_height)
                logger.info("生成长图 %s", img_path)
            if is_gen_pdf:
                pdf_path = chapter.save_as_pdf(output_dir=output_dir)
                logger.info("生成pdf文件 %s", pdf_path)

            if is_send_mail:
                mail.send(subject=os.path.basename(pdf_path),
                          content=None,
                          file_list=[pdf_path, ],
                          receivers=receivers)
            if is_gen_zip:
                zip_file_path = chapter.save_as_zip(output_dir=output_dir)
                logger.info("生成zip文件 %s", zip_file_path)
        except Exception:
            logger.exception('download comicbook error. site=%s comicid=%s chapter_number=%s',
                             comicbook.crawler.SITE, comicbook.crawler.comicid, chapter_number)


def download_latest_all(page_str, **kwargs):
    comicbook = kwargs.pop('comicbook')
    page_str = page_str or '1'
    for page in parser_chapter_str(page_str):
        for citem in comicbook.latest(page=page):
            next_comicbook = ComicBook(site=comicbook.crawler.SITE, comicid=citem.comicid)
            next_comicbook.start_crawler()
            echo_comicbook_desc(comicbook=next_comicbook, ext_name=kwargs.get('ext_name'))
            download_main(comicbook=next_comicbook, **kwargs)


def download_tag_all(tag, page_str, **kwargs):
    comicbook = kwargs.pop('comicbook')
    page_str = page_str or '1'
    for page in parser_chapter_str(page_str):
        for citem in comicbook.get_tag_result(tag=tag, page=page):
            next_comicbook = ComicBook(site=comicbook.crawler.SITE, comicid=citem.comicid)
            next_comicbook.start_crawler()
            echo_comicbook_desc(comicbook=next_comicbook, ext_name=kwargs.get('ext_name'))
            download_main(comicbook=next_comicbook, **kwargs)


def download_url_list(url_file, **kwargs):
    comicbook = kwargs.pop('comicbook')
    with open(url_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            url = line
            site = ComicBook.get_site_by_url(url=url)
            comicid = ComicBook.get_comicid_by_url(site=site, url=url)
            if not site or not comicid:
                logger.info('Unknown url. url=%s', url)
                continue
            comicbook = ComicBook(site=site, comicid=comicid)
            comicbook.start_crawler()
            echo_comicbook_desc(comicbook=comicbook, ext_name=kwargs.get('ext_name'))
            download_main(comicbook=comicbook, **kwargs)


def show_tags(comicbook):
    msg_list = []
    for t1 in comicbook.get_tags():
        category = t1['category']
        t1_msg_list = []
        for t2 in t1['tags']:
            msg = '{name}={tag}'.format(name=t2['name'], tag=t2['tag'])
            t1_msg_list.append(msg)
        msg = '{}:\n{}'.format(category, '\t'.join(t1_msg_list))
        msg_list.append(msg)
    logger.info('支持的标签\n%s', '\n'.join(msg_list))


def echo_comicbook_desc(comicbook, ext_name=None):
    name = "{} {}".format(comicbook.name, ext_name) if ext_name else comicbook.name
    msg = ("{source_name} 【{name}】 更新至: {last_chapter_number:>03} "
           "【{last_chapter_title}】 数据来源: {source_url}").format(
        source_name=comicbook.source_name,
        name=name,
        last_chapter_number=comicbook.get_last_chapter_number(ext_name),
        last_chapter_title=comicbook.get_last_chapter_title(ext_name),
        source_url=comicbook.source_url)
    logger.info(msg)


def main():
    args = parse_args()

    if args.url:
        site = ComicBook.get_site_by_url(args.url)
        if not site:
            raise RuntimeError('Unknown url. url=%s' % args.url)
        comicid = ComicBook.get_comicid_by_url(site=site, url=args.url)
    else:
        site = args.site or 'qq'
        comicid = args.comicid

    session_path = args.session_path
    if not session_path and DEFAULT_SESSION_DIR:
        session_path = os.path.join(DEFAULT_SESSION_DIR, f'{site}.pickle')
    cookies_path = args.cookies_path
    if not cookies_path and DEFAULT_COOKIES_DIR:
        cookies_path = os.path.join(DEFAULT_COOKIES_DIR, f'{site}.json')

    loglevel = logging.DEBUG if args.debug else logging.INFO
    init_logger(level=loglevel)
    comicbook = ComicBook(site=site, comicid=comicid)
    # 设置代理
    proxy = args.proxy or os.environ.get('ONEPIECE_PROXY_{}'.format(site.upper())) or DEFAULT_PROXY
    if proxy:
        logger.info('set proxy. %s', proxy)
        SessionMgr.set_proxy(site=site, proxy=proxy)
    if args.verify:
        SessionMgr.set_verify(site=site, verify=True)

    WorkerPoolMgr.set_worker(worker=args.worker)
    CrawlerBase.DRIVER_PATH = args.driver_path
    CrawlerBase.DRIVER_TYPE = args.driver_type

    # 加载 session
    if session_path and os.path.exists(session_path):
        SessionMgr.load_session(site=site, path=session_path)
        logger.info('load session success. %s', session_path)

    # 加载cookies
    if cookies_path and os.path.exists(cookies_path):
        SessionMgr.load_cookies(site=site, path=cookies_path)
        logger.info('load cookies success. %s', cookies_path)

    if args.login:
        comicbook.crawler.login()

    if args.show_tags:
        show_tags(comicbook=comicbook)
        exit(0)

    if args.name:
        result = comicbook.search(name=args.name, limit=10)
        msg_list = []
        for item in result:
            msg_list.append("\ncomicid={}\t{}\tsource_url={}".format(
                item.comicid, item.name, item.source_url)
            )
        logger.info('\n%s', 'n'.join(msg_list))
        exit(0)

    if args.mail:
        is_send_mail = True
        mail = Mail.init(args.config)
    else:
        is_send_mail = False
        mail = None

    download_main_kwargs = dict(
        comicbook=comicbook,
        output_dir=args.output,
        chapters=args.chapter,
        is_download_all=args.all,
        is_gen_pdf=args.pdf,
        is_gen_zip=args.zip,
        is_single_image=args.single_image,
        quality=args.quality,
        max_height=args.max_height,
        mail=mail,
        ext_name=args.ext_name,
        is_send_mail=is_send_mail,
        receivers=args.receivers)

    if args.url_file:
        download_url_list(url_file=args.url_file, **download_main_kwargs)
    if args.latest_all:
        download_latest_all(page_str=args.latest_page, **download_main_kwargs)
    elif args.tag_all:
        download_tag_all(tag=args.tag, page_str=args.tag_page, **download_main_kwargs)
    else:
        logger.info("正在获取最新数据")
        comicbook.start_crawler()
        echo_comicbook_desc(comicbook=comicbook, ext_name=args.ext_name)
        download_main(**download_main_kwargs)

    # 保存 session
    if session_path:
        ensure_file_dir_exists(session_path)
        SessionMgr.export_session(site=site, path=session_path)
        logger.info("session saved. path={}".format(session_path))

    # 保存 cookies
    if cookies_path:
        ensure_file_dir_exists(cookies_path)
        SessionMgr.export_cookies(site=site, path=cookies_path)
        logger.info("cookies saved. path={}".format(cookies_path))


if __name__ == '__main__':
    main()
