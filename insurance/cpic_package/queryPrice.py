from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium import webdriver
from build.cpic_usage import write_down_error, crop_valid_code
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


# 把返回的数据整理完毕
def sum_up_response(inquiryInfo, error_message, res_dictionary):
    reptileDict = {}
    reptileDict['id'] = inquiryInfo['id']
    reptileDict['inquiryId'] = inquiryInfo['inquiryId']
    reptileDict['isRenewal'] = 0  # 没有续保情况时候默认为0
    reptileDict['cityName'] = '四川'  # 没有筛选情况下默认为四川
    if 'commercialInsuransVo' in res_dictionary['quotesInfo']:
        # 商业险
        commInfo = res_dictionary['quotesInfo']['commercialInsuransVo']
        # 折扣率信息
        reptileDict['manageCoefNum'] = commInfo['nonClaimDiscountRate']  # 无赔款折扣系数
        reptileDict['illegalCoefNum'] = commInfo['trafficTransgressRate']  # 交通违法系数
        reptileDict['selfChannelNum'] = commInfo['comm_channelRate']  # 自主渠道系数
        reptileDict['selfUnderNum'] = commInfo['comm_underwritingRate']  # 自主核保系数
        # 商业险详细
        reptileDict['insuranceCompanyNameOne'] = '太平洋保险'  # 商业险投保公司
        reptileDict['policyOneNo'] = commInfo['comm_insuranceQueryCode']  # 商业险保单号
        reptileDict['insuranceCompanyOneStartDate'] = commInfo['stStartDate']  # 商业险起始日期
        reptileDict['insuranceCompanyOneEndDate'] = commInfo['stEndDate']  # 商业险截止日期
        reptileDict['insurances'] = ''  # 商业险险种列表
        reptileDict['insurancePrice'] = commInfo['premium']  # 商业险保费

        # =====================================================车辆损失险
        if 'DAMAGELOSSCOVERAGE' in commInfo:
            reptileDict['chesuanInsuranceBaoe'] = res_dictionary['DamagePrice']  # 车辆损失保额
            reptileDict['chesuanInsurancePrice'] = commInfo['DAMAGELOSSCOVERAGE']['premium']  # 车辆损失险额
        else:
            reptileDict['chesuanInsuranceBaoe'] = 0  # 车辆损失保额
            reptileDict['chesuanInsurancePrice'] = 0  # 车辆损失险额
        # =====================================================第三者责任险额
        if 'THIRDPARTYLIABILITYCOVERAGE' in commInfo:
            reptileDict['disanfangInsurancePrice'] = commInfo['THIRDPARTYLIABILITYCOVERAGE']['premium']  # 第三者责任险额
        else:
            reptileDict['disanfangInsurancePrice'] = 0  # 第三者责任险额
        # =====================================================全车盗抢险额
        if 'THEFTCOVERAGE' in commInfo:
            reptileDict['chedaoInsurancePrice'] = commInfo['THEFTCOVERAGE']['premium']  # 全车盗抢险额
        else:
            reptileDict['chedaoInsurancePrice'] = 0  # 第三者责任险额
            # =====================================================司机座位责任险额
        if 'INCARDRIVERLIABILITYCOVERAGE' in commInfo:
            reptileDict['sijiInsurancePrice'] = commInfo['INCARDRIVERLIABILITYCOVERAGE']['premium']  # 司机座位责任险额
        else:
            reptileDict['sijiInsurancePrice'] = 0  # 司机座位责任险额
            # =====================================================乘客座位责任险
        if 'INCARPASSENGERLIABILITYCOVERAGE' in commInfo:
            reptileDict['chenkeInsurancePrice'] = commInfo['INCARPASSENGERLIABILITYCOVERAGE']['premium']  # 乘客座位责任险(4座)额
        else:
            reptileDict['chenkeInsurancePrice'] = 0
            # =====================================================玻璃单独破碎险额
        if 'GLASSBROKENCOVERAGE' in commInfo:
            reptileDict['boliInsurancePrice'] = commInfo['GLASSBROKENCOVERAGE']['premium']  # 玻璃单独破碎险额
        else:
            reptileDict['boliInsurancePrice'] = 0
            # =====================================================车身划痕损失险额
        if 'CARBODYPAINTCOVERAGE' in commInfo:
            reptileDict['huahenInsurancePrice'] = commInfo['CARBODYPAINTCOVERAGE']['premium']  # 车身划痕损失险额
        else:
            reptileDict['huahenInsurancePrice'] = 0
            # =====================================================自燃损失险额
        if 'SELFIGNITECOVERAGE' in commInfo:
            reptileDict['ziranInsurancePrice'] = commInfo['SELFIGNITECOVERAGE']['premium']  # 自燃损失险额
        else:
            reptileDict['ziranInsurancePrice'] = 0
            # =====================================================发动机涉水损失险额
        if 'PADDLEDAMAGECOVERAGE' in commInfo:
            reptileDict['fadongjiInsurancePrice'] = commInfo['PADDLEDAMAGECOVERAGE']['premium']  # 发动机涉水损失险额
        else:
            reptileDict['fadongjiInsurancePrice'] = 0
            # =====================================================指定专修厂特约条款额
        if 'APPOINTEDREPAIRFACTORYSPECIALCLAUSE' in commInfo:
            reptileDict['zhuanxiuInsurancePrice'] = commInfo['APPOINTEDREPAIRFACTORYSPECIALCLAUSE']['premium']  # 指定专修厂特约条款额
        else:
            reptileDict['zhuanxiuInsurancePrice'] = 0
            # =====================================================无法找到第三方特约险额
        if 'DAMAGELOSSCANNOTFINDTHIRDSPECIALCOVERAGE' in commInfo:
            reptileDict['teyueInsurancePrice'] = commInfo['DAMAGELOSSCANNOTFINDTHIRDSPECIALCOVERAGE'][
                'premium']  # 无法找到第三方特约险额
        else:
            reptileDict['teyueInsurancePrice'] = 0
    if 'compulsoryInsuransVo' in res_dictionary['quotesInfo']:
        # 交强险详细
        compInfo = res_dictionary['quotesInfo']['compulsoryInsuransVo']
        reptileDict['insuranceCompanyNametwo'] = '太平洋保险'  # 交强险投保公司
        reptileDict['policyNo'] = compInfo['comp_insuranceQueryCode']  # 交强险保单号
        reptileDict['quotesPricetwo'] = compInfo['comp_totalPremium']  # 强制险出单费
        reptileDict['insuranceCompanyTwoStartDate'] = parse('2018-01-01')  # 交强险起始日期
        reptileDict['insuranceCompanyTwoEndDate'] = parse('2018-12-31')  # 交强险截止日期
        reptileDict['jiaoqiangInsurancePrice'] = compInfo['comp_standardPremium']  # 交强险额
        reptileDict['chechuanInsurancePrice'] = compInfo['comp_taxAmount']  # 车船税额
        # 不计免赔信息
    # 不计免赔
    reptileDict['bujimianpeiName'] = res_dictionary['nonDeductible']['name']  # 不计免赔险名
    reptileDict['bujimianpeiPrice'] = res_dictionary['nonDeductible']['value']  # 不计免赔保费
    if 'carInfo' in res_dictionary['quotesInfo']:
        # 车信息
        carInfo = res_dictionary['quotesInfo']['carInfo']
        reptileDict['vin'] = carInfo['carVIN']  # 车架号
        reptileDict['motorNum'] = carInfo['engineNo']  # 发动机号
        reptileDict['labeltype'] = carInfo['factoryType']  # 厂牌型号
        reptileDict['initialDate'] = carInfo['stRegisterDate']  # 初登日期
        reptileDict['ownerContact'] = 1383838438  # carInfo['phoneNo']  # 车主手机号码
        reptileDict['licenseNumber'] = carInfo['plateNo']  # 车牌号
        reptileDict['ownerName'] = carInfo['ownerName']  # 车主姓名
        reptileDict['idCard'] = carInfo['certNo']  # 证件号码
        reptileDict['carTypeCode'] = '02'  # carInfo['plateColor']  # 号牌种类
        reptileDict['approvedLoadQuality'] = carInfo['emptyWeight']  # 核定载质量
        reptileDict['operation'] = 0  # 使用性质 0非营运 1营运  #=======================预留
        reptileDict['households'] = 0  # 是否过户  #=======================预留
    # 表单信息
    reptileDict['insuranceCompanyId'] = res_dictionary['codeNo']  # 保单号
    reptileDict['quotesPrice'] = res_dictionary['sumPrice']  # 保费
    reptileDict['state'] = 1  # 1成功；2失败；3等待
    reptileDict['createTime'] = datetime.datetime.now()  # 创建时间
    reptileDict['updateTime'] = datetime.datetime.now()  # 修改时间
    reptileDict['message'] = error_message  # 爬虫信息
    reptileDict['rate'] = res_dictionary['quotesInfo']['commercialInsuransVo']['comm_premiumRatio']  # 折扣率
    reptileDict['company'] = '太平洋保险'  # 保险公司
    reptileDict['companyEndDate'] = parse(res_dictionary['quotesInfo']['commercialInsuransVo']['stEndDate'])  # 保险到期日
    return reptileDict


