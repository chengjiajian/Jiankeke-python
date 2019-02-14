# -*- coding: utf-8 -*-
from selenium import webdriver
from datetime import timedelta
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
import re
from selenium.webdriver.support import expected_conditions as EC
import datetime
import pymysql
import contextlib
import json
from selenium.common.exceptions import *
from PIL import Image
import base64
import requests


@contextlib.contextmanager
def mysql(host='121.40.207.59', port=3306, user='root', passwd='MmlAN8kX', db='ggcx', charset='utf8'):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


class MysqlUsage:
    def __init__(self):
        pass

    # 获取input里单条数据
    @classmethod
    def get_one_piece(cls):
        insuranceList = ['chesuanInsurance',  # 车损
                         'disanfangInsurance',  # 第三方
                         'chedaoInsurance',  # 全车盗抢
                         'sijiInsurance',  # 司机座位责任险
                         'chenkeInsurance',  # 乘客座位责任险
                         'boliInsurance',  # 玻璃单独破碎险
                         'huahenInsurance',  # 车身划痕损失险
                         'ziranInsurance',  # 自燃损失险
                         'fadongjiInsurance',  # 发动机涉水损失险
                         'zhuanxiuInsurance',  # 指定专修厂特约条款
                         'teyueInsurance',  # 无法找到第三方特约险
                         'jiaoqiangInsurance',  # 交强险
                         'chechuanInsurance']  # 车船税
        with mysql() as cursor:
            sql_content = "SELECT * from inquiry_input WHERE state=0 and companyName='平安保险' ORDER BY createTime LIMIT 1"
            c = cursor.execute(sql_content)
            infos = cursor.fetchall()
            if infos:
                infos = infos[0]
                update_input_state = "UPDATE inquiry_input SET state=1 WHERE id='{}'".format(infos['id'])  # 把表内状态改为1
                update_waitcount = "UPDATE inquiry SET waitCount=waitCount+1 WHERE quiryId='{}'".format(infos['inquiryId'])  # 把主表里的等待状态 + 1
                c = cursor.execute(update_input_state)
                c = cursor.execute(update_waitcount)
                for insur in insuranceList:
                    if infos[insur]:
                        stredInfo = re.sub('”|“', '"', infos[insur])
                        infos[insur] = eval(stredInfo)
        return infos

    # update 失败数量
    @classmethod
    def update_inquiry_error_count(cls, quiryId):
        with mysql() as cursor:
            sql_content = "UPDATE inquiry SET waitCount=waitCount-1,errorCount=errorCount+1 WHERE quiryId='{}'".format(quiryId)
            c = cursor.execute(sql_content)

    # update 成功数量
    @classmethod
    def update_inquiry_success_count(cls, quiryId):
        with mysql() as cursor:
            sql_content = "UPDATE inquiry SET waitCount=waitCount-1,successCount=successCount+1,state=1 WHERE quiryId='{}'".format(quiryId)
            c = cursor.execute(sql_content)

    # 插库成功 条
    @classmethod
    def insert_success_reptile(cls, reptile_dict):
        with mysql() as cursor:
            c = cursor.execute("INSERT INTO inquiry_reptile(inquiryInputId,inquiryId,isRenewal,cityName,licenseNumber,ownerName,idCard,carTypeCode,approvedLoadQuality,operation,households,chesuanInsurancePrice,disanfangInsurancePrice,chedaoInsurancePrice,sijiInsurancePrice,chenkeInsurancePrice,boliInsurancePrice,huahenInsurancePrice,ziranInsurancePrice,fadongjiInsurancePrice,zhuanxiuInsurancePrice,teyueInsurancePrice,jiaoqiangInsurancePrice,chechuanInsurancePrice,insuranceCompanyId,quotesPrice,insuranceCompanyNametwo,policyNo,quotesPricetwo,insurancePrice,vin,motorNum,labeltype,caseName,insurances,state,createTime,updateTime,initialDate,ownerContact,company,companyEndDate,insuranceCompanyNameOne,policyOneNo,insuranceCompanyOneStartDate,insuranceCompanyOneEndDate,insuranceCompanyTwoStartDate,insuranceCompanyTwoEndDate,message,rate,chesuanInsuranceBaoe,bujimianpeiName,bujimianpeiPrice,manageCoefNum,illegalCoefNum,selfChannelNum,selfUnderNum,allMessage) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                reptile_dict['id'],
                reptile_dict['inquiryId'],
                reptile_dict['isRenewal'],
                reptile_dict['cityName'],
                reptile_dict['licenseNumber'],
                reptile_dict['ownerName'],
                reptile_dict['idCard'],
                reptile_dict['carTypeCode'],
                reptile_dict['approvedLoadQuality'],
                reptile_dict['operation'],
                reptile_dict['households'],
                reptile_dict['chesuanInsurancePrice'],
                reptile_dict['disanfangInsurancePrice'],
                reptile_dict['chedaoInsurancePrice'],
                reptile_dict['sijiInsurancePrice'],
                reptile_dict['chenkeInsurancePrice'],
                reptile_dict['boliInsurancePrice'],
                reptile_dict['huahenInsurancePrice'],
                reptile_dict['ziranInsurancePrice'],
                reptile_dict['fadongjiInsurancePrice'],
                reptile_dict['zhuanxiuInsurancePrice'],
                reptile_dict['teyueInsurancePrice'],
                reptile_dict['jiaoqiangInsurancePrice'],
                reptile_dict['chechuanInsurancePrice'],
                reptile_dict['insuranceCompanyId'],
                reptile_dict['quotesPrice'],
                reptile_dict['insuranceCompanyNametwo'],
                reptile_dict['policyNo'],
                reptile_dict['quotesPricetwo'],
                reptile_dict['insurancePrice'],
                reptile_dict['vin'],
                reptile_dict['motorNum'],
                reptile_dict['labeltype'],
                reptile_dict['caseName'],
                reptile_dict['insurances'],
                reptile_dict['state'],
                reptile_dict['createTime'],
                reptile_dict['updateTime'],
                reptile_dict['initialDate'],
                reptile_dict['ownerContact'],
                reptile_dict['company'],
                reptile_dict['companyEndDate'],
                reptile_dict['insuranceCompanyNameOne'],
                reptile_dict['policyOneNo'],
                reptile_dict['insuranceCompanyOneStartDate'],
                reptile_dict['insuranceCompanyOneEndDate'],
                reptile_dict['insuranceCompanyTwoStartDate'],
                reptile_dict['insuranceCompanyTwoEndDate'],
                '询价成功',
                reptile_dict['rate'],
                reptile_dict['chesuanInsuranceBaoe'],
                reptile_dict['bujimianpeiName'],
                reptile_dict['bujimianpeiPrice'],
                reptile_dict['manageCoefNum'],
                reptile_dict['illegalCoefNum'],
                reptile_dict['selfChannelNum'],
                reptile_dict['selfUnderNum'],
                reptile_dict['message']
            ))

    # 插库失败 条
    @classmethod
    def insert_failed_reptile(cls, reptile_dict):
        with mysql() as cursor:
            c = cursor.execute("INSERT INTO inquiry_reptile(inquiryInputId,inquiryId,isRenewal,cityName,licenseNumber,ownerName,idCard,vin,motorNum,caseName,state,createTime,updateTime,initialDate,ownerContact,company,message,allMessage) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
                reptile_dict['id'],
                reptile_dict['inquiryId'],
                reptile_dict['isRenewal'],
                reptile_dict['cityName'],
                reptile_dict['licenseNumber'],
                reptile_dict['ownerName'],
                reptile_dict['idCard'],
                reptile_dict['vin'],
                reptile_dict['motorNum'],
                reptile_dict['caseName'],
                reptile_dict['state'],
                reptile_dict['createTime'],
                reptile_dict['updateTime'],
                reptile_dict['initialDate'],
                reptile_dict['ownerContact'],
                reptile_dict['company'],
                reptile_dict['message'],
                '询价失败'
            ))


# 验证码接口
def dpi_request(path, code_type=1004):
    try:
        print('接口调用成功')
        with open(path,'rb') as s:
            ls_f = base64.b64encode(s.read())  # 读取文件内容，转换为base64编码
            #print(ls_f)

            params = {
                "key": '889fdc9bc1d1e5e678e52623b23c1f7a',  # 您申请到的APPKEY
                "codeType": code_type,
            # 验证码的类型，&lt;a href=&quot;http://www.juhe.cn/docs/api/id/60/aid/352&quot; target=&quot;_blank&quot;&gt;查询&lt;/a&gt;
                "base64Str": ls_f,  # 图片文件
                "dtype": "",  # 返回的数据的格式，json或xml，默认为json

            }
            #print(params)
            #input('')
            # with open (r'C:\Users\ASUS\Desktop\x.txt','wb+') as f:
            #     f.write(ls_f)
        url = "http://op.juhe.cn/vercode/index"
        f = requests.post(url=url, data=params, timeout=120)
        res = f.json()
        print('res',res)
        if res:
            error_code = res["error_code"]
            if error_code == 0:
                # 成功请求
                print(res["result"])
            else:
                print("%s:%s" % (res["error_code"], res["reason"]))
        else:
            print("request api error")
        return res["result"]
    except Exception as e:
        return dpi_request(path)


# 验证码校验
def crop_valid_code(save_path, driver, image_element):
    driver.save_screenshot(save_path)
    location = image_element.location  # 获取验证码x,y轴坐标
    size = image_element.size  # 获取验证码的长宽
    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
    i = Image.open(save_path)  # 打开截图
    frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save(save_path)  # 保存接下来的验证码图片 进行打码
    validcode_num = dpi_request(save_path)
    return validcode_num


# 记录错误信息的方法
def write_down_error(message):
    with open('errorMessage.txt', 'a', encoding='utf-8') as fn:
        fn.write('{} \n {} \n ==============================================='.format(datetime.datetime.now(), message))


# 处理 入口数据
def sum_up_info(info):
    insuranceList = ['chesuanInsurance',  # 车损
                     'disanfangInsurance',  # 第三方
                     'chedaoInsurance',  # 全车盗抢
                     'sijiInsurance',  # 司机座位责任险
                     'chenkeInsurance',  # 乘客座位责任险
                     'boliInsurance',  # 玻璃单独破碎险
                     'huahenInsurance',  # 车身划痕损失险
                     'ziranInsurance',  # 自燃损失险
                     'fadongjiInsurance',  # 发动机涉水损失险
                     'zhuanxiuInsurance',  # 指定专修厂特约条款
                     'teyueInsurance',  # 无法找到第三方特约险
                     'jiaoqiangInsurance',  # 交强险
                     'chechuanInsurance']  # 车船税
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


# 处理 出口数据
def sum_up_response(res_dictionary, inquiry_info, error_message):
    nonDeduct_name_list = []
    nonDeduct_price_sum = 0
    # 不计免赔类
    pingan_nonDeductible = {'CV27027': '车损',  # 不计免赔
                            'CV31028': '三者',  # 不计免赔
                            'CV60079': '发动机涉水',  # 不计免赔
                            'CV44049': '司机',  # 不计免赔
                            'CV44080': '乘客',  # 不计免赔
                            'CV41048': '盗抢',  # 不计免赔
                            'CV58077': '自燃',  # 不计免赔
                            'CV56075': '划痕',  # 不计免赔
                            }
    # 普通险种类
    pingan_insurance_info_dictionary = {'F30': 'manageCoefNum',  # 无赔款折扣系数
                                        'F34': 'illegalCoefNum',  # 交通违法系数
                                        'F74': 'selfChannelNum',  # 自主渠道系数
                                        'F76': 'selfUnderNum',  # 自主核保系数
                                        'F999': 'rate',  # 合计折扣 (折扣率)
                                        'CV01001': 'chesuanInsurancePrice',  # 车辆损失险额
                                        'CV05002': 'disanfangInsurancePrice',  # 第三者责任险额
                                        'CV09003': 'chedaoInsurancePrice',  # 全车盗抢险额
                                        'CV13004': 'sijiInsurancePrice',  # 司机座位责任险额
                                        'CV17005': 'chenkeInsurancePrice',  # 乘客座位责任险(4座)额
                                        'CV08000': 'boliInsurancePrice',  # 玻璃单独破碎险额
                                        'CV17000': 'huahenInsurancePrice',  # 车身划痕损失险额
                                        'CV18000': 'ziranInsurancePrice',  # 自燃损失险额
                                        'CV36041': 'fadongjiInsurancePrice',  # 发动机涉水损失险额
                                        'CV48057': 'zhuanxiuInsurancePrice',  # 指定专修厂特约条款额
                                        'CV49063': 'teyueInsurancePrice',  # 无法找到第三方特约险额
                                        }
    reptileDict = {}
    reptileDict['insurances'] = ''
    reptileDict['id'] = inquiry_info['id']
    reptileDict['inquiryId'] = inquiry_info['inquiryId']
    reptileDict['isRenewal'] = 0  # 没有续保情况时候默认为0
    reptileDict['cityName'] = inquiry_info['cityName']  # '四川'  # 没有筛选情况下默认为四川
    base_info = res_dictionary['voucherDetailList'][0]
    insur_info = base_info['voucher']
    # 商业险
    if 'c01DutyList' in insur_info:
        # 基础信息 + 折扣信息
        comm_base_info = insur_info['c01BaseInfo']
        # 折扣率信息
        discount_infos = insur_info['c01DisplayRateFactorList']
        for discount_info in discount_infos:
            if discount_info['factorCode'] in pingan_insurance_info_dictionary:
                sql_column_name = pingan_insurance_info_dictionary[discount_info['factorCode']]
                reptileDict[sql_column_name] = discount_info['factorRatioCOM']
        # =====================================================================================================
        comm_info_list = insur_info['c01DutyList']
        # 商业险 详细信息
        reptileDict['insuranceCompanyNameOne'] = '平安保险'  # 商业险投保公司
        reptileDict['policyOneNo'] = base_info['c01CircInfoDTO']['thirdVehicleInfoDTO']['applyQueryCode']  # 商业险保单号
        reptileDict['insuranceCompanyOneStartDate'] = comm_base_info['insuranceBeginTime']  # 商业险起始日期
        reptileDict['insuranceCompanyOneEndDate'] = comm_base_info['insuranceEndTime']  # 商业险截止日期
        reptileDict['insurancePrice'] = comm_base_info['totalActualPremium']  # 商业险保费

        # 遍历险种列表，转换成数据库格式
        for comm_info in comm_info_list:
            code = comm_info['dutyCode']
            if code in pingan_insurance_info_dictionary:
                if code == 'CV01001':
                    reptileDict['chesuanInsuranceBaoe'] = comm_info['insuredAmount']
                sql_column_name = pingan_insurance_info_dictionary[code]
                reptileDict[sql_column_name] = comm_info['totalActualPremium']
            elif code in pingan_nonDeductible:
                nonDeduct_name_list.append(pingan_nonDeductible[code])
                nonDeduct_price_sum += comm_info['totalActualPremium']
        # 不计免赔信息
        reptileDict['bujimianpeiName'] = '、'.join(nonDeduct_name_list)  # 不计免赔险名
        reptileDict['bujimianpeiPrice'] = nonDeduct_price_sum  # 不计免赔保费
    # 交强险详细
    if 'c51BaseInfo' in insur_info:
        comp_info = insur_info['c51BaseInfo']
        reptileDict['insuranceCompanyNametwo'] = '平安保险'  # 交强险投保公司
        reptileDict['policyNo'] = base_info['c51CircInfoDTO']['thirdVehicleInfoDTO']['applyQueryCode']  # 交强险保单号
        reptileDict['insuranceCompanyTwoStartDate'] = comp_info['insuranceBeginTime']  # 交强险起始日期
        reptileDict['insuranceCompanyTwoEndDate'] = comp_info['insuranceEndTime']  # 交强险截止日期
        reptileDict['jiaoqiangInsurancePrice'] = comp_info['totalActualPremium']  # 交强险额
        reptileDict['chechuanInsurancePrice'] = insur_info['vehicleTaxInfo']['totalTaxMoney']  # 车船税额
        reptileDict['quotesPricetwo'] = float(reptileDict['jiaoqiangInsurancePrice']) + \
                                        float(reptileDict['chechuanInsurancePrice'])  # 强制险出单费
    # 车信息==================================================================================
    car_info = insur_info['vehicleTarget']
    if car_info:
        reptileDict['vin'] = car_info['vehicleFrameNo']  # 车架号
        reptileDict['motorNum'] = car_info['engineNo']  # 发动机号
        reptileDict['labeltype'] = car_info['circVehicleModel']  # 厂牌型号
        reptileDict['initialDate'] = car_info['firstRegisterDate']  # 初登日期
        reptileDict['licenseNumber'] = car_info['vehicleLicenceCode'].replace('-', '')  # 车牌号
        reptileDict['carTypeCode'] = car_info['licenceTypeCode']  # carInfo['plateColor']  # 号牌种类
        reptileDict['approvedLoadQuality'] = ''  # car_info['emptyWeight']  # 核定载质量
        reptileDict['operation'] = 0 if car_info['usageAttributeName'] == '非营业' else 1  # 使用性质 0非营运 1营运
        reptileDict['households'] = car_info['loanVehicleFlag']  # 是否过户  !!!还有歧义!!!
    # 表单信息==================================================================================
    reptileDict['insuranceCompanyId'] = insur_info['quotationNo']  # 保单号
    reptileDict['quotesPrice'] = insur_info['totalAmount']  # 保费
    reptileDict['state'] = 1  # 1成功；2失败；3等待
    reptileDict['createTime'] = res_dictionary['aplylicantInfoList'][0]['createdDate']  # 创建时间
    reptileDict['updateTime'] = str(datetime.datetime.now())  # 修改时间
    reptileDict['message'] = error_message  # 爬虫信息
    reptileDict['company'] = '平安'  # 保险公司
    reptileDict['companyEndDate'] = reptileDict['insuranceCompanyOneEndDate'] if reptileDict[
        'insuranceCompanyOneEndDate'] \
        else reptileDict['insuranceCompanyTwoEndDate']  # 保险到期日
    # 车主信息==================================================================================
    owner_info = insur_info['ownerDriver']
    if owner_info:
        reptileDict['ownerName'] = inquiry_info['ownerName']  # 车主姓名
        reptileDict['idCard'] = inquiry_info['idCard']  # 证件号码
        reptileDict['ownerContact'] = inquiry_info['ownerContact']  # carInfo['phoneNo']  # 车主手机号码
        reptileDict['caseName'] = inquiry_info['planName']  # 方案名称
    return reptileDict


# 主程序
class PingAnCrew:
    def __init__(self,wbdriver='PhantomJS'):
        suzhou_account = {'username': 'QLBXJJ-00003',
                          'password': 'qlbxjj001'}
        sichuan_account = {'username': 'DRTGQC-00009',
                           'password': 'pingan000'}
        if wbdriver == 'PhantomJS':
            self.driver = webdriver.PhantomJS()
        else:
            self.driver = webdriver.Chrome()
        self.car_selector = 0
        # self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1280, 800)
        self.stopHint = 0
        self.official_insur_list = {'CV01001': '机动车损失保险',
                                    'CV05002': '机动车第三者责任保险',
                                    'CV08000': '玻璃单独破碎险',
                                    'CV09003': '机动车全车盗抢保险',
                                    'CV13004': '机动车车上人员责任保险(司机)',
                                    'CV17000': '车身划痕损失险',
                                    'CV17005': '机动车车上人员责任保险(乘客)',
                                    'CV18000': '自燃损失险',
                                    'CV36041': '发动机涉水损失险',
                                    'CV48057': '指定修理厂险',
                                    'CV49063': '机动车损失保险无法找到第三方特约险',
                                    'CV27027': '不计免赔险(机动车损失保险)',
                                    'CV31028': '不计免赔险(机动车第三者责任保险)',
                                    'CV41048': '不计免赔险(机动车全车盗抢险)',
                                    'CV44049': '不计免赔险(机动车车上人员责任保险(司机))',
                                    'CV44080': '不计免赔险(机动车车上人员责任保险(乘客))',
                                    'CV56075': '不计免赔险(车身划痕损失险)',
                                    'CV58077': '不计免赔险(自燃损失险)',
                                    'CV60079': '不计免赔险(发动机涉水损失险)',
                                    }
        self.refresh_times = 0
        self.account = sichuan_account
    # 翻页
    def roll_page(self, roll_long):
        js = "var q=document.body.scrollTop={}".format(roll_long)
        self.driver.execute_script(js)

    # 登录页面操作命令
    def login(self):
        self.driver.get('https://pacas-login.pingan.com.cn/cas/PA003/ICORE_PTS/login')
        username = self.driver.find_element_by_xpath('//*[@id="username"]')
        pwd = self.driver.find_element_by_xpath(r'//*[@id="password"]')
        username.send_keys(self.account['username'])
        pwd.send_keys(self.account['password'])
        validCode = self.driver.find_element_by_xpath(r'//*[@id="randCodeText"]')
        imageLocate = self.driver.find_element_by_xpath(r'//*[@id="randCode"]')
        savePath = 'validcode.png'
        # validcode   = crop_valid_code(save_path=savePath, driver=self.driver, image_element=imageLocate)
        # validCode.send_keys(validcode)
        #self.driver.save_screenshot('pic.png')
        validCode.send_keys(input('input valicode'))
        botton = self.driver.find_element_by_xpath(r'//*[@id="loginButton"]')
        botton.click()
        time.sleep(2)
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
                return self.login()
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
            if self.stopHint == 1:
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
        botton = self.driver.find_element_by_xpath(r'//*[@id="mainContent"]/div[2]/div[2]/form/div[2]/div/div/button[1]')
        botton.click()
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'owner_isShowExtInfo personnelCtrl_isShowExtInfo')))
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
        self.driver.find_element_by_xpath(r'//*[@id="ownerDriverInfoDiv"]/div/div[1]/div/input').send_keys(infos['ownerInfo']['ownerName'])  # 车主姓名
        id_type = '身份证'
        # 预留证件类型选择 口
        if id_type == '身份证':
            self.driver.find_element_by_xpath(r'//*[@id="ownerDriverInfoDiv"]/div/div[2]/div/input').send_keys(infos['ownerInfo']['ownerId'])  # 证件号
        else:
            selector = Select(self.driver.find_element_by_xpath('//*[@id="ownerDriverInfoDiv"]/div/div[2]/div/select'))
            selector.select_by_visible_text('其他')
            self.driver.find_element_by_xpath(r'//*[@id="ownerDriverInfoDiv"]/div/div[2]/div/input').send_keys(infos['ownerInfo']['ownerId'])  # 证件号
            self.driver.find_element_by_xpath('//*[@id="dp1534149415604"]')
        #车辆信息
        self.plate = infos['carInfo']['plateNo']
        self.vinNo = infos['carInfo']['vehicleFrameNo']
        self.driver.find_element_by_xpath(r'//*[@id="vehicleLicenceCode"]').send_keys('{}-{}'.format(self.plate[0], self.plate[1:]))  # 车牌号
        self.driver.find_element_by_xpath(r'//*[@id="engineNo"]').send_keys(infos['carInfo']['engineNo'])  # 发动机号
        self.driver.find_element_by_xpath(r'//*[@id="vehicleFrameNo"]').send_keys(self.vinNo)  # 车架号
        self.driver.find_element_by_xpath('//*[@id="VehicleFrameNoID"]/div/button').click()
        reg1 = 'watch:veh.brandParaOutYear" ui-valid-id=".*?" id="dp(.*?)"'  # 初等日期reg
        reg2 = 'ng-change="refreshBeginTimeC51\(\)" ui-valid-id=".*?" id="dp(.*?)"'  # 交强险reg
        reg3 = 'ui-valid="r datetime rule\.insure\.beginDate" ng-change="refreshBeginTimeC01\(\)" ng-disabled="ctrl\.isShowCommDate" ui-valid-id=.*? id="dp(.*?)"'  # 商业险reg
        htmlContent = self.driver.page_source
        firstRegist_id = re.findall(reg1, htmlContent)[0]  # 初等id
        self.firstRegist = infos['carInfo']['firstRegist']
        self.driver.find_element_by_xpath(r'//*[@id="dp{}"]'.format(firstRegist_id)).send_keys(self.firstRegist)#初等日期
        # 险种日期填写''
        # 商业险
        beginTime_commercial_id = re.findall(reg2, htmlContent)[0]  # 定位元素id
        beginTime_commercial    = self.driver.find_element_by_xpath('//*[@id="dp{}"]'.format(beginTime_commercial_id))
        beginTime_commercial.clear()
        # 因为平安系统脑残，所以要分批录入
        comm_begin_time = infos['insuranceInfo']['commInfo']['beginTime']
        part1, part2, part3 = comm_begin_time.split('-')
        beginTime_commercial.send_keys('{}-{}-A'.format(part1,part2))
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
        self.driver.find_element_by_xpath('//*[@id="auto0Div"]/div/div[3]/div/div[2]/form[2]/div/div[1]/div[1]/div/div[1]/label/input').click()
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
        CheSun    = infos['insuranceInfo']['commInfo']['chesuanInsurance']
        if CheSun['baoe']    == '不投保':
            self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/input').click()#勾选车损
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
                selector.select_by_visible_text(str(int(DiSanFang['baoe'])//10000))  # 保额选择
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
            self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[4]/td[1]/input').click()  # 勾选抢盗险
        # ===============================================司机座位责任险
        SiJi = infos['insuranceInfo']['commInfo']['sijiInsurance']
        if SiJi['baoe']     != '不投保':
            sijiValue = self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[5]/td[3]/div/span/input')
            sijiValue.click()
            for i in range(10):
                sijiValue.send_keys(Keys.BACK_SPACE)
            sijiValue.send_keys(SiJi['baoe'])
        else:
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[5]/td[1]/input').click()  # 勾选司机险
        # ===============================================乘客座位责任险
        ChengKe = infos['insuranceInfo']['commInfo']['chenkeInsurance']
        if ChengKe['baoe']  != '不投保':
            chengkeValue = self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[6]/td[3]/div/span/input[2]')
            for i in range(10):
                chengkeValue.send_keys(Keys.BACK_SPACE)
            chengkeValue.send_keys(ChengKe['baoe'])
        else:
            self.driver.find_element_by_xpath(
                r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[6]/td[1]/input').click()  # 勾选乘客险
        # ===============================================玻璃单独破碎险
        BoLi = infos['insuranceInfo']['commInfo']['boliInsurance']
        if BoLi['baoe']     != '不投保':
            if BoLi['baoe'] == '进口':
                self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[7]/td[3]/div/input[2]').click()  # 选择进口（默认为国产）
        else:
            self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[7]/td[1]/input').click()  # 勾选 玻璃单独破碎险
        # ===============================================车身划痕损失险
        self.driver.find_element_by_xpath\
            (r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[10]/td[1]/input').send_keys(Keys.TAB)
        # ===============================================自燃损失险
        ZiRan = infos['insuranceInfo']['commInfo']['ziranInsurance']
        if ZiRan['baoe']    == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[9]/td[1]/input').click()  # 勾选 自燃损失险
        # ===============================================发动机涉水损失险
        SheShui = infos['insuranceInfo']['commInfo']['fadongjiInsurance']
        if SheShui['baoe']  == '投保':
            self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[10]/td[1]/input').click()  # 勾选 发动机涉水损失险
        # ===============================================指定专修厂特约条款
        ZhuanXiu = infos['insuranceInfo']['commInfo']['zhuanxiuInsurance']
        # ===============================================无法找到第三方特约险
        TeYue = infos['insuranceInfo']['commInfo']['teyueInsurance']
        if ZhuanXiu or TeYue:
            self.driver.find_element_by_xpath(r'//*[@id="ctrl_isShowExtDuty"]/span').click()
            self.driver.find_element_by_xpath(r'//*[@id="plan-ext-tbl"]/tbody/tr[8]/td[1]/input').send_keys(Keys.TAB)
            if ZhuanXiu['baoe'] == '投保':
                self.driver.find_element_by_xpath(r'//*[@id="plan-ext-tbl"]/tbody/tr[5]/td[1]/input').click()  # 勾选 发动机涉水损失险
                #rateInput = self.driver.find_element_by_xpath(r'//*[@id="rate"]')
                #rateInput.clear()
                #rateInput.send_keys('0.3')
            if TeYue['baoe']    == '投保':
                self.driver.find_element_by_xpath(r'//*[@id="plan-ext-tbl"]/tbody/tr[6]/td[1]/input').click()  # 勾选 无法找到第三方特约险
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
                self.driver.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[8]/td[4]/input[1]').click()  # 取消 不计免赔勾选
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
                error_str += '{},流水号：{}\n'.format(num,message)
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
                self.driver.find_element_by_xpath(r'/html/body/div[1]/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/input').click()
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
            self.driver.find_element_by_xpath('/html/body/fieldset/form/table[2]/tbody/tr[{}]/td[1]/input'.format(2 + choice)).click()
            time.sleep(1)
            self.driver.find_element_by_xpath('/html/body/fieldset/form/table[2]/tbody/tr[{}]/td/button'.format(2 + len(years))).click()
            self.driver.switch_to.parent_frame()
            time.sleep(10)
            return self.calculate_price()
        elif '续保检索及新能源车校验' in response:
            print('续保检索及新能源车校验')
            self.driver.switch_to.frame('doalogBox')
            self.driver.find_element_by_xpath('/html/body/div[2]/div/button').click()
            try:
                if '本次投保保险起期大于上年保单止期，请确认本年保险起止日期' in self.driver.page_source:
                    self.driver.find_element_by_xpath('/html/body/div[1]/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/input').click()
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

    def get_insur_info(self, insur_code):
        self.driver.find_element_by_xpath(r'//*[@id="beApply"]/span').click()
        self.driver.switch_to.frame('main')
        selector = Select(self.driver.find_element_by_xpath('//*[@id="apply.voucherType"]'))
        selector.select_by_visible_text('子询价单号')
        self.driver.find_element_by_xpath('//*[@id="mainContent"]/form/div[3]/div[3]/div[2]/div[6]/div/input').send_keys(insur_code)
        self.driver.find_element_by_xpath('//*[@id="mainContent"]/form/div[3]/div[13]/button[1]').click()
        time.sleep(1)
        self.roll_page(2000)
        self.driver.find_element_by_xpath('//*[@id="mainContent"]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td[2]/a').click()
        time.sleep(1)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fieldset-legend')))
        origion_data = re.findall('var quotationDTO = (\{.*\})', self.driver.page_source)[0]
        origion_data = origion_data.replace('true', 'True')
        origion_data = origion_data.replace('false', 'False')
        data = eval(origion_data)
        return data


# 格式化print
def json_print(dict_data):
    import json
    json_dicts = json.dumps(dict_data, ensure_ascii=False, indent=4)
    print(json_dicts)


def sum_job(driver='PhantomJS'):
    crewer = PingAnCrew(wbdriver=driver)  # 初始化任务
    crewer.login()  # 登录
    time_count = 0
    while True:
        if crewer.check_login():  # 当前状态为已登录
            # 原始数据
            info = MysqlUsage.get_one_piece()  # 从库里取一条数据出来
            if info:
                write_down_error(str(info))  # 日志记录
                try:
                    crewer.transfer()  # 跳转
                except NoSuchElementException:
                    crewer.close_mission()
                    sum_job(driver=driver)
                # 填信息
                if crewer.fill_in_blanks(infos=sum_up_info(info=info)):
                    # 给系统10秒报价
                    time.sleep(10)
                    # 报价
                    price_return = crewer.calculate_price()
                    # 查询结果
                    if price_return:
                        if price_return['status'] == 1:
                            res_dictionary = crewer.get_insur_info(insur_code=price_return['error_message'])
                            if res_dictionary:
                                message = '询价成功'
                                # 把信息整理成规范的入库格式
                                reptileDict = sum_up_response(res_dictionary=res_dictionary, inquiry_info=info, error_message=message)
                                # 插入成功条数
                                MysqlUsage.insert_success_reptile(reptile_dict=reptileDict)
                            else:
                                message = '未知错误:{}'.format(price_return['error_message'])
                                write_down_error(message)
                        elif price_return['status'] == 0:
                            MysqlUsage.update_inquiry_error_count(quiryId=info['inquiryId'])
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
                                           'message': price_return['error_message'],
                                           }
                            MysqlUsage.insert_failed_reptile(reptileDict)
                    else:
                        message = '未知错误:{}'.format(price_return['error_message'])
                        write_down_error(message)
                    # 跳回首页
                else:
                    MysqlUsage.update_inquiry_error_count(quiryId=info['inquiryId'])
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
                                   'message': '报价引擎出错',
                                   }
                    MysqlUsage.insert_failed_reptile(reptileDict)
                    write_down_error('报价引擎出错')
                crewer.back_to_main()
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
    sum_job(driver='Chrome')

    #analyse_info()
