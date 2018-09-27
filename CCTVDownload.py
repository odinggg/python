import datetime
import os
import urllib
from urllib import parse
from urllib import request

import fire
import gevent
import requests
from lxml import etree
from dumblog import dlog

logger = dlog(__file__)

HEADERS = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.baidu.com/link?url=poccBSgMrYoFaqykvx_t6iNzDijw30eIUoq-N259rY_&wd=&eqid=fb628a9f00086d94000000035bab4bd6',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}
HEADERS2 = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'Accept': 'text/html, */*; q=0.01',
    'Referer': 'http://tv.cctv.com/lm/xwlb/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}
FLV_URL = 'http://www.flvcd.com/parse.php/?'
FLV_INDEX = 'http://www.flvcd.com/index.htm'
CCTV_URL = 'http://tv.cctv.com/lm/xwlb/day/'
CCTV_SUFFIX = '.shtml'


def get_mp4_url(cctv_url):
    flv_search = {'kw': cctv_url, 'flag': 'one', 'format': 'super'}
    flv_data = parse.urlencode(flv_search)
    url = FLV_URL + flv_data
    s = requests.Session()
    resp = s.get(url, headers=HEADERS)
    html = etree.HTML(resp.content)
    mp4s = html.xpath('//table[2]//tr[1]//td[@class="mn STYLE4"]/a')
    mp4_url = []
    for index, v in enumerate(mp4s):
        mp4_url.append(v.get('href'))
    return mp4_url


def download(url, name, filetype):
    filepath = '%s/%s.%s' % (filetype, name, filetype)
    if os.path.exists(filepath):
        logger.warn('this file had been downloaded :: %s' % filepath)
        return
    urllib.request.urlretrieve(url, '%s' % filepath)
    logger.info('download success :: %s' % filepath)


def file_name(url):
    list1 = url.split('/')
    name = list1[-1].split('.')[0]
    return list1[-4] + '-' + list1[-3] + '-' + list1[-2] + '-' + name


def mp4_job(mp4_url):
    name = file_name(url=mp4_url)
    download(url=mp4_url, name=name, filetype='mp4')


def get_cctv_url(cctv_search):
    url = CCTV_URL + cctv_search + CCTV_SUFFIX
    session = requests.Session()
    resp = session.get(url, headers=HEADERS2)
    html = etree.HTML(resp.content)
    cctv_url = html.xpath('//ul[1]/li[1]/a')[0].get('href')
    return cctv_url


def get_date_str(start, end):
    dates = []
    date_begin = datetime.datetime.strptime(start, '%Y%m%d')
    date_end = datetime.datetime.strptime(end, '%Y%m%d')
    while date_begin <= date_end:
        date_str = date_begin.strftime('%Y%m%d')
        dates.append(date_str)
        date_begin += datetime.timedelta(days=1)
    return dates


def run(start, end):
    dates = get_date_str(start=str(start), end=str(end))
    jobs = []
    with open(r'download.txt', 'w') as fileWriter:
        for d in dates:
            url1 = get_cctv_url(d)
            logger.info('下载日期：%s' % d)
            urls = get_mp4_url(url1)
            for url2 in urls:
                mp4_job(url2)
                fileWriter.write(url2)
                fileWriter.write('\n')
                jobs.append(gevent.spawn(mp4_job, url2))
    gevent.joinall(jobs, timeout=2)


if __name__ == '__main__':
    fire.Fire()
