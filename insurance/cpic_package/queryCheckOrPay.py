from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from build.cpic_usage import write_down_error, crop_valid_code, write_down_error_check_or_pay
from build.cpic_info import insuranceList, officialList, plateInfo
from build.cpic_mysql_usage import mysql, MysqlUsage
from build.cpic_settings import *
from dateutil.parser import parse
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
import datetime
import json
import time
import re


# 主面板
class TaiPingYangCrew:

    def __init__(self):
        """
        :param wbdriver: 内核工具
        """
        if wbdriver_type == 'visible':
            self.driver = webdriver.Chrome(executable_path=cpic_executable_path)
        else:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=cpic_executable_path)
        self.car_selector = 0
        self.driver.set_window_size(1280, 800)
        self.driver.implicitly_wait(10)
        self.stop_hint = 0
        self.refresh_times = 0

    # 调取现在的 cookies
    def get_now_cookies(self):
        return self.driver.get_cookies()

    # 翻页
    def roll_page(self, roll_long):
        """
        :param roll_long: 划页的长度
        :return:
        """
        js = "var q=document.body.scrollTop={}".format(roll_long)
        self.driver.execute_script(js)

    # 登陆
    def login(self):
        """
        负责登录的模块，确认登录状态
        :return:
        """
        with mysql() as cursor:
            sql_content = "select username,password from insurance_account where region='{}' and company_name='{}'".format(region_info, '太平洋')
            cursor.execute(sql_content)
            result = cursor.fetchall()[0]
            cpic_username, cpic_password = result['username'], result['password']
        self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/common/login.html')
        username = self.driver.find_element_by_xpath(r'//*[@id="j_username"]')
        username.clear()
        username.send_keys(cpic_username)
        self.driver.find_element_by_xpath(r'//*[@id="_password"]').send_keys(cpic_password)
        validCode = self.driver.find_element_by_xpath(r'//*[@id="verifyCode"]')
        if query_mode == 'auto':
            imageLocate = self.driver.find_element_by_xpath(r'//*[@id="capImg"]')
            savePath = 'validcode.png'
            validcode = crop_valid_code(save_path=savePath, driver=self.driver, image_element=imageLocate)
            validCode.send_keys(validcode)
        else:
            validCode.send_keys(input('input validcode'))
        self.driver.find_element_by_xpath(r'//*[@id="j_login"]').click()
        while True:
            pageContent = self.driver.page_source
            if '终端及经办人选择' in pageContent:
                if '何爱国' in pageContent:
                    self.driver.find_element_by_xpath(r'//*[@id="__agent_2__"]').click()
                    self.driver.find_element_by_xpath(r'//*[@id="loginBtn"]').click()
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'width-2')))
                    time.sleep(1)
                    return True
                time.sleep(1)
            elif '验证码错误' in pageContent or '用户名或密码错误' in pageContent or '验证码不能为空' in pageContent:
                return self.login()

    # 检查当前登录状态
    def check_login(self):
        self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/common/index.html')
        pageSource = self.driver.page_source
        while True:
            if self.stop_hint == 1:
                return False
            if '立即登录' in pageSource:  # 检查页面登录情况
                write_down_error('refresh times: {}'.format(self.refresh_times))
                if self.login():
                    break
            else:
                print('its login now')
                print(self.refresh_times)
                self.refresh_times += 1
                break
        return True

    # 转移到出价界面
    def transfer(self, transfer_type='check'):
        if transfer_type == 'check':
            self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/quotation_search/quotation_search.html')
        elif transfer_type == 'pay':
            self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/premium_payment/premium_payment.html')

    # 核保查询
    def queryCheck(self, query_dict):
        """
        :param query_dict: query_dict['query_num'] 报价单号
                            query_dict['query_time'] 报价时间
        :return:
        """
        self.driver.find_element_by_xpath('//*[@id="quotationNo"]').send_keys(query_dict['query_num'])
        date_input = self.driver.find_element_by_xpath(r'//*[@id="endDate"]')
        date_input.clear()
        date_input.send_keys(query_dict['query_time'])
        self.driver.find_element_by_xpath(r'//*[@id="queryCondition"]/div/table/tbody/tr[1]/td[4]/input').click()
        self.driver.find_element_by_xpath(r'//*[@id="search"]').click()
        #for i in range(2):
        ActionChains(self.driver).double_click(self.driver.find_element_by_xpath(r'//*[@id="resultTable"]/tbody/tr[1]/td[2]')).perform()
        #self.driver.find_element_by_xpath(r'//*[@id="resultTable"]/tbody/tr[1]/td[2]').click()
        while True:
            if '车辆信息' in self.driver.page_source:
                self.driver.find_element_by_xpath(r'//*[@id="next"]/img').click()
            elif '保险权益人' in self.driver.page_source:
                #WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, r'//*[@id="next"]/img')))
                mobile_input1 = self.driver.find_element_by_xpath(r'//*[@id="insuranceInfoMobilePhone"]')
                mobile_phone = '17601228909'
                address = '金钟路968号'
                # 被保险人 投保人 不是同一个人情况
                if not self.driver.find_element_by_xpath('//*[@id="samePolicyHolder"]').is_selected():
                    mobile_input2 = self.driver.find_element_by_xpath(r'//*[@id="insuranceInfoInMobilePhone"]')
                    if not mobile_input1.get_attribute('value') or not mobile_input2.get_attribute('value'):
                        mobile_input1.clear()
                        mobile_input2.clear()
                        for i in mobile_phone:
                            mobile_input1.click()
                            mobile_input1.send_keys(i)
                            mobile_input2.click()
                            mobile_input2.send_keys(i)
                            self.driver.find_element_by_xpath(r'//*[@id="holderVo"]/div/table/tbody/tr[3]/td[5]/input').click()
                    address_input1 = self.driver.find_element_by_xpath(r'//*[@id="holderVo"]/div/table/tbody/tr[3]/td[7]/input')
                    address_input2 = self.driver.find_element_by_xpath(r'//*[@id="insureVo"]/table/tbody/tr[3]/td[7]/input')
                    if not address_input1.get_attribute('value') or not address_input2.get_attribute('value'):
                        address_input1.clear()
                        address_input2.clear()
                        address_input1.send_keys(address)
                        address_input2.send_keys(address)
                # 被保险人 投保人 是同一个人情况
                else:
                    if not mobile_input1.get_attribute('value'):
                        mobile_input1.clear()
                        for i in mobile_phone:
                            mobile_input1.click()
                            mobile_input1.send_keys(i)
                            self.driver.find_element_by_xpath(r'//*[@id="holderVo"]/div/table/tbody/tr[3]/td[5]/input').click()
                    address_input1 = self.driver.find_element_by_xpath(r'//*[@id="holderVo"]/div/table/tbody/tr[3]/td[7]/input')
                    if not address_input1.get_attribute('value'):
                        address_input1.clear()
                        address_input1.send_keys(address)
                # 能看到保险权益人说明到底了，跳出循环
                break
            elif '保险方案' in self.driver.page_source:
                print(self.driver.page_source)
                self.driver.find_element_by_xpath(r'//*[@id="next"]/img').click()
            time.sleep(2)
        # 预核保
        self.driver.find_element_by_xpath(r'//*[@id="yhb"]/img').click()
        while True:
            pageSource = self.driver.page_source
            if '预核保提示' in pageSource:
                hint = re.findall('id="questionTxt">(.*?)</div>', pageSource)
                if hint:
                    hint = hint[0]
                # 点掉弹窗
                self.driver.find_element_by_xpath('//*[@id="fClose"]/a').click()
                break
            elif '错误信息' in pageSource:
                hint = re.findall(re.compile('\[预核保请求\]报价失败！报价引擎返回：报价引擎提示：(.*?)\(平台提示\)'), pageSource)
                if hint:
                    print(hint)
                break
            time.sleep(1)
        check_list = ['商业险：标准件,核保通过',
                      '交强险：标准件,核保通过',
                      '交强险：标准件,核保通过<br />商业险：标准件,核保通过'
                      ]
        if hint in check_list:
            # 提交审核
            self.driver.find_element_by_xpath('//*[@id="submitAudit"]/img').click()
            while True:
                pageSource = self.driver.page_source
                if '信息提示' in pageSource:
                    handIn = re.findall('<div class="text-center lh-25 message">(.*?)</div>',pageSource)
                    print(handIn)
                    break
                time.sleep(1)
            # 立即支付
            _status = True
        else:
            for i in check_list:
                hint = re.sub(i, '', hint)
            hint = re.sub('<br />', '', hint)
            print(hint)
            _status = False
        self.driver.get('http://issue.cpic.com.cn/ecar/view/portal/page/quotation_search/quotation_search.html')
        return _status

    # 支付查询
    def queryPay(self, query_dict):
        self.driver.get('http://issue.cpic.com.cn/ecar/view/portal/page/premium_payment/premium_payment.html')
        self.driver.find_element_by_xpath(r'//*[@id="queryCondition"]/div/table/tbody/tr[1]/td[2]/input').send_keys(query_dict['query_num'])
        date_input = self.driver.find_element_by_xpath(r'//*[@id="endDate"]')
        date_input.clear()
        date_input.send_keys(query_dict['query_time'])
        self.driver.find_element_by_xpath(r'//*[@id="search"]').click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'premiumCheckAll')))
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="premiumCheckAll"]').click()
        self.driver.find_element_by_xpath('//*[@id="pay"]').click()
        pay_select = Select(self.driver.find_element_by_id('payWay'))
        pay_select.select_by_visible_text('划卡')  # 支付类型
        time.sleep(1)
        bank_select = Select(self.driver.find_element_by_id('cooperant'))
        bank_select.select_by_visible_text('交通银行')  # 支付银行
        self.driver.find_element_by_xpath(r'//*[@id="payDialog"]/div[2]/div[6]/a[1]').click()
        base_times = 0
        while True:
            reg = re.compile('src="(data:.*?)" /></div>')
            a = re.findall(reg, self.driver.page_source)
            if a:
                pic_base = re.sub('&#10;', '', a[0])
                return pic_base
            time.sleep(1)
            base_times += 1
            if base_times >= 10:
                break
        return False


    # 回到主界面
    def back_to_main(self):
        self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/common/index.html')

    # 关闭引擎
    def close_mission(self):
        self.driver.close()


def sum_job():
    crewer = TaiPingYangCrew()#wbdriver='Chrome'
    crewer.login()  # 登录
    time_count = 0
    while True:
        if crewer.check_login():
            info = {'type': 'check', 'query_num': 'QCHDA81Y1418F031000M', 'query_time': '2018-11-08'}  # 从库里取一条保单号数据出来
            # try:
            if info:
                write_down_error_check_or_pay(str(info))  # 日志记录
                crewer.transfer(info['type'])  # 跳转
                if info['type'] == 'check':
                    pic_base = 0
                    if crewer.queryCheck(query_dict=info):
                        time.sleep(3)
                        pic_base = crewer.queryPay(info)
                elif info['type'] == 'pay':
                    pic_base = crewer.queryPay(info)
                if pic_base:
                    #成功获取了支付码
                    print(pic_base)
                else:
                    # 没有获取到支付码
                    pass
            else:
                print('no valid info')
                time.sleep(10)
                time_count += 10
                if time_count / 60 == 15:
                    write_down_error_check_or_pay('心跳反应')
                    time_count = 0
            # except Exception as e:
            #     write_down_error(str(e))
            #     crewer.driver.save_screenshot('error pic{}.png'.format(str(datetime.datetime.now())))
            #     input(str(e))
            # input('end')
        else:
            break


if __name__ == '__main__':
    sum_job()