# 查询车型的模块
def car_model_query(targetID, carInfos,cookie):
    carName = carInfos.split('/')[0].strip()
    print(carName)
    urls = r'http://issue.cpic.com.cn/ecar/ecar/queryCarModel'
    headers = {'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'46',
                'Content-Type':'application/json;charset=UTF-8',
                'Cookie':cookie,
                'Host':'issue.cpic.com.cn',
                'Origin':'http://issue.cpic.com.cn',
                'Referer':'http://issue.cpic.com.cn/ecar/view/portal/page/quick_quotation/quick_quotation.html',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest'}
    payload ={"meta":{},"redata": {"name": carName}}
    response = requests.post(url=urls, data=json.dumps(payload), headers=headers)
    return_info ={}
    try:
        response = response.json()
        if response['message']['code'] == 'success':
            results = response['result']
            for countNum in range(0, len(results)):
                info = results[countNum]
                if targetID == info['moldCharacterCode']:
                    return_info['code'] = 1
                    return_info['foundid'] = countNum + 1
                    break
                else:
                    return_info['code'] = 0
    except  Exception as e:
        return_info['code'] = 0
    return return_info


#把selenium里的cookies 处理成 requests的 cocokies
def processCookie(cookie_list):
    str_list = []
    for cookie in cookie_list:
        str_list.append('{}={}'.format(cookie['name'],cookie['value']))
    str = ';'.join(str_list)
    return str


def get_accident_product_info(order_id, cookie):
    payload = {"meta": {}, "redata": {"quotationNo": "{}".format(order_id)}}
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Connection': 'keep-alive',
               'Content-Length': '59',
               'Content-Type': 'application/json;charset=UTF-8',
               'Cookie': cookie,
               'Host': 'issue.cpic.com.cn',
               'Origin': 'http://issue.cpic.com.cn',
               'Referer': 'http://issue.cpic.com.cn/ecar/view/portal/page/quick_quotation/quick_quotation.html',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest'}
    response = requests.post(r'http://issue.cpic.com.cn/ecar/quickoffer/queryQuickOffer',data=json.dumps(payload),headers=headers)
    try:
        response = response.json()
    except Exception as e:
        response = {"message":{"code":"falied","message":"","status":""}}
    quotesInfo = {}
    dictionary = {}
    if response['message']['code'] == 'success':
        # 车信息
        carInfo = response['result']['ecarvo']
        quotesInfo['carInfo'] = {}
        quotesInfo['carInfo']['carVIN'] = carInfo['carVIN']#车架号
        quotesInfo['carInfo']['certNo'] = carInfo['certNo']#证件号
        quotesInfo['carInfo']['engineNo'] = carInfo['engineNo']#发动机号
        quotesInfo['carInfo']['factoryType'] = carInfo['factoryType']#厂牌型号
        quotesInfo['carInfo']['stRegisterDate'] = carInfo['stRegisterDate']#初登日期
        #quotesInfo['carInfo']['phoneNo'] = carInfo['phoneNo']#车主手机号码
        quotesInfo['carInfo']['plateNo'] = carInfo['plateNo']#车牌号
        quotesInfo['carInfo']['ownerName'] = carInfo['ownerName']#车主姓名
        quotesInfo['carInfo']['plateColor'] = plateInfo[int(carInfo['plateColor'])]#号牌种类
        quotesInfo['carInfo']['emptyWeight'] = carInfo['emptyWeight']  #核定载质量
        quotesInfo['carInfo']['usage'] = carInfo['usage']  #使用性质 0非营运 1营运
        quotesInfo['carInfo']['isTrade'] = 0  #是否过户 预留字段
        if response['result']['commercial']:#商业险
            commInfo = response['result']['commercialInsuransVo']
            quotesInfo['commercialInsuransVo']={}
            quotesInfo['commercialInsuransVo']['nonClaimDiscountRate']        = commInfo['nonClaimDiscountRate']#无赔偿折扣系数
            quotesInfo['commercialInsuransVo']['trafficTransgressRate']       = commInfo['trafficTransgressRate']#交通违法系数
            quotesInfo['commercialInsuransVo']['comm_underwritingRate']       = commInfo['underwritingRate']  # 自主核保系数
            quotesInfo['commercialInsuransVo']['comm_channelRate']             = commInfo['channelRate']  # 自主渠道系数
            quotesInfo['commercialInsuransVo']['stStartDate']                   = commInfo['stStartDate']#起保时间
            quotesInfo['commercialInsuransVo']['stEndDate']                     = commInfo['stEndDate']#终保时间
            quotesInfo['commercialInsuransVo']['comm_ecompensationRate']      = commInfo['ecompensationRate']#预期赔付率
            quotesInfo['commercialInsuransVo']['comm_insuranceQueryCode']     =commInfo['insuranceQueryCode'] #商业险 投保查询码
            quotesInfo['commercialInsuransVo']['comm_totalEcompensationRate'] = commInfo['totalEcompensationRate']#交商合计预期赔付率
            quotesInfo['commercialInsuransVo']['comm_standardPremium']         = commInfo['standardPremium']#标准保费
            quotesInfo['commercialInsuransVo']['premium']                        = commInfo['premium']#折后保费
            quotesInfo['commercialInsuransVo']['comm_premiumRatio']            = commInfo['premiumRatio']#折扣率
        if response['result']['compulsory']:#交强险
            compInfo = response['result']['compulsoryInsuransVo']
            quotesInfo['compulsoryInsuransVo'] = {}
            quotesInfo['compulsoryInsuransVo']['comp_ecompensationRate']  = compInfo['ecompensationRate']#预期赔付率
            quotesInfo['compulsoryInsuransVo']['comp_insuranceQueryCode'] = compInfo['insuranceQueryCode']#投保查询码
            quotesInfo['compulsoryInsuransVo']['comp_payableAmount']      = compInfo['payableAmount']#当年应缴
            quotesInfo['compulsoryInsuransVo']['comp_registryNumber']     = compInfo['registryNumber']#税务登记号
            quotesInfo['compulsoryInsuransVo']['comp_standardPremium']    = compInfo['standardPremium']#交强险保费
            quotesInfo['compulsoryInsuransVo']['comp_taxAmount']          = compInfo['taxAmount']#车船税保费
            quotesInfo['compulsoryInsuransVo']['comp_totalPremium']       = compInfo['totalPremium']#交强险总计费用
            quotesInfo['compulsoryInsuransVo']['comp_taxpayerName']       = compInfo['taxpayerName']#纳税人名
            quotesInfo['compulsoryInsuransVo']['comp_taxpayerNo']         = compInfo['taxpayerNo']#身份证号
        commDetail = response['result']['quoteInsuranceVos']
        sumPrice = response['result']['totalPremium']
        nonDeductible = []
        nonDeductiblePrice=0
        for quote in commDetail:
            insurName = quote['insuranceCode']
            if 'DAMAGELOSSCOVERAGE'==insurName:
                DamageLossCoverage = quote['stAmount']
            if insurName in officialList:
                #名字 = 折后价
                quotesInfo['commercialInsuransVo'][insurName]={'premium':quote['premium']}
                if 'nonDeductible' in quote:
                    nonDeductible.append(officialList[insurName]['nickname'])
                    nonDeductiblePrice+=quote['nonDeductible']
                    #print(nonDeductiblePrice)
        dictionary = {'codeNo': order_id,
                      'sumPrice':sumPrice,
                      'quotesInfo': quotesInfo,
                      'nonDeductible': {'name': '、'.join(nonDeductible), 'value': nonDeductiblePrice}}
        try:
            dictionary['DamagePrice']=DamageLossCoverage
        except Exception as e:
            pass
    return dictionary


# 处理 入口数据
def sum_up_info(info):
    companyId = info['companyName']
    ownerName = info['ownerName']  # 车主姓名
    ownerId   = info['idCard']  # 身份证号
    # certType = ''#预留 接口里暂时没有
    phoneNo   = info['contact']
    if not phoneNo:
        if len(phoneNo) != 11:
            phoneNo = '13987654321'  # 手机号
    else:
        phoneNo = '13987654321'
    plateNo        = info['licenseNumber']  # 车牌号x
    engineNo       = info['motorNum']  # 发动机号
    vehicleFrameNo = info['vin']  # 车架号
    firstRegist    = info['initialDate'].strftime('%Y-%m-%d')  # 初等日期
    compStartTime  = info['forceInsuranceStartTime']  # 交强险起期
    if (datetime.datetime.now()-compStartTime).days > -1:     # 校验起期 日期
        compStartTime = datetime.datetime.now()+timedelta(days=1)
    commStartTime = info['insuranceStartTime']  # 商业险起期
    if (datetime.datetime.now()-commStartTime).days > -1:      # 校验起期 日期
        commStartTime = datetime.datetime.now()+timedelta(days=1)
    beginTime_comp = '{}'.format(compStartTime.strftime('%Y-%m-%d'))  # 交强险起期
    beginTime_comm = '{}'.format(commStartTime.strftime('%Y-%m-%d'))  # 商业险起期
    certType   = '身份证'
    inquiryInfo    = {
        'ownerInfo':
            {'ownerName': ownerName,
             'ownerId': ownerId,
             'certType': certType,
             'phoneNo': phoneNo},
        'carInfo':
            {'plateNo': plateNo,
             'engineNo': engineNo,
             'vehicleFrameNo': vehicleFrameNo,
             'firstRegist': firstRegist},
        'insuranceInfo':
            {'commInfo': {'beginTime': beginTime_comm},
             'compInfo': {'beginTime': beginTime_comp},
             },
    }
    for insur in insuranceList:
        inquiryInfo['insuranceInfo']['commInfo'][insur] = info[insur]
    return inquiryInfo

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
    def transfer(self):
        self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/a/img').click()
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'width-2')))
            time.sleep(1)
            self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/a/img').click()
            return True
        except Exception:
            return False

    # 回到主界面
    def back_to_main(self):
        self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/common/index.html')

    # 填写信息
    def fill_in_blanks(self, infos):
        print('filling in blanks')
        plate = self.driver.find_element_by_xpath(r'//*[@id="plateNo"]')
        plate.clear()
        plate.send_keys(infos['carInfo']['plateNo'])  # 车牌号
        vinNo = infos['carInfo']['vehicleFrameNo']
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'modelType')))
        for i in vinNo:
            vinInput = self.driver.find_element_by_xpath(r'//*[@id="carVIN"]')
            vinInput.send_keys(i)  # 车架号
            self.driver.find_element_by_xpath(r'//*[@id="engineNo"]').click()
        self.driver.find_element_by_xpath(r'//*[@id="engineNo"]').send_keys(infos['carInfo']['engineNo'])  # 发动机号
        self.driver.find_element_by_xpath(r'//*[@id="stRegisterDate"]').send_keys(infos['carInfo']['firstRegist'])  # 初等日期
        self.driver.find_element_by_xpath(r'//*[@id="VINSearch"]').click()
        # Vin码查询
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="carTypeTable"]/tbody/tr[1]/td[2]')))
        carInfo = self.driver.find_element_by_xpath(r'//*[@id="carTypeTable"]/tbody/tr').text
        print(carInfo)
        chairs_reg = re.compile('/(\w+)座')
        chairs = int(re.findall(chairs_reg, carInfo)[0])
        self.driver.find_element_by_xpath(r'//*[@id="carTypeTable"]/tbody/tr[1]/td[1]/input').click()
        self.driver.find_element_by_xpath(r'//*[@id="carTypeDialog"]/div[2]/div[2]/a[1]').click()
        # 以上退出了vin码查询页面
        # 以下开始选座位用途
        type_selector = Select(self.driver.find_element_by_id('vehicleType'))
        usage_selector = Select(self.driver.find_element_by_id('vehiclePurpose'))
        if chairs < 6:
            car_type = '6座以下客车'
            car_usage = '9座以下客车'
        elif 6 <= chairs < 10:
            car_type = '6座及10座以下客车'
            car_usage = '9座以下客车'
        elif 10 <= chairs < 20:
            car_type = '10座及20座以下客车'
            car_usage = '10座以上客车'
        elif 20 <= chairs < 36:
            car_type = '20座及36座以下客车'
            car_usage = '10座以上客车'
        elif chairs >= 36:
            car_type = '36座及36座以下客车'
            car_usage = '10座以上客车'
        # 根据车类型 来选择
        type_selector.select_by_visible_text(car_type)  # 证件类型
        time.sleep(1)
        usage_selector.select_by_visible_text(car_usage)  # 证件类型
        # 车主信息填写
        self.driver.find_element_by_xpath(r'//*[@id="ecarvoForm"]/div[1]/div[26]/input').send_keys(
            infos['ownerInfo']['ownerName'])  # 车主姓名
        s1 = Select(self.driver.find_element_by_id('certType'))
        s1.select_by_visible_text(infos['ownerInfo']['certType'])  # 证件类型
        self.driver.find_element_by_xpath(r'//*[@id="certNo"]').send_keys(infos['ownerInfo']['ownerId'])  # 证件号码
        compDate = self.driver.find_element_by_xpath(r'//*[@id="compulsoryStartDate"]')  # 交强险起期
        compDate.clear()
        compDate.send_keys('{} 00:00'.format(infos['insuranceInfo']['compInfo']['beginTime']))
        commDate = self.driver.find_element_by_xpath(r'//*[@id="commercialStartDate"]')  # 商业险起期
        commDate.clear()
        commDate.send_keys('{} 00:00'.format(infos['insuranceInfo']['commInfo']['beginTime']))
        return carInfo

    # 填写保险信息
    def fill_in_insurance_info(self, infos):
        print('fill_in_insurance_info')
        time.sleep(1)
        commDate = self.driver.find_element_by_xpath(r'//*[@id="commercialStartDate"]')  # 商业险起期
        commDate.clear()
        commDate.send_keys('{} 00:00'.format(infos['insuranceInfo']['commInfo']['beginTime']))
        self.driver.find_element_by_xpath('//*[@id="compulsoryInput"]').click()
        self.driver.find_element_by_xpath('//*[@id="compulsoryInput"]').click()
        compDate = self.driver.find_element_by_xpath(r'//*[@id="compulsoryStartDate"]')  # 交强险起期
        compDate.clear()
        compDate.send_keys('{} 00:00'.format(infos['insuranceInfo']['compInfo']['beginTime']))
        # 调整页面位置
        locate = self.driver.find_element_by_xpath(r'//*[@id="rate"]')
        locate.send_keys(Keys.TAB)
        locate.send_keys(Keys.TAB)
        # ===============================================交强险入口勾选情况
        if infos['insuranceInfo']['commInfo']['jiaoqiangInsurance']['baoe'] == '不投保':
            self.driver.find_element_by_xpath('//*[@id="compulsoryInput"]').click()
        # ===============================================车辆损失险
        CheSun = infos['insuranceInfo']['commInfo']['chesuanInsurance']
        if CheSun['baoe'] == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox3"]').click()  # 勾选车损
            if CheSun['insuranceType'] == 0:
                # 取消 不计免赔 的勾
                self.driver.find_element_by_xpath(r'//*[@id="checkbox4"]').click()
        # ===============================================第三方
        DiSanFang = infos['insuranceInfo']['commInfo']['disanfangInsurance']
        if DiSanFang['baoe'] != '不投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox5"]').click()  # 勾选三者险
            selector = Select(self.driver.find_element_by_id('thirdInsuranceAmount'))
            selector.select_by_visible_text(DiSanFang['baoe'])  # 保额选择
            if DiSanFang['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox6"]').click()  # 取消 不计免赔 的勾
        # ===============================================全车盗抢
        QiangDao = infos['insuranceInfo']['commInfo']['chedaoInsurance']
        if QiangDao['baoe'] == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox10"]').click()  # 勾选抢盗险
            if QiangDao['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox11"]').click()  # 取消 不计免赔勾选
        # ===============================================司机座位责任险
        SiJi = infos['insuranceInfo']['commInfo']['sijiInsurance']
        if SiJi['baoe'] != '不投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox7"]').click()  # 勾选司机险
            sijiValue = self.driver.find_element_by_xpath(r'//*[@id="pLI"]')
            if SiJi['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox77"]').click()  # 取消 不计免赔勾选
            sijiValue.click()
            for i in range(10):
                sijiValue.send_keys(Keys.BACK_SPACE)
            sijiValue.send_keys(SiJi['baoe'])
        # ===============================================乘客座位责任险
        ChengKe = infos['insuranceInfo']['commInfo']['chenkeInsurance']
        if ChengKe['baoe'] != '不投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox8"]').click()  # 勾选乘客险
            if ChengKe['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox88"]').click()  # 取消 不计免赔勾选
            chengkeValue = self.driver.find_element_by_xpath(r'//*[@id="seatPrice"]')
            for i in range(10):
                chengkeValue.send_keys(Keys.BACK_SPACE)
            chengkeValue.send_keys(ChengKe['baoe'])
        # ===============================================# ===============================================
        self.driver.find_element_by_xpath('//*[@id="rate"]').send_keys(Keys.TAB)  # 用TAB来控制页面下拉
        # ===============================================# ===============================================
        # ===============================================玻璃单独破碎险
        BoLi = infos['insuranceInfo']['commInfo']['boliInsurance']
        if BoLi['baoe'] != '不投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox12"]').click()  # 勾选 玻璃单独破碎险
            selector = Select(self.driver.find_element_by_id('locality'))
            selector.select_by_visible_text(BoLi['baoe'])  # 玻璃选择
        # ===============================================车身划痕损失险
        HuaHen = infos['insuranceInfo']['commInfo']['huahenInsurance']
        if HuaHen['baoe'] != '不投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox16"]').click()  # 勾选 车身划痕损失险
            selector = Select(self.driver.find_element_by_xpath('//*[@id="quoteInsuranceTable"]/tbody/tr[9]/td[3]/select'))
            selector.select_by_visible_text(HuaHen['baoe'])  # 车身划痕损失险 选择
            if HuaHen['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox17"]').click()  # 取消 不计免赔勾选
        # ===============================================自燃损失险
        ZiRan = infos['insuranceInfo']['commInfo']['ziranInsurance']
        if ZiRan['baoe'] == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox14"]').click()  # 勾选 自燃损失险
            if ZiRan['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox15"]').click()  # 取消 不计免赔勾选
        # ===============================================发动机涉水损失险
        SheShui = infos['insuranceInfo']['commInfo']['fadongjiInsurance']
        if SheShui['baoe'] == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox18"]').click()  # 勾选 发动机涉水损失险
            if SheShui['insuranceType'] == 0:
                self.driver.find_element_by_xpath(r'//*[@id="checkbox19"]').click()  # 取消 不计免赔勾选
        # ===============================================指定专修厂特约条款
        ZhuanXiu = infos['insuranceInfo']['commInfo']['zhuanxiuInsurance']
        if ZhuanXiu['baoe'] == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox28"]').click()  # 勾选 发动机涉水损失险
            rateInput = self.driver.find_element_by_xpath(r'//*[@id="rate"]')
            rateInput.clear()
            rateInput.send_keys('0.3')
        # ===============================================无法找到第三方特约险
        TeYue = infos['insuranceInfo']['commInfo']['teyueInsurance']
        if TeYue['baoe'] == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="checkbox30"]').click()  # 勾选 无法找到第三方特约险
        print('doing error dict')
        return True

    # 报价
    def calculate_price(self, carInfo):
        error_dict = {}
        print('calculate_price')
        self.driver.find_element_by_xpath(r'//*[@id="premiumTrial"]/img').click()
        time.sleep(3)
        while True:
            PageContent = self.driver.page_source
            if '提示信息' and '所选车型不一致' in PageContent:
                print('提示信息')
                error_reg = re.compile('平台对应车型代码有：(.*?)</div>')
                car_id = re.findall(error_reg, PageContent)[0].split('、')[0]
                cookieList = self.driver.get_cookies()
                cookie = processCookie(cookie_list=cookieList)
                response = car_model_query(targetID=car_id, carInfos=carInfo, cookie=cookie)
                try:
                    self.driver.find_element_by_xpath(r'/html/body/div[21]/div[2]/div[2]/a').click()
                except Exception as e:
                    print('提示信息错误\n', e)
                if response['code'] == 1:
                    self.driver.find_element_by_xpath(r'/html/body/div[22]/div[2]/div[2]/a').click()
                    self.driver.find_element_by_xpath(r'//*[@id="plateNo"]').send_keys(Keys.TAB)
                    self.driver.find_element_by_xpath(r'//*[@id="modelType"]').click()
                    self.driver.find_element_by_xpath(r'//*[@id="modelType"]').send_keys(Keys.BACK_SPACE)
                    time.sleep(1)
                    xp = '//*[@id="ecarvoForm"]/div[1]/div[14]/div[2]/ul/li[{}]'.format(response['foundid'])
                    self.driver.find_element_by_xpath(xp).click()
                    print('信息修改成功，重新报价')
                    self.calculate_price(carInfo)
                else:
                    error_dict['status'] = 0
                    error_message = '找不到车型 {}'.format(error_message)
            elif '警示信息' in PageContent:
                print('警示信息')
                soup = BeautifulSoup(PageContent, 'lxml')
                if '商业险重复投保' in PageContent:
                    error_dict['status'] = 0
                    tag = soup.find_all('div')
                    error_dict['error_message'] = tag[-2].get_text()  # 预留的errormessage信息口子
                    self.driver.find_element_by_xpath(r'/html/body/div[20]/div[2]/div[2]/a').click()
                    return error_dict
                elif '请填写税务机关名称' in PageContent:
                    self.driver.find_element_by_xpath('/html/body/div[22]/div[2]/div[2]/a').click()
                    self.driver.find_element_by_xpath('//*[@id="taxBody"]/div[2]/form/div[2]/input').send_keys('国家税务总局四川省税务局')
                    self.calculate_price(carInfo)
                else:
                    error_dict['status'] = 0
                    error_dict['error_message'] = PageContent
                    return error_dict
            elif '错误信息' in PageContent:
                print('错误信息')
                error_dict['status'] = 0
                error_reg = re.compile('\[保费计算\]保费计算失败，错误信息为\[(.*)\]')
                error_dict['error_message'] = re.findall(error_reg, PageContent)[0]
                return error_dict
            else:
                print('all good')
                try:
                    self.driver.find_element_by_xpath(r'/html/body/div[22]/div[2]/div[2]/a').click()
                except Exception:
                    pass
                self.driver.find_element_by_xpath(r'//*[@id="temporary"]/img').click()
                code_reg = re.compile('<span id="billCode">(.*?)</span>')
                time.sleep(1)
                code = re.findall(code_reg, self.driver.page_source)
                #print(self.driver.page_source)
                if code:
                    error_dict['status'] = 1
                    error_dict['code'] = code[0]
                    error_dict['error_message'] = '询价成功'
                else:
                    error_dict['status'] = 0
                    error_dict['error_message'] = '没有查到单号'
                return error_dict

    # 关闭引擎
    def close_mission(self):
        self.driver.close()

    # 查询保险详细信息
    def get_insur_info(self, order_id, cookie):
        payload = {"meta": {}, "redata": {"quotationNo": "{}".format(order_id)}}
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.8',
                   'Connection': 'keep-alive',
                   'Content-Length': '59',
                   'Content-Type': 'application/json;charset=UTF-8',
                   'Cookie': cookie,
                   'Host': 'issue.cpic.com.cn',
                   'Origin': 'http://issue.cpic.com.cn',
                   'Referer': 'http://issue.cpic.com.cn/ecar/view/portal/page/quick_quotation/quick_quotation.html',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
                   'X-Requested-With': 'XMLHttpRequest'}
        response = requests.post(r'http://issue.cpic.com.cn/ecar/quickoffer/queryQuickOffer', data=json.dumps(payload),
                                 headers=headers)
        try:
            response = response.json()
        except Exception as e:
            response = {"message": {"code": "falied", "message": "", "status": ""}}
        quotesInfo = {}
        dictionary = {}
        if response['message']['code'] == 'success':
            print(response)
            # 车信息
            carInfo = response['result']['ecarvo']
            quotesInfo['carInfo'] = {}
            quotesInfo['carInfo']['carVIN'] = carInfo['carVIN']  # 车架号
            quotesInfo['carInfo']['certNo'] = carInfo['certNo']  # 证件号
            quotesInfo['carInfo']['engineNo'] = carInfo['engineNo']  # 发动机号
            quotesInfo['carInfo']['factoryType'] = carInfo['factoryType']  # 厂牌型号
            quotesInfo['carInfo']['stRegisterDate'] = carInfo['stRegisterDate']  # 初登日期
            # quotesInfo['carInfo']['phoneNo'] = carInfo['phoneNo']#车主手机号码
            quotesInfo['carInfo']['plateNo'] = carInfo['plateNo']  # 车牌号
            quotesInfo['carInfo']['ownerName'] = carInfo['ownerName']  # 车主姓名
            quotesInfo['carInfo']['plateColor'] = plateInfo[int(carInfo['plateColor'])]  # 号牌种类
            quotesInfo['carInfo']['emptyWeight'] = carInfo['emptyWeight']  # 核定载质量
            quotesInfo['carInfo']['usage'] = carInfo['usage']  # 使用性质 0非营运 1营运
            quotesInfo['carInfo']['isTrade'] = 0  # 是否过户 预留字段
            if response['result']['commercial']:  # 商业险
                commInfo = response['result']['commercialInsuransVo']
                quotesInfo['commercialInsuransVo'] = {}
                quotesInfo['commercialInsuransVo']['nonClaimDiscountRate'] = commInfo['nonClaimDiscountRate']  # 无赔偿折扣系数
                quotesInfo['commercialInsuransVo']['trafficTransgressRate'] = commInfo[
                    'trafficTransgressRate']  # 交通违法系数
                quotesInfo['commercialInsuransVo']['comm_underwritingRate'] = commInfo['underwritingRate']  # 自主核保系数
                quotesInfo['commercialInsuransVo']['comm_channelRate'] = commInfo['channelRate']  # 自主渠道系数
                quotesInfo['commercialInsuransVo']['stStartDate'] = commInfo['stStartDate']  # 起保时间
                quotesInfo['commercialInsuransVo']['stEndDate'] = commInfo['stEndDate']  # 终保时间
                quotesInfo['commercialInsuransVo']['comm_ecompensationRate'] = commInfo['ecompensationRate']  # 预期赔付率
                quotesInfo['commercialInsuransVo']['comm_insuranceQueryCode'] = commInfo[
                    'insuranceQueryCode']  # 商业险 投保查询码
                quotesInfo['commercialInsuransVo']['comm_totalEcompensationRate'] = commInfo[
                    'totalEcompensationRate']  # 交商合计预期赔付率
                quotesInfo['commercialInsuransVo']['comm_standardPremium'] = commInfo['standardPremium']  # 标准保费
                quotesInfo['commercialInsuransVo']['premium'] = commInfo['premium']  # 折后保费
                quotesInfo['commercialInsuransVo']['comm_premiumRatio'] = commInfo['premiumRatio']  # 折扣率
            if response['result']['compulsory']:  # 交强险
                compInfo = response['result']['compulsoryInsuransVo']
                quotesInfo['compulsoryInsuransVo'] = {}
                quotesInfo['compulsoryInsuransVo']['comp_ecompensationRate'] = compInfo['ecompensationRate']  # 预期赔付率
                quotesInfo['compulsoryInsuransVo']['comp_insuranceQueryCode'] = compInfo['insuranceQueryCode']  # 投保查询码
                quotesInfo['compulsoryInsuransVo']['comp_payableAmount'] = compInfo['payableAmount']  # 当年应缴
                quotesInfo['compulsoryInsuransVo']['comp_registryNumber'] = compInfo['registryNumber']  # 税务登记号
                quotesInfo['compulsoryInsuransVo']['comp_standardPremium'] = compInfo['standardPremium']  # 交强险保费
                quotesInfo['compulsoryInsuransVo']['comp_taxAmount'] = compInfo['taxAmount']  # 车船税保费
                quotesInfo['compulsoryInsuransVo']['comp_totalPremium'] = compInfo['totalPremium']  # 交强险总计费用
                quotesInfo['compulsoryInsuransVo']['comp_taxpayerName'] = compInfo['taxpayerName']  # 纳税人名
                quotesInfo['compulsoryInsuransVo']['comp_taxpayerNo'] = compInfo['taxpayerNo']  # 身份证号
            commDetail = response['result']['quoteInsuranceVos']
            sumPrice = response['result']['totalPremium']
            nonDeductible = []
            nonDeductiblePrice = 0
            for quote in commDetail:
                insurName = quote['insuranceCode']
                if 'DAMAGELOSSCOVERAGE' == insurName:
                    DamageLossCoverage = quote['stAmount']
                if insurName in officialList:
                    # 名字 = 折后价
                    quotesInfo['commercialInsuransVo'][insurName] = {'premium': quote['premium']}
                    if 'nonDeductible' in quote:
                        nonDeductible.append(officialList[insurName]['nickname'])
                        nonDeductiblePrice += quote['nonDeductible']
                        # print(nonDeductiblePrice)
            dictionary = {'codeNo': order_id,
                          'sumPrice': sumPrice,
                          'quotesInfo': quotesInfo,
                          'nonDeductible': {'name': '、'.join(nonDeductible), 'value': nonDeductiblePrice}}
            try:
                dictionary['DamagePrice'] = DamageLossCoverage
            except Exception as e:
                pass
        return dictionary


