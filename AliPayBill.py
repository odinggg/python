# -*- coding:utf-8 -*-
'''
尝试登录支付宝
并获取账单记录

通过 seleium 登录支付宝，
获取 cookies
'''

import datetime
import os
import random
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

# 登录 url

Login_Url = 'https://auth.alipay.com/login/index.htm?goto=https%3A%2F%2Fwww.alipay.com%2F'
# 账单 url
Bill_Url = 'https://consumeprod.alipay.com/record/standard.htm'

# 登录用户名和密码
USERNMAE = ''
PASSWD = ''

# 自定义 headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Referer': 'https://consumeprod.alipay.com/record/advanced.htm',
    'Host': 'consumeprod.alipay.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive'
}


def date_end(date_1=datetime.datetime.now()):
    year = str(date_1.year)
    month = str(date_1.month)
    day = str(date_1.day)
    if (date_1.month / 10) < 1:
        month = '0' + str(date_1.month)
    if (date_1.day / 10) < 1:
        day = '0' + str(date_1.day)
    return year + "." + month + "." + day


class Alipay_Bill_Info(object):
    '''支付宝账单信息'''

    def __init__(self, headers, user, passwd):
        '''
        类的初始化

        headers：请求头
        cookies: 持久化访问
        info_list: 存储账单信息的列表
        '''
        self.headers = headers
        # 初始化用户名和密码
        self.user = user
        self.passwd = passwd
        # 利用 requests 库构造持久化请求
        self.session = requests.Session()
        # 将请求头添加到缓存之中
        self.session.headers = self.headers
        # 初始化存储列表
        self.info_list = []

    def wait_input(self, ele, str):
        '''减慢账号密码的输入速度'''
        for i in str:
            ele.send_keys(i)
            time1 = random.random() + 1
            time.sleep(time1)

    def date_start(self, del_day):
        date_now = datetime.datetime.now()
        date_del = datetime.timedelta(days=del_day)
        date_1 = date_now - date_del
        return date_end(date_1)

    @property
    def get_cookies(self):
        '''获取 cookies'''

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # 初始化浏览器对象
        sel = webdriver.Chrome(chrome_options=chrome_options)
        sel.maximize_window()
        sel.get(Login_Url)
        sel.implicitly_wait(3)

        tabs = sel.find_element_by_xpath('//li[contains(text(),"账密登录")]')
        tabs.click()

        # 找到用户名字输入框
        uname = sel.find_element_by_id('J-input-user')
        uname.clear()
        print('正在输入账号.....')
        self.wait_input(uname, self.user)
        time.sleep(1 + random.random())
        # 找到密码输入框
        upass = sel.find_element_by_id('password_rsainput')
        upass.clear()
        print('正在输入密码....')
        self.wait_input(upass, self.passwd)
        # 截图查看
        # sel.save_screenshot('1.png')
        # 找到登录按钮
        butten = sel.find_element_by_id('J-login-btn')
        time.sleep(1 + random.random())
        butten.click()

        # sel.save_screenshot('2.png')
        print(sel.current_url)
        # 跳转到账单页面
        print('正在跳转页面....')
        sel.get(Bill_Url)
        sel.implicitly_wait(10)
        # sel.save_screenshot('3.png')
        sel.save_screenshot('d:\\二维码.png')
        time.sleep(1 + random.random())
        os.startfile('d:\\二维码.png')
        try:
            while True:
                qrcode = sel.find_element_by_xpath('//div[@class="qrcode-info"]')
        except:
            os.remove('d:\\二维码.png')

        time.sleep(1 + random.random())
        # 设置自定义时间
        select = sel.find_element_by_xpath('//a[@seed="JDatetimeSelect-link"]')
        time.sleep(1 + random.random())
        select.click()
        option = sel.find_element_by_xpath('//li[@data-value="customDate"]')
        time.sleep(0.5 + random.random())
        option.click()
        # 设置时间起
        sel.execute_script('window.document.getElementById("beginDate").value="' + self.date_start(7) + '"')

        # 设置时间止
        sel.execute_script('window.document.getElementById("endDate").value="' + date_end() + '"')
        # 搜索
        seach = sel.find_element_by_id('J-set-query-form')
        time.sleep(2 + random.random())
        seach.click()
        # 迭代获取所有数据
        self.find_page_next(sel)
        # 关闭浏览器
        sel.close()
        return 'success'

    def find_page_next(self, sel):
        try:
            self.write_info(sel)
            time.sleep(3 + random.random())
            next_page = sel.find_element_by_xpath('//a[@class="page-next page-trigger"]')
            time.sleep(1 + random.random())
            next_page.click()
        except:
            return
        else:
            self.find_page_next(sel)

    def write_info(self, sel):
        texts = sel.find_elements_by_xpath(
            '/html/body/div[@id="container"]/div[@id="content"]/div[@id="main"]/table[@id="tradeRecordsIndex"]/tbody/tr')
        for text in texts:
            tds = text.find_elements_by_tag_name('td')
            time2 = tds[0].text
            amount = tds[5].text
            code = tds[2].text
            bill_num = tds[3].text
            pay_name = tds[4].text
            pay_result = tds[7].text
            remark = tds[8].text
            self.info_list.append(
                dict(time=time2, amount=amount, code=code, bill_num=bill_num, pay_name=pay_name, pay_result=pay_result,
                     remark=remark))

    def write_txt(self):
        try:
            txt = open('D:\\weixin\\Alipay.txt', 'a')
            txt.write('\n')
            if len(self.info_list) > 0:
                txt.write(json.dumps(self.info_list, ensure_ascii=False))
                print(self.info_list)
                txt.write('\n')
        except:
            self.info_list.append({'error': '出现错误,请加站长支付宝好友获取充值码'})
        finally:
            txt.write('\n')
            txt.close()

    def set_cookies(self):
        '''将获取到的 cookies 加入 session'''
        c = self.get_cookies
        return c

    def login_status(self):
        '''判断登录状态'''
        # 添加 cookies
        return self.set_cookies()

    def get_data(self):
        '''
        利用 bs4 库解析 html
        并抓取数据，
        数据以字典格式保存在列表里
        '''
        return self.login_status()


if __name__ == '__main__':
    # test:
    test = Alipay_Bill_Info(HEADERS, USERNMAE, PASSWD)
    data = test.get_data()
    print(data)
