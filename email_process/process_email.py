from email_process.usages.settings import *
from email_process.usages.email_usage import ali_pop_usage
from email_process.usages.file_tools import *
from email_process.usages.mysql_usage import *
from email.parser import Parser
from dateutil.parser import parse
from email.header import decode_header
from email.utils import parseaddr
from xlrd import open_workbook
from openpyxl import load_workbook
from email_process.analyzeExcelTest import processSheet,analyzeSheet
from datetime import timedelta
import pyexcel_xlsx
import re
import time
import os
from copy import deepcopy


# 处理邮件
class ProcessEmail:
    def __init__(self):
        print('正在初始化邮箱')
        pass

    # 获取文本编码
    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    # 解码
    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    # 获取email 附件
    def get_excel_from_email(self):
        sum_email_info = {'status': 0, 'mail_list': {}}  # 记录所有 需要录的邮件信息
        for email_account in [nobusadvance_email, busadvance_email]:
            print('scanning the email:{}========================================'.format(email_account))
            if 'nobus' in email_account:
                email_type = 1  # 非预付
            else:
                email_type = 2  # 预付
            with ali_pop_usage(useraccount=email_account) as server:
                # 使用list()返回所有邮件的编号，默认为字节类型的串
                resp, mails, octets = server.list()
                total_mail_numbers = len(mails)
                if not os.path.exists(main_path):  # 如果文件夹不存在，创建文件夹
                    os.makedirs(main_path)
                # 从后往前 翻一遍邮箱
                for i in range(total_mail_numbers, 0, -1):
                    resp, lines, octets = server.retr(i)
                    msg_content = b'\r\n'.join(lines).decode('utf-8')
                    msg = Parser().parsestr(msg_content)
                    # 转换邮箱内的时间
                    date_now = time.strftime("%Y%m%d-%H-%M-%S",
                                             time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S'))  # 格式化收件时间
                    x = time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S')
                    a = '{}-{}-{} {}:{}:{}'.format(x.tm_year, x.tm_mon, x.tm_mday, x.tm_hour, x.tm_min, x.tm_sec)
                    delete_time = datetime.datetime.now() - datetime.timedelta(days=30)
                    time_delta = parse(a) - delete_time
                    if time_delta.days > 0:
                        sender = msg.get('From', '')  # 发件人信息处理========================
                        hdr, address = parseaddr(sender)
                        name = self.decode_str(hdr)
                        # 这里获得了 发件人名字，发件人邮箱
                        from_name = u'{}'.format(name)  # 发件人名称
                        from_address = u'{}'.format(address)  # 发件人邮箱
                        title_value = msg.get('Subject', '')
                        if title_value:
                            # 需要解码Subject字符串:
                            value = self.decode_str(title_value)
                            print('{}、这封邮件标题:'.format(i), value)
                            identify_id = re.findall('SYP-\w{8}-\w{3}', value) if re.findall('SYP-\w{8}-\w{3}', value) else re.findall('SYCX[0-9]{13}', value)
                            if identify_id:
                                # time title是这封邮件的唯一标识 名 字
                                time_title = '{}_{}_{}'.format(date_now, identify_id[0], email_type)
                                save_path = os.path.join(main_path, time_title)
                                if not os.path.exists(save_path):  # 如果文件夹不存在，创建文件夹
                                    os.makedirs(save_path)
                                # 检查库里情况===========================
                                check_response = MysqlUsage.check_attachment_exist(time_title)
                                if check_response:
                                    sum_email_info['status'] = 1
                                    # 遍历邮件内容
                                    for part in msg.walk():
                                        # 分析附件名字
                                        filename = part.get_filename()
                                        if filename:
                                            # 文件名转码
                                            true_file_name = self.decode_str(filename)
                                            if 'xls' in true_file_name:
                                                # 发现附件 就解析附件
                                                data = part.get_payload(decode=True)
                                                with open(os.path.join(save_path, true_file_name), 'wb') as file:
                                                    file.write(data)
                                                print('{} 下载成功'.format(true_file_name))

                                                MysqlUsage.insert_data(time_title=time_title, file_name=true_file_name,
                                                                       email_type=email_type,
                                                                       email_account=from_address,
                                                                       email_name=from_name, origin_name=true_file_name)
                                                if time_title not in sum_email_info['mail_list']:
                                                    sum_email_info['mail_list'][time_title] = from_address
                            else:
                                message = '发现新邮件,但邮件抬头里没有台账关键字,所以跳过'
                                print(message)
                    else:
                        server.dele(i)
        return sum_email_info


class ProcessPayment:
    def __init__(self, file_path, programme_id, file_type, cationNumber):
        self.file_path = file_path
        self.programme_id = programme_id
        self.file_type = int(file_type)
        self.cationNumber = cationNumber
        self.insert_detail_list = []
        self.insert_advance_data = []
        self.sum_payment = 0
        self.bussiness_type = ''

    # 获取 项目的 详细信息
    def GetProgrammeInfo(self):
        with mysql_analyze() as cursor:
            sql_content = "select * from contract where programId='{}'".format(self.programme_id)
            cursor.execute(sql_content)
            result = cursor.fetchall()
        return result

    # 获取 项目 对应的excel信息
    def GetProgrammeExcelModel(self):
        with mysql_analyze() as cursor:
            sql_content = "select createTime,insuranceNum,commercialPrice,compulsoryPrice,returnPrice,validTime,plate,insuranceName,remark,detailType,detailName,endValue from contract_excel_model where programId='{}'".format(self.programme_id)
            cursor.execute(sql_content)
            result = cursor.fetchall()
        return result


    # 先把excel预处理
    def process_excel(self):
        pure_file_name, excel_type = os.path.splitext(os.path.split(self.file_path)[1])
        if 'xls' in excel_type:
            excel_data_dict = pyexcel_xlsx.read_data(self.file_path)
            for sheet_name, values in excel_data_dict.items():
                self.process_excel_detail(values)

    # excel的后续内容分析
    def process_excel_detail(self, sheet_list):
        programme_info_dict, excel_model_list = self.GetProgrammeInfo(), self.GetProgrammeExcelModel()
        programme_info_dict = programme_info_dict[0]
        postpone = self.file_type
        createTime = datetime.datetime.now()
        organization = programme_info_dict['institution']
        inCompany = programme_info_dict['inCompany']
        contractId_pro = programme_info_dict['programId']
        contractId = programme_info_dict['contractId']
        proName = programme_info_dict['conName']
        baoliType = programme_info_dict['baoliType']
        while [] in sheet_list:
            sheet_list.remove([])
        #
# =====================是付款清单的  情况=======================
        header_line = ['收款账号', '开户行', '收款户名', '打款金额']
        if header_line in sheet_list:  # 判断是否为付款excel
            print('payment_sheet')
            self.bussiness_type = "payment_sheet"
            header_line_index = sheet_list.index(header_line)
            for i in range(header_line_index + 1, len(sheet_list)):
                print(sheet_list[i])
                if sheet_list[i][3]:
                    self.sum_payment += float(sheet_list[i][3])
            cationDate = datetime.datetime.now().strftime('%Y-%m-%d')
            returnPeriod = int(programme_info_dict['cycleTime']) if programme_info_dict['cycleTime'] else 0  # 回款周期
            interest_rate = float(programme_info_dict['interest'])  # 手续费率
            passFee_rate = float(programme_info_dict['passFee'])  # 通道费率
            taxPoint_rate = float(programme_info_dict['taxPoint'])  # 税费
            # 必传
            state = 4
            contractName = programme_info_dict['proName']
            businessApprover = programme_info_dict['businessApprover']
            # 实际回款 = 实际付款 * （（1+ 万分之五*周期）/ （1-税率-通道费率））  ##其中，周期为0的时候，对应到付（非垫资）业务
            # returnMoney = self.sum_payment * ((1+0.0005 * returnPeriod)/(1 - taxPoint_rate - passFee_rate)) if self.file_type == 2 else self.sum_payment * ((1+0.0005 * 0)/(1 - taxPoint_rate - passFee_rate))  #  经过讨论作废此公式  20190403
            # 新公式 实际回款 = 实际付款 * （ 1/（1-税率-通道费率）+ 万分之五*周期））
            returnMoney = self.sum_payment * ((1 / (1 - taxPoint_rate - passFee_rate)) + 0.0005 * returnPeriod) if self.file_type == 2 else self.sum_payment / (1 - taxPoint_rate - passFee_rate)
            interest = self.sum_payment * 0.0005 * returnPeriod  # 手续费 # self.sum_payment * interest_rate
            passMoney = self.sum_payment * passFee_rate  # 通道费
            taxation = self.sum_payment * taxPoint_rate  # 税费
            expectReturnTime = createTime if self.file_type == 1 else datetime.datetime.now() + datetime.timedelta(days=int(returnPeriod))  # 如果是预付，加法回款日期，非预付，即刻到账
            advance = [cationDate, organization, inCompany, self.cationNumber, state, contractId_pro, proName, postpone, self.sum_payment, returnMoney, interest, passMoney, taxation, contractName, returnPeriod, expectReturnTime, createTime, businessApprover, baoliType]
            self.insert_advance_data.append(advance)
# =====================不是付款清单的 情况=======================
        else:
            print('service_sheet')
            self.bussiness_type = 'service_sheet'
            if baoliType == '1':  # =佣金=手续费
                print('手续费')
                for i in range(len(sheet_list)):  # 遍历excel，判断title
                    stop_hint = 0
                    row_value = sheet_list[i]
                    for header_type in excel_model_list:  # 遍历同一个查询结果下的所有模板
                        header_title_list = sorted([header_type[key] for key in header_type if
                                                    header_type[key] and key not in (
                                                    'detailType', 'endValue')])  # 剔除不必要关键词
                        print('header_title_list', header_title_list, 'a',
                              [a for a in header_title_list if a in row_value])
                        if header_title_list == sorted(
                                [a for a in header_title_list if a in row_value]):  # 分析title模型是否 被包含在 行数据里
                            stop_hint = 1
                            header_dict = deepcopy(header_type)
                            # insert_list = []
                            uName = 'cjj_python_newemail'
                            uid = 8
                            flag = 1
                            status = 2
                            detailType = header_dict['detailType']
                            print("header_dict['endValue']", header_dict['endValue'])
                            for _row_value in sheet_list[i + 1:]:
                                if _row_value[0] == header_dict['endValue'] or not _row_value[0]:#not _row_value[0] or
                                    break
                                writeDate = _row_value[row_value.index(header_dict['createTime'])] \
                                    if header_dict['createTime'] else datetime.datetime.now()  # 签单日期
                                insuranceNum = _row_value[row_value.index(header_dict['insuranceNum'])] \
                                    if header_dict['insuranceNum'] else ''  # 保单号
                                returnPrice = float(_row_value[row_value.index(header_dict['returnPrice'])]) \
                                    if header_dict['returnPrice'] else 0  # 退费金额，手续费
                                validTime = _row_value[row_value.index(header_dict['validTime'])] \
                                    if header_dict['validTime'] else datetime.datetime.now()  # 生效时间
                                plate = _row_value[row_value.index(header_dict['plate'])] \
                                    if header_dict['plate'] else ''  # 生效时间
                                owner_name = _row_value[row_value.index(header_dict['insuranceName'])] \
                                    if header_dict['insuranceName'] else ''  # 投保人
                                remark = _row_value[row_value.index(header_dict['remark'])] \
                                    if header_dict['remark'] else '无'  # 备注
                                #  商业险 和 交强险 分开2次插入
                                self.sum_payment += returnPrice
                                if detailType == 1:
                                    commercialPrice = _row_value[row_value.index(header_dict['commercialPrice'])] \
                                        if header_dict['commercialPrice'] else ''  # 商业险保费
                                    compulsoryPrice = _row_value[row_value.index(header_dict['compulsoryPrice'])] \
                                        if header_dict['compulsoryPrice'] else ''  # 交强险保费
                                    if commercialPrice:
                                        rate = round(returnPrice / float(commercialPrice), 4)
                                        single_data = (organization, inCompany, inCompany, '', writeDate, owner_name, '', plate,
                                                       commercialPrice, rate, returnPrice, status, uid, uName, createTime, flag,
                                                       2, 2,
                                                       '商业险', insuranceNum, '', self.cationNumber, returnPrice, 0, 1, 1,
                                                       contractId,
                                                       contractId_pro, proName, validTime, remark)
                                        self.insert_detail_list.append(single_data)
                                    if compulsoryPrice:
                                        rate = round(returnPrice / float(compulsoryPrice), 4)
                                        single_data = (organization, inCompany, inCompany, '', writeDate, owner_name, '', plate,
                                                       compulsoryPrice, rate, returnPrice, status, uid, uName, createTime, flag,
                                                       2, 1,
                                                       '交强险', insuranceNum, '', self.cationNumber, returnPrice, 0, 1, 1,
                                                       contractId,
                                                       contractId_pro, proName, validTime, remark)
                                        self.insert_detail_list.append(single_data)
                                elif detailType == 2:
                                    detail_name = _row_value[row_value.index(header_dict['detailName'])] if header_dict['detailName'] else ''  # 商业险保费
                                    payPrice = _row_value[row_value.index(header_dict['commercialPrice'])] \
                                        if header_dict['commercialPrice'] else ''  # 商业险保费
                                    rate = round(returnPrice / float(payPrice), 4)
                                    single_data = (
                                    organization, inCompany, inCompany, '', writeDate, owner_name, '', plate,
                                    payPrice, rate, returnPrice, status, uid, uName, createTime, flag,
                                    2, 3,
                                    detail_name, insuranceNum, '', self.cationNumber, returnPrice, 0, 1, 1,
                                    contractId,
                                    contractId_pro, proName, validTime, remark)
                                    self.insert_detail_list.append(single_data)
                            break
                    if stop_hint:
                        break
            elif baoliType == '2':  # 批增 业务
                print('批增')
                sheet_col_dict = analyzeSheet(sheet_list)
                #sheet_col_dict = {'price':2, 'remark':1}
                if 'price' in sheet_col_dict:
                    #  返回详细信息
                    insert_list, row_count, amount_count = processSheet(sheet_list, self.programme_id, self.cationNumber, sheet_col_dict)
                    self.insert_detail_list.extend(insert_list)
                    self.sum_payment += sum([x[10] for x in insert_list])


# 主任务流程
def main_job():
    write_down_error('开始执行主任务')
    ruuning_time_count = 0
    while True:
        mail = ProcessEmail()
        email_info = mail.get_excel_from_email()
        if email_info['status'] == 1:
            # 遍历 邮件结果
            for folder_name, sender_email in email_info['mail_list'].items():
                folder_path = os.path.join(main_path, folder_name)
                #date_info, programme_id, file_type = folder_name.split('_')
                date_info, identify_id, file_type = folder_name.split('_')
                # 如果是续传文件
                if re.findall('SYCX[0-9]{13}', identify_id):
                    insert_detail_list = []
                    sum_payment = 0
                    sum_count = 0
                    for file in os.listdir(folder_path):
                        excel_data_dict = pyexcel_xlsx.read_data(os.path.join(folder_path, file))
                        programme_id = MysqlAnalyzeUsage.get_programId_from_advance(identify_id)
                        if programme_id:
                            for sheet_name, values in excel_data_dict.items():
                                sheet_col_dict = analyzeSheet(values)
                                if 'price' in sheet_col_dict:
                                    insert_list, row_count, amount_count = processSheet(values, programme_id,
                                                                                        identify_id, sheet_col_dict)
                                    insert_detail_list.extend(insert_list)
                                    sum_payment += amount_count
                                    sum_count += row_count
                        MysqlAnalyzeUsage.new_insert_single_insur(insert_detail_list)
                        MysqlAnalyzeUsage.update_advance_counts(counts=sum_count,amounts=sum_payment,cationNumber=identify_id)
                # 如果是直接传付款凭证 + 清单
                elif re.findall('SYP-\w{8}-\w{3}', identify_id):
                    print('date_info,programme_id,file_type', date_info, identify_id, file_type)
                    cationNumber = 'SYCX{}'.format(str(int(time.time() * 1000)))  # 标识
                    folder_dict = {'payment_sheet': {}, 'service_sheet': {}}
                    for file in os.listdir(folder_path):
                        job = ProcessPayment(file_path=os.path.join(folder_path, file), programme_id=identify_id,
                                             file_type=file_type, cationNumber=cationNumber)
                        job.process_excel()
                        datas = vars(job)
                        folder_dict[datas['bussiness_type']] = datas
                    insert_state = 1

                    if file_type == "2":
                        pay_amount = round(folder_dict['payment_sheet']['sum_payment'], 2)
                        service_amount = round(folder_dict['service_sheet']['sum_payment'], 2)
                        print('pay_amount', pay_amount, 'service_amount', service_amount)
                        insert_state = 1 if pay_amount <= service_amount else 0
                        if insert_state == 0:
                            send_email(error_message_dict={"title": folder_name, "error_message": str('付款金额({})大于清单金额({})'.format(pay_amount, service_amount))},
                                       sender_email='busadvance@shiyugroup.com', receiver_email=sender_email)
                    if insert_state:
                        # 插入付款申请
                        MysqlAnalyzeUsage.InsertAdvance(folder_dict['payment_sheet']['insert_advance_data'])  # requires list data
                        # 插入服务单明细
                        if 'insert_detail_list' in folder_dict['service_sheet']:
                            MysqlAnalyzeUsage.new_insert_single_insur(folder_dict['service_sheet']['insert_detail_list'])
                        print('insert done')
        ruuning_time_count += 1
        next_time = '本次扫描结束，下次扫描时间 {}'.format(datetime.datetime.now() + timedelta(minutes=3))
        write_down_time(next_time)
        print(next_time)
        time.sleep(60 * 3)

def ttestJob():
    cationNumber = 'SYCX{}'.format(str(int(time.time() * 1000)))  # 标识
    folder_dict = {'payment_sheet': {}, 'service_sheet': {}}
    folder_path = r'C:\Users\ASUS\Desktop\测试业务\测试6'
    programme_id = 'SYP-20190107-003'
    file_type = 2
    for file in os.listdir(folder_path):
        job = ProcessPayment(file_path=os.path.join(folder_path, file), programme_id=programme_id,
                             file_type=file_type, cationNumber=cationNumber)
        job.process_excel()
        datas = vars(job)
        folder_dict[datas['bussiness_type']] = datas
    pay_amount = round(folder_dict['payment_sheet']['sum_payment'], 2)
    service_amount = round(folder_dict['service_sheet']['sum_payment'], 2)
    print('pay_amount', pay_amount, 'service_amount', service_amount)
    input('')
    if pay_amount <= service_amount:
        input('low')
    else:
        send_email(error_message_dict={"title": '',
                                       "error_message": str('付款金额({})大于清单金额({})'.format(pay_amount, service_amount))},
                   sender_email='busadvance@shiyugroup.com', receiver_email='busadvance@shiyugroup.com')

if __name__ == '__main__':
    # ttestJob()
    # input('')
    # #main_job()
    # while True:
    #     try:
    main_job()
        # except Exception as e:
        #     print('发生未知错误，详情请看日志')
        #     send_email(error_message_dict={"title": 'systemdown', "error_message": str(e)},
        #                sender_email='busadvance@shiyugroup.com', receiver_email='378218354@qq.com')
        #     write_down_error('run times ,error occoured :\n{} \n'.format('\n' + str(e)))
        #     print('系统将在 {} 分钟后重启： {}'.format(later_mins, datetime.datetime.now() + timedelta(minutes=later_mins)))
        #     time.sleep(60 * later_mins)
    ##ttestJob()
