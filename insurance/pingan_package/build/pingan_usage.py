# 放所有工具方法
import base64
from PIL import Image
import requests
import datetime

# 记录错误信息
def write_down_error(message):
    with open('errorMessage.txt', 'a', encoding='utf-8') as fn:
        fn.write('{} \n {} \n ==============================================='.format(datetime.datetime.now(), message))

# 记录错误信息
def write_down_error_check_or_pay(message):
    with open('errorMessage_check_or_pay.txt', 'a', encoding='utf-8') as fn:
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


# 验证码 校验 接口
def dpi_request(path, code_type=1004):
    try:
        print('正在分析验证码')
        with open(path, 'rb') as s:
            print(path)
            ls_f = base64.b64encode(s.read())  # 读取文件内容，转换为base64编码
            params = {
                "key": '889fdc9bc1d1e5e678e52623b23c1f7a',  # 您申请到的APPKEY
                "codeType": code_type,
                "base64Str": ls_f,  # 图片文件
                "dtype": "",  # 返回的数据的格式，json或xml，默认为json

            }
        url = "http://op.juhe.cn/vercode/index"
        f = requests.post(url=url, data=params, timeout=120)
        res = f.json()
        print('res', res)
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


# 验证码截取 + 校验
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

# 支付码
def crop_pay_picture(save_path, driver, image_element):
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

if __name__ == '__main__':
    pass