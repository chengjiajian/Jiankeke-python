from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
#from build.pingan_info import insuranceList, officialList, plateInfo
from build.pingan_mysql_usage import mysql, MysqlUsage
from build.pingan_usage import *
from build.pingan_settings import *
from dateutil.parser import parse
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
import datetime
import json
import time
import re


# 主面板
class PingAnCrew:

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
            sql_content = "select username,password from insurance_account where region='{}' and company_name='{}'".format(region_info, '平安')
            cursor.execute(sql_content)
            result = cursor.fetchall()[0]
            cpic_username, cpic_password = result['username'], result['password']
        self.driver.get('https://pacas-login.pingan.com.cn/cas/PA003/ICORE_PTS/login')
        username = self.driver.find_element_by_xpath('//*[@id="username"]')
        pwd = self.driver.find_element_by_xpath(r'//*[@id="password"]')
        username.clear()
        pwd.clear()
        username.send_keys(cpic_username)
        pwd.send_keys(cpic_password)
        validCode = self.driver.find_element_by_xpath(r'//*[@id="randCodeText"]')
        if query_mode == 'auto':
            imageLocate = self.driver.find_element_by_xpath(r'//*[@id="randCode"]')
            savePath = 'validcode.png'
            validcode = crop_valid_code(save_path=savePath, driver=self.driver, image_element=imageLocate)
            validCode.send_keys(validcode)
        else:
            validCode.send_keys(input('input validcode'))
        self.driver.find_element_by_xpath(r'//*[@id="loginButton"]').click()
        while True:
            time.sleep(1)
            pageSource = self.driver.page_source
            if '立即登录' in pageSource:  # 检查页面登录情况
                if '登录认证错误' in pageSource:
                    write_down_error('登录认证错误')
                    self.stopHint = 1
                    return False
                elif '风控锁定' in pageSource:
                    write_down_error('风控锁定')
                    self.stopHint = 1
                    return False
                elif '请输入正确的验证码' in pageSource or '验证码错误' in pageSource:
                    write_down_error('验证码错误，尝试重新登录')
                    self.login()
                else:
                    write_down_error('未知错误，请查看页面\n\n\n {}'.format(pageSource))
                    self.stopHint = 1
                    return False
            else:
                print('its login now')
                return True

    # 检查登录状态
    def check_login(self):
        self.driver.get(r'https://icore-pts.pingan.com.cn/ebusiness/login.do')
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
    def transfer(self):
        self.driver.find_element_by_xpath(r'//*[@id="nav"]/li[3]/a').click()
        self.driver.switch_to.frame('main_c')
        self.driver.find_element_by_xpath('//*[@id="toibcsWriter"]').click()
        time.sleep(1)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'mainCont')))
        self.driver.switch_to.frame('main')
        WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'control-group')))
        time.sleep(3)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'mainContent')))
        Select(self.driver.find_element_by_xpath('//*[@id="agentAgreement"]')).select_by_index(1)
        botton = self.driver.find_element_by_xpath(
            r'//*[@id="mainContent"]/div[2]/div[2]/form/div[2]/div/div/button[1]')
        botton.click()
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'owner_isShowExtInfo personnelCtrl_isShowExtInfo')))
            return True
        except Exception:
            return False

    # 转回主界面
    def back_to_main(self):
        windows = self.driver.window_handles
        for i in windows[1:]:
            self.driver.switch_to.window(i)
            self.driver.close()
        self.driver.switch_to.window(windows[0])

    # 填写信息
    def fill_in_blanks(self, infos):
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'ownerDriverInfoDiv')))
        self.driver.find_element_by_xpath(r'//*[@id="ownerDriverInfoDiv"]/div/div[1]/div/input').send_keys(
            infos['ownerInfo']['ownerName'])  # 车主姓名
        id_type = '身份证'
        # 预留证件类型选择 口
        if id_type == '身份证':
            self.driver.find_element_by_xpath(r'//*[@id="ownerDriverInfoDiv"]/div/div[2]/div/input').send_keys(
                infos['ownerInfo']['ownerId'])  # 证件号
        else:
            selector = Select(
                self.driver.find_element_by_xpath('//*[@id="ownerDriverInfoDiv"]/div/div[2]/div/select'))
            selector.select_by_visible_text('其他')
            self.driver.find_element_by_xpath(r'//*[@id="ownerDriverInfoDiv"]/div/div[2]/div/input').send_keys(
                infos['ownerInfo']['ownerId'])  # 证件号
            self.driver.find_element_by_xpath('//*[@id="dp1534149415604"]')
        # 车辆信息
        self.plate = infos['carInfo']['plateNo']
        self.vinNo = infos['carInfo']['vehicleFrameNo']
        self.driver.find_element_by_xpath(r'//*[@id="vehicleLicenceCode"]').send_keys(
            '{}-{}'.format(self.plate[0], self.plate[1:]))  # 车牌号
        self.driver.find_element_by_xpath(r'//*[@id="engineNo"]').send_keys(infos['carInfo']['engineNo'])  # 发动机号
        self.driver.find_element_by_xpath(r'//*[@id="vehicleFrameNo"]').send_keys(self.vinNo)  # 车架号
        self.driver.find_element_by_xpath('//*[@id="VehicleFrameNoID"]/div/button').click()
        reg1 = 'watch:veh.brandParaOutYear" ui-valid-id=".*?" id="dp(.*?)"'  # 初等日期reg
        reg2 = 'ng-change="refreshBeginTimeC51\(\)" ui-valid-id=".*?" id="dp(.*?)"'  # 交强险reg
        reg3 = 'ui-valid="r datetime rule\.insure\.beginDate" ng-change="refreshBeginTimeC01\(\)" ng-disabled="ctrl\.isShowCommDate" ui-valid-id=.*? id="dp(.*?)"'  # 商业险reg
        htmlContent = self.driver.page_source
        firstRegist_id = re.findall(reg1, htmlContent)[0]  # 初等id
        self.firstRegist = infos['carInfo']['firstRegist']
        self.driver.find_element_by_xpath(r'//*[@id="dp{}"]'.format(firstRegist_id)).send_keys(
            self.firstRegist)  # 初等日期
        # 险种日期填写''
        # 商业险
        beginTime_commercial_id = re.findall(reg2, htmlContent)[0]  # 定位元素id
        beginTime_commercial = self.driver.find_element_by_xpath('//*[@id="dp{}"]'.format(beginTime_commercial_id))
        beginTime_commercial.clear()
        # 因为平安系统脑残，所以要分批录入
        comm_begin_time = infos['insuranceInfo']['commInfo']['beginTime']
        part1, part2, part3 = comm_begin_time.split('-')
        beginTime_commercial.send_keys('{}-{}-A'.format(part1, part2))
        beginTime_commercial.send_keys(part3)
        for i in range(2):
            beginTime_commercial.send_keys(Keys.ARROW_LEFT)
        beginTime_commercial.send_keys(Keys.BACK_SPACE)
        # 交强险
        beginTime_compulsory_id = re.findall(reg3, htmlContent)[0]  # 定位元素id
        beginTime_compulsory = self.driver.find_element_by_xpath('//*[@id="dp{}"]'.format(beginTime_compulsory_id))
        beginTime_compulsory.clear()
        # 因为平安系统脑残，所以要分批录入
        comp_begin_time = infos['insuranceInfo']['compInfo']['beginTime']
        part1, part2, part3 = comp_begin_time.split('-')
        beginTime_compulsory.send_keys('{}-{}-A'.format(part1, part2))
        beginTime_compulsory.send_keys(part3)
        for i in range(2):
            beginTime_compulsory.send_keys(Keys.ARROW_LEFT)
        beginTime_compulsory.send_keys(Keys.BACK_SPACE)
        # 勾选商业险
        self.driver.find_element_by_xpath(
            '//*[@id="auto0Div"]/div/div[3]/div/div[2]/form[2]/div/div[1]/div[1]/div/div[1]/label/input').click()
        self.roll_page(1000)
        time.sleep(2)
        print(json.dumps(infos, sort_keys=True, indent=2, ensure_ascii=False))
        count = 0  # 下拉框偏移度
        # ===============================================交强险入口勾选情况
        if infos['insuranceInfo']['commInfo']['jiaoqiangInsurance']['baoe'] == '不投保':
            pass
        else:  # 点击交强险
            self.driver.find_element_by_xpath('//*[@id="taxInfoTitle"]/div/div/label/input').click()
        self.roll_page(1300)
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/input').click()  # 勾选车损
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/input').click()  # 勾选三者险
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[4]/td[1]/input').click()  # 勾选抢盗险
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[5]/td[1]/input').click()  # 勾选司机险
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[6]/td[1]/input').click()  # 勾选乘客险
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[7]/td[1]/input').click()  # 勾选 玻璃单独破碎险
        self.driver.find_element_by_xpath(
            r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[8]/td[1]/input').click()  # 勾选 车身划痕损失险
        # ===============================================车辆损失险
        CheSun = infos['insuranceInfo']['commInfo']['chesuanInsurance']
        if CheSun['baoe'] == '不投保':
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/input').click()  # 勾选车损
        # ===============================================第三方
        DiSanFang = infos['insuranceInfo']['commInfo']['disanfangInsurance']
        if DiSanFang['baoe'] != '不投保':
            print(len(self.driver.find_elements_by_class_name('ng-pristine')))
            if len(self.driver.find_elements_by_class_name('ng-pristine')) != 121:
                count = len(self.driver.find_elements_by_class_name('ng-pristine')) - 121
            selector = Select(self.driver.find_elements_by_class_name('ng-pristine')[64 + count])  # + count
            if int(DiSanFang['baoe']) > 1000000:
                count += 2
                selector.select_by_visible_text('100+')
                self.driver.find_element_by_xpath(
                    '//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[3]/td[3]/div/table/tbody/tr[2]/td/input').send_keys(
                    str(int(int(DiSanFang['baoe']) / 10000)))
            else:
                count += 4
                selector.select_by_visible_text(str(int(DiSanFang['baoe']) // 10000))  # 保额选择
        HuaHen = infos['insuranceInfo']['commInfo']['huahenInsurance']
        if HuaHen['baoe'] != '不投保':
            test_list = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5]
            for i in test_list:
                num = int(count)
                try:
                    print(len(self.driver.find_elements_by_class_name('ng-pristine')))
                    num += i
                    print(num)
                    selector = Select(self.driver.find_elements_by_class_name('ng-pristine')[77 + num])
                    selector.select_by_visible_text(HuaHen['baoe'])  # 车身划痕损失险 选择
                except Exception as e:
                    return False
        else:
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[8]/td[1]/input').click()  # 勾选 车身划痕损失险
        # ===============================================全车盗抢
        QiangDao = infos['insuranceInfo']['commInfo']['chedaoInsurance']
        if QiangDao['baoe'] == '不投保':
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[4]/td[1]/input').click()  # 勾选抢盗险
        # ===============================================司机座位责任险
        SiJi = infos['insuranceInfo']['commInfo']['sijiInsurance']
        if SiJi['baoe'] != '不投保':
            sijiValue = self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[5]/td[3]/div/span/input')
            sijiValue.click()
            for i in range(10):
                sijiValue.send_keys(Keys.BACK_SPACE)
            sijiValue.send_keys(SiJi['baoe'])
        else:
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[5]/td[1]/input').click()  # 勾选司机险
        # ===============================================乘客座位责任险
        ChengKe = infos['insuranceInfo']['commInfo']['chenkeInsurance']
        if ChengKe['baoe'] != '不投保':
            chengkeValue = self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[6]/td[3]/div/span/input[2]')
            for i in range(10):
                chengkeValue.send_keys(Keys.BACK_SPACE)
            chengkeValue.send_keys(ChengKe['baoe'])
        else:
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[6]/td[1]/input').click()  # 勾选乘客险
        # ===============================================玻璃单独破碎险
        BoLi = infos['insuranceInfo']['commInfo']['boliInsurance']
        if BoLi['baoe'] != '不投保':
            if BoLi['baoe'] == '进口':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[7]/td[3]/div/input[2]').click()  # 选择进口（默认为国产）
        else:
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[7]/td[1]/input').click()  # 勾选 玻璃单独破碎险
        # ===============================================车身划痕损失险
        self.driver.find_element_by_xpath \
            (r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[10]/td[1]/input').send_keys(Keys.TAB)
        # ===============================================自燃损失险
        ZiRan = infos['insuranceInfo']['commInfo']['ziranInsurance']
        if ZiRan['baoe'] == '投保':
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[9]/td[1]/input').click()  # 勾选 自燃损失险
        # ===============================================发动机涉水损失险
        SheShui = infos['insuranceInfo']['commInfo']['fadongjiInsurance']
        if SheShui['baoe'] == '投保':
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[10]/td[1]/input').click()  # 勾选 发动机涉水损失险
        # ===============================================指定专修厂特约条款
        ZhuanXiu = infos['insuranceInfo']['commInfo']['zhuanxiuInsurance']
        # ===============================================无法找到第三方特约险
        TeYue = infos['insuranceInfo']['commInfo']['teyueInsurance']
        if ZhuanXiu or TeYue:
            self.driver.find_element_by_xpath(r'//*[@id="ctrl_isShowExtDuty"]/span').click()
            self.driver.find_element_by_xpath(r'//*[@id="plan-ext-tbl"]/tbody/tr[8]/td[1]/input').send_keys(
                Keys.TAB)
            if ZhuanXiu['baoe'] == '投保':
                self.driver.find_element_by_xpath(
                    r'//*[@id="plan-ext-tbl"]/tbody/tr[5]/td[1]/input').click()  # 勾选 发动机涉水损失险
                # rateInput = self.driver.find_element_by_xpath(r'//*[@id="rate"]')
                # rateInput.clear()
                # rateInput.send_keys('0.3')
            if TeYue['baoe'] == '投保':
                self.driver.find_element_by_xpath(
                    r'//*[@id="plan-ext-tbl"]/tbody/tr[6]/td[1]/input').click()  # 勾选 无法找到第三方特约险
        # 切换页面视角
        self.roll_page(1300)
        # 不计免赔按钮统计
        if ChengKe['baoe'] != '不投保':
            if ChengKe['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[6]/td[4]/input[1]').click()  # 取消 不计免赔勾选
        if SiJi['baoe'] != '不投保':
            if SiJi['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[5]/td[4]/input[1]').click()  # 取消 不计免赔勾选
        if QiangDao['baoe'] != '不投保':
            if QiangDao['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[4]/td[4]/input[1]').click()  # 取消 不计免赔勾选
        if DiSanFang['baoe'] != '不投保':
            if DiSanFang['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[3]/td[4]/input[1]').click()  # 取消 不计免赔 的勾
        if CheSun['baoe'] != '不投保':
            if CheSun['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[2]/td[4]/input[1]').click()
        if HuaHen['baoe'] != '不投保':
            if HuaHen['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[8]/td[4]/input[1]').click()  # 取消 不计免赔勾选
        if ZiRan['baoe'] != '不投保':
            if ZiRan['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[9]/td[4]/input[1]').click()  # 取消 不计免赔勾选
        self.driver.find_element_by_xpath(r'//*[@id="plan-ext-tbl"]/tbody/tr[2]/td[1]/input').send_keys(Keys.TAB)
        if SheShui['baoe'] != '不投保':
            if SheShui['insuranceType'] == '0':
                self.driver.find_element_by_xpath(
                    r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[10]/td[4]/input[1]').click()  # 取消 不计免赔勾选
        # 点击报价
        self.driver.find_element_by_xpath(r'//*[@id="commonOperate"]/div[2]/button[2]').click()
        return True

    # 报价信息
    def calculate_price(self):
        info_dict = {'error_message': 'default'}
        response = self.driver.page_source
        if '申请报价出现错误！' in response:
            print('申请报价出现错误')
            self.driver.switch_to.frame('doalogBox')
            reg = re.compile('''<td>
                    <label class="ng-binding">(.*?)</label>
                </td>
                <td>
                    <label class="ng-binding">流程号：(.*?)</label>
                </td>''')
            error_info = list(set(re.findall(reg, self.driver.page_source)))
            error_str = ''
            for num, message in error_info:
                error_str += '{},流水号：{}\n'.format(num, message)
            input('申请报价出现错误,enter')
            info_dict = {'status': 0,
                         'error_message': error_str}
            self.driver.switch_to.default_content()
        elif '申请报价完成并保存报价单成功' in response:
            reg = re.compile('申请报价完成并保存报价单成功，子询价单号:Q(\d+)')
            quotation_number = re.findall(reg, response)
            if quotation_number:
                info_dict = {'status': 1,
                             'error_message': "Q{}".format(quotation_number[0])}
            else:
                info_dict = {'status': 0,
                             'error_message': '报价成功，报价号获取失败'}
            self.driver.switch_to.default_content()
            print(info_dict)
        elif '车辆信息校验不通过' in response:
            print('车辆信息校验不通过')
            try:
                self.driver.find_element_by_xpath(
                    r'/html/body/div[1]/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/input').click()
                selector = Select(self.driver.find_elements_by_class_name('ng-pristine')[17])
                self.car_selector += 1
                selector.select_by_index(self.car_selector)
                time.sleep(1)
                # 点击重新报价
                self.driver.find_element_by_xpath(r'//*[@id="commonOperate"]/div[2]/button[2]').click()
                return self.calculate_price()
            except Exception as e:
                write_down_error(e)
                info_dict = {'status': 0,
                             'error_message': '报价失败，车型校验未通过'}
                self.driver.switch_to.default_content()
        elif '车型信息' in response:
            print('车型信息')
            self.driver.switch_to.frame('doalogBox')
            response = self.driver.page_source
            year_reg = re.compile('<td class="ng-binding">(20\d{2})</td>')
            years = re.findall(year_reg, response)
            car_year = int(self.firstRegist.split('-')[0])
            for i, year in enumerate(years):
                if car_year >= int(year):
                    choice = i
                    break
            self.driver.find_element_by_xpath(
                '/html/body/fieldset/form/table[2]/tbody/tr[{}]/td[1]/input'.format(2 + choice)).click()
            time.sleep(1)
            self.driver.find_element_by_xpath(
                '/html/body/fieldset/form/table[2]/tbody/tr[{}]/td/button'.format(2 + len(years))).click()
            self.driver.switch_to.parent_frame()
            time.sleep(10)
            return self.calculate_price()
        elif '续保检索及新能源车校验' in response:
            print('续保检索及新能源车校验')
            self.driver.switch_to.frame('doalogBox')
            self.driver.find_element_by_xpath('/html/body/div[2]/div/button').click()
            try:
                if '本次投保保险起期大于上年保单止期，请确认本年保险起止日期' in self.driver.page_source:
                    self.driver.find_element_by_xpath(
                        '/html/body/div[1]/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/input').click()
                    self.driver.switch_to.parent_frame()
                    time.sleep(5)
                    return self.calculate_price()
            except Exception as e:
                write_down_error(e)
                info_dict = {'status': 0,
                             'error_message': '报价失败，车型校验未通过'}
                self.driver.switch_to.default_content()
        elif '平台返回信息' in response:
            reg = re.compile('>平台返回信息:(.*?)<')
            try:
                reply_info = re.findall(reg, response)[0]
            except Exception:
                reply_info = ''
            info_dict = {'status': 0,
                         'error_message': reply_info}
            return info_dict
        elif '重复投保' in response:
            print(response)
            while self.plate not in response:
                if self.vinNo in response:
                    break
                print('plate not in')
                time.sleep(1)
                response = self.driver.page_source
            htmlsoup = BeautifulSoup(response, 'lxml')
            repeat = htmlsoup.find_all(attrs={'class': 'table table-bordered table-condensed'})[0]
            header_reg = re.compile('<td class="w\d{1,3}">(.*?)</td>')
            info_reg = re.compile('<td class="ng-binding">(.*?)</td>')
            header_info = re.findall(header_reg, str(repeat))
            info_info = re.findall(info_reg, str(repeat))
            reply_info = repeat.find_all(attrs={'class': 'mb5 f_c_f00 f20'})[0].get_text()
            if len(header_info) == len(info_info):
                for i, value in enumerate(header_info):
                    reply_info += "\n{} : {}".format(value, info_info[i])
            info_dict = {'status': 0,
                         'error_message': reply_info}
            self.driver.switch_to.default_content()
            return info_dict
        else:
            print('else')
            info_dict = {'status': 0,
                         'error_message': '未知错误，请联系管理员查询 错误码:{}'.format('test')}
            self.driver.switch_to.default_content()

        return info_dict

    # 关闭引擎
    def close_mission(self):
        self.driver.close()



def sum_job():
    crewer = PingAnCrew()
    crewer.login()
    time_count = 0
    while True:
        if crewer.check_login():
            # 原始数据
            #info = MysqlUsage.get_one_piece_query()
            info = {'id': 43, 'inquiryId': 'GGCX153472814953803', 'companyId': None, 'isRenewal': 0, 'companyName': '平安', 'cityName': '四川', 'licenseNumber': '川AML067', 'ownerName': '刘静', 'idCard': '513622198003160182', 'chesuanInsurance': {'insuranceType': '1', 'baoe': '投保'}, 'disanfangInsurance': {'insuranceType': '1', 'baoe': '500000'}, 'chedaoInsurance': {'insuranceType': '1', 'baoe': '投保'}, 'sijiInsurance': {'baoe': '不投保'}, 'chenkeInsurance': {'baoe': '不投保'}, 'boliInsurance': {'baoe': '国产'}, 'huahenInsurance': {'insuranceType': '1', 'baoe': '2000'}, 'ziranInsurance': {'insuranceType': '1', 'baoe': '投保'}, 'fadongjiInsurance': {'baoe': '不投保'}, 'zhuanxiuInsurance': {'baoe': '投保'}, 'teyueInsurance': {'baoe': '投保'}, 'jiaoqiangInsurance': {'baoe': '投保'}, 'chechuanInsurance': {'baoe': '投保'}, 'insuranceStartTime': datetime.datetime(2018, 11, 22, 0, 0), 'insuranceEndTime': datetime.datetime(2019, 11, 22, 0, 0), 'forceInsuranceStartTime': datetime.datetime(2018, 11, 22, 0, 0), 'insuranceEndTimetwo': datetime.datetime(2019, 11, 20, 0, 0), 'forcePremium': None, 'forceInsurances': None, 'creator': 'admin', 'contact': '18516670899', 'company': '', 'Inquirytype': '', 'createTime': datetime.datetime(2018, 8, 20, 10, 27, 36), 'updateTime': datetime.datetime(2018, 11, 9, 15, 45, 55), 'initialDate': datetime.datetime(2013, 7, 15, 0, 0), 'vin': '4JGDF2EE1DA155619', 'ownerContact': '', 'planName': '方案1', 'motorNum': '64282641361031', 'state': 0}
            # try:
            if info:
                write_down_error(str(info))
                crewer.transfer()
                if crewer.fill_in_blanks(infos=sum_up_info(info)):
                    time.sleep(5)
                    price_return = crewer.calculate_price()
                    if price_return:
                        if price_return['status'] == 1:
                            pass
            else:
                print('no valid info')
                time.sleep(10)
                time_count += 10
                if time_count / 60 == 15:
                    write_down_error('心跳反应')
                    time_count = 0
        else:
            break
if __name__ == '__main__':
    sum_job()