def sum_job():
    crewer = TaiPingYangCrew()#wbdriver='Chrome'
    crewer.login()  # 登录
    time_count = 0
    while True:
        if crewer.check_login():
            info = MysqlUsage.get_one_piece_query()  # 从库里取一条数据出来
            try:
                if info:
                    write_down_error(str(info))  # 日志记录
                    try:
                        crewer.transfer()  # 跳转
                    except NoSuchElementException:
                        crewer.close_mission()
                    processed_info = sum_up_info(info)
                    time.sleep(2)
                    car_info = crewer.fill_in_blanks(infos=processed_info)  # 填车辆信息
                    crewer.fill_in_insurance_info(infos=processed_info)  # 保险信息
                    order_info = crewer.calculate_price(carInfo=car_info,)  # 点击计算按钮
                    print(order_info)
                    if order_info['status'] == 1:
                        cookieList = crewer.get_now_cookies()
                        cookie = processCookie(cookie_list=cookieList)
                        res_dictionary = get_accident_product_info(order_id=order_info['code'], cookie=cookie)  # 爬到的保单信息
                        reptileDict = sum_up_response(inquiryInfo=info, error_message=order_info['error_message'],res_dictionary=res_dictionary)
                        reptileDict['ownerContact'] = info['ownerContact']
                        reptileDict['caseName'] = info['planName']  # 方案名称
                        MysqlUsage.update_inquiry_success_count(quiryId=info['inquiryId'])
                        MysqlUsage.insert_success_reptile(reptileDict)
                    elif order_info['status'] == 0:
                        reptileDict = {'id': info['id'],
                                       'inquiryId': info['inquiryId'],
                                       'isRenewal': info['isRenewal'],
                                       'cityName': info['cityName'],
                                       'licenseNumber': info['licenseNumber'],
                                       'ownerName': info['ownerName'],
                                       'idCard': info['idCard'],
                                       'vin': info['vin'],
                                       'motorNum': info['motorNum'],
                                       'caseName': info['planName'],
                                       'state': 2,
                                       'createTime': datetime.datetime.now(),
                                       'updateTime': datetime.datetime.now(),
                                       'initialDate': info['initialDate'],
                                       'ownerContact': info['ownerContact'],
                                       'company': info['companyName'],
                                       'message': order_info['error_message'],
                                       }
                        MysqlUsage.update_inquiry_error_count(quiryId=info['inquiryId'])
                        MysqlUsage.insert_failed_reptile(reptileDict)
                else:
                    print('no valid info')
                    time.sleep(10)
                    time_count += 10
                    if time_count / 60 == 15:
                        write_down_error('心跳反应')
                        time_count = 0
            except Exception as e:
                write_down_error(str(e))
                crewer.driver.save_screenshot('error pic{}.png'.format(str(datetime.datetime.now())))
                input('')
        else:
            break
        input('next')
if __name__ == '__main__':
    sum_job()
