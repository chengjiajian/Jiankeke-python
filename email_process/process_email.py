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
                email_type = 2  # 预付
            else:
                email_type = 1  # 非预付
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
                            programme_id = re.findall('SYP-\w{8}-\w{3}', value)
                            if programme_id:
                                # time title是这封邮件的唯一标识 名 字
                                time_title = '{}_{}_{}'.format(date_now, programme_id[0], email_type)
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
            sql_content = "select createTime,insuranceNum,commercialPrice,compulsoryPrice,returnPrice,validTime,plate,insuranceName from contract_excel_model where programId='{}'".format(self.programme_id)
            cursor.execute(sql_content)
            result = cursor.fetchall()
        return result

    # 插入单条 付款信息
    def InsertAdvance(self, data_list):
        with mysql_analyze() as cursor:
            sql_content = "INSERT INTO baoli_advances(cationDate, organization, inCompany, cationNumber, state, contractId, proName, postpone, actualMoney, returnMoney, interest, passMoney, taxation, contractName, returnPeriod, expectReturnTime, createTime, businessApprover, baoliType) \
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            c = cursor.executemany(sql_content, data_list)


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
        #
        # 判断是否为 付款清单excel
        header_line = ['收款账号', '开户行', '收款户名', '打款金额']
        if header_line in sheet_list:  # 判断是否为付款excel
            header_line_index = sheet_list.index(header_line)
            actualMoney = 0
            for i in range(header_line_index + 1, len(sheet_list)):
                print(sheet_list[i])
                if sheet_list[i][3]:
                    actualMoney += float(sheet_list[i][3])
            cationDate = datetime.datetime.now().strftime('%Y-%m-%d')
            returnPeriod = int(programme_info_dict['cycleTime']) if programme_info_dict['cycleTime'] else 0  # 回款周期
            interest_rate = float(programme_info_dict['interest'])  # 手续费率
            passFee_rate = float(programme_info_dict['passFee'])  # 通道费率
            taxPoint_rate = float(programme_info_dict['taxPoint'])  # 税费
            # 必传
            state = 4
            baoliType = programme_info_dict['baoliType']
            contractName = programme_info_dict['proName']
            businessApprover = programme_info_dict['businessApprover']
            # 实际回款 = 实际付款 * （（1+ 万分之五*周期）/ （1-税率-通道费率））  ##其中，周期为0的时候，对应到付（非垫资）业务
            returnMoney = actualMoney * ((1+0.0005 * returnPeriod)/(1 - taxPoint_rate - passFee_rate)) if self.file_type == 1 else actualMoney * ((1+0.0005 * 0)/(1 - taxPoint_rate - passFee_rate))
            interest = actualMoney * interest_rate  # 手续费
            passMoney = actualMoney * passFee_rate  # 通道费
            taxation = actualMoney * taxPoint_rate  # 税费
            expectReturnTime = createTime if self.file_type == 2 else datetime.datetime.now() + datetime.timedelta(days=int(returnPeriod))  # 如果是预付，加法回款日期，非预付，即刻到账
            advance = [cationDate, organization, inCompany, self.cationNumber, state, contractId_pro, proName, postpone, actualMoney, returnMoney, interest, passMoney, taxation, contractName, returnPeriod, expectReturnTime, createTime, businessApprover, baoliType]
            self.InsertAdvance([advance, ])  # requires list data
        else:
        # 不是付款清单的 情况
            for i in range(len(sheet_list)):  # 遍历excel，判断title
                stop_hint = 0
                row_value = sheet_list[i]
                for header_type in excel_model_list:
                    header_title_list = [header_type[key] for key in header_type if header_type[key]]
                    if header_title_list == [a for a in header_title_list if a in row_value]:  # 分析title模型是否 被包含在 行数据里
                        stop_hint = 1
                        header_dict = deepcopy(header_type)
                        break
                if stop_hint:
                    title_index = i
                    break
            else:
                title_index = -1
            # 为了看起来清晰  写在遍历外面
            if title_index != -1:  # 如果匹配到了title
                insert_list = []
                uName = 'cjj_python_newemail'
                uid = 8
                flag = 1
                status = 2
                for row_value in sheet_list[title_index+1:]:
                    if not row_value[0]:
                        break
                    writeDate       = row_value[sheet_list[title_index].index(header_dict['createTime'])] \
                        if header_dict['createTime'] else datetime.datetime.now()  # 签单日期
                    insuranceNum    = row_value[sheet_list[title_index].index(header_dict['insuranceNum'])] \
                        if header_dict['insuranceNum'] else ''  # 保单号
                    commercialPrice = row_value[sheet_list[title_index].index(header_dict['commercialPrice'])] \
                        if header_dict['commercialPrice'] else ''  # 商业险保费
                    compulsoryPrice = row_value[sheet_list[title_index].index(header_dict['compulsoryPrice'])] \
                        if header_dict['compulsoryPrice'] else ''  # 交强险保费
                    returnPrice     = row_value[sheet_list[title_index].index(header_dict['returnPrice'])] \
                        if header_dict['returnPrice'] else 0  # 退费金额，手续费
                    validTime       = row_value[sheet_list[title_index].index(header_dict['validTime'])] \
                        if header_dict['validTime'] else datetime.datetime.now()  # 生效时间
                    plate           = row_value[sheet_list[title_index].index(header_dict['plate'])] \
                        if header_dict['plate'] else ''  # 生效时间
                    owner_name      = row_value[sheet_list[title_index].index(header_dict['insuranceName'])] \
                        if header_dict['insuranceName'] else ''  # 投保人
                    #  商业险 和 交强险 分开2次插入
                    if commercialPrice:
                        rate = round(float(returnPrice) / float(commercialPrice), 4)
                        single_data = (organization, inCompany, inCompany, '', writeDate, owner_name, '', plate,
                                       commercialPrice,rate, returnPrice, status, uid, uName, createTime, flag, 2, 2,
                                       '商业险', insuranceNum, '', self.cationNumber, returnPrice, 0, 1, 1, contractId,
                                       contractId_pro, proName, validTime)
                        insert_list.append(single_data)
                    if compulsoryPrice:
                        rate = round(float(returnPrice) / float(compulsoryPrice), 4)
                        single_data = (organization, inCompany, inCompany, '', writeDate, owner_name, '', plate,
                                       compulsoryPrice, rate, returnPrice, status, uid, uName, createTime, flag, 2, 1,
                                       '交强险', insuranceNum, '', self.cationNumber, returnPrice, 0, 1, 1, contractId,
                                       contractId_pro, proName, validTime)
                        insert_list.append(single_data)
                MysqlAnalyzeUsage.new_insert_single_insur(insert_list)
            else:  # 没有匹配到title
                pass



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
                excel_folder_path = os.path.join(main_path, folder_name)
                date_info, programme_id, file_type = folder_name.split('_')
                date_year_info = parse(date_info.split('-')[0])
                # 遍历对应邮件下的文件
                # try:
                cationNumber = 'SYCX{}'.format(str(int(time.time() * 1000)))  # 标识
                for file in os.listdir(excel_folder_path):
                    excel_path = os.path.join(excel_folder_path, file)
                    process_tool = ProcessPayment(excel_path, programme_id, file_type, cationNumber)
                    process_tool.process_excel()
                # except Exception as e:
                #     #pass
                #     send_email(error_message_dict={"title": folder_name, "error_message": str(e)}, sender_email='busadvance@shiyugroup.com', receiver_email=sender_email)
                #send_email(error_message_dict={"title": folder_name, "error_message": str("e")},sender_email='busadvance@shiyugroup.com', receiver_email=sender_email)
        ruuning_time_count += 1
        next_time = '本次扫描结束，下次扫描时间 {}'.format(datetime.datetime.now() + timedelta(minutes=5))
        print(next_time)
        write_down_time(next_time)
        time.sleep(60 * 5)


if __name__ == '__main__':
    main_job()
    # job = ProcessPayment(file_path=r'C:\Users\ASUS\Desktop\3.25-3.26清单.xlsx', programme_id='SYP-20190107-002', file_type=1)
    # job.process_excel()