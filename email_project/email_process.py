from xlrd import open_workbook
import contextlib
import poplib
import pymysql
from dateutil.parser import parse
from email.parser import Parser
from email.header import decode_header,Header
from email.utils import parseaddr,formataddr
import base64
import datetime
from datetime import timedelta
import time
import re
import os
from openpyxl import load_workbook
from decimal import *
from xlrd import xldate_as_datetime
# 保存地址管理
current_path = 'static'
save_path = os.path.join(current_path, 'excel_attachment')
# 关键字管理
keywords1 = '骚爷台账'  # 普通台账关键字
keywords2 = '骚爷垫资'  # 垫资关键字

# 库名
test_insert_server = 'ggcx_test'
using_insert_server = 'ggcx'
test_info_server = 'insurance_info_temp'
using_info_server = 'insurance_info'

# 切换 入库数据入口
insert_server = using_insert_server

# 切换 取数据的来源
@contextlib.contextmanager
# useraccount='17601228909@163.com'
# useraccount='shiyugroup_cjj@163.com'
def pop_usage(useraccount='shiyugroup_cjj@163.com', password='cjj941208', pop3_server='pop.163.com'):
    useraccount = useraccount
    password = password
    # 邮件服务器地址。如果你的邮箱是163，那么可以这么写。qq的话就是pop.qq.com
    server = poplib.POP3(pop3_server)
    # 可选项： 打开或者关闭调试信息，1为打开，会在控制台打印客户端与服务器的交互信息
    server.set_debuglevel(1)
    # 可选项： 打印POP3服务器的欢迎文字，验证是否正确连接到了邮件服务器
    print(server.getwelcome().decode('utf8'))
    server.user(useraccount)
    server.pass_(password)
    try:
        yield server
    finally:
        server.quit()



# 记录错误信息的方法
def write_down_error(message):
    with open('errorMessage.txt', 'a', encoding='utf-8') as fn:
        fn.write('{} \n {} \n ==============================================='.format(datetime.datetime.now(), message))

# 记录 扫描时间 的方法
def write_down_time(message):
    with open('timeMessage.txt', 'a', encoding='utf-8') as fn:
        fn.write('{} \n {} \n ==============================================='.format(datetime.datetime.now(), message))



# 解码
def decode_base64(s, charset='utf8'):
    return str(base64.decodebytes(s.encode(encoding=charset)), encoding=charset)


# 连接数据库
@contextlib.contextmanager
def mysql(get_type='dict', host='120.55.55.19', port=3306, user='root', passwd='shiyu#2018$', db='excel_info', charset='utf8'):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    if get_type == 'dict':
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    else:
        cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


# 连接正式库
@contextlib.contextmanager
def mysql_analyze(get_type='dict', host='121.40.207.59', port=3306, user='root', passwd='MmlAN8kX', db=insert_server, charset='utf8'):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    if get_type == 'dict':
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    else:
        cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


# 正式库 管理
class MysqlAnalyzeUsage:
    def __init__(self):
        pass

    @classmethod
    def get_info(cls, month, organization_name):
        with mysql_analyze() as cursor:
            sql_content = "SELECT * from insurance_analy WHERE (inType=0 OR inType=2) and month='{}' and inOrganization='{}'".format(month, organization_name)
            c = cursor.execute(sql_content)
            infos = cursor.fetchall()
            return infos

    @classmethod
    def change_info(cls, strange_date, organization, type):
        pass

    # 插表  大数据 非单条
    @classmethod
    def insert_data(cls, data, organization_name='聚仁', year_time='2018'):
        if data:
            now_time = datetime.datetime.now()
            inMonth = '{}/{}'.format(str(year_time)[-2:], data['month'])
            state = 0
            now_month = '{}{}'.format(year_time, data['month'])
            now_day = now_time.strftime('%Y%m%d')
            data.pop('month')
            insert_list = []
            for inType, value in data.items():
                try:
                    rate = Decimal(value['inCharges'] / value['inPrice']).quantize(Decimal('0.00'))
                except Exception:
                    rate = Decimal('0.00').quantize(Decimal('0.00'))
                charges = value['inCharges'] if value['inCharges'] > 0 else 0
                price = value['inPrice'] if value['inPrice'] > 0 else 0
                if charges or price:
                    single_info = (
                        inMonth, organization_name, inType, price, charges, rate, now_time, state, \
                        now_month, now_day, 0)
                    insert_list.append(single_info)
                else:
                    print('两数字都为0')
                    # if value['inCharges'] > 0:
                    #     single_info = (
                    #     inMonth, organization_name, inType, 0, value['inCharges'], rate, now_time, \
                    #     state, now_month, now_day, value['count'])
                    #     insert_list.append(single_info)
                    # else:
                    #     print('inCharges小于0，不录入')
                    # if value['inPrice'] > 0:
                    #     single_info = (
                    #         inMonth, organization_name, inType, value['inPrice'], 0, rate, now_time, \
                    #         state, now_month, now_day, value['count'])
                    #     insert_list.append(single_info)
                    # else:
                    #     print('inPrice小于0，不录入')
            if insert_list:
                with mysql_analyze() as cursor:
                    sql_content = "INSERT INTO insurance_analy(inMonth, inOrganization, inType, inPrice, inCharges, inRate\
            , creatTime, state, month, day, countInfo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    c = cursor.executemany(sql_content, insert_list)
            else:
                print('没有需要入库的保费/手续费数据')
        else:
            print('没取到数据')

    # 批量 插入 单条数据
    @classmethod
    def insert_single_insur(cls, data_list):
        if data_list:
            print('正在将 {} 条保单数据数据入库'.format(len(data_list)))
            with mysql_analyze() as cursor:
                sql_content = "INSERT INTO insurance_info(organization, company, insuranceCompany, insuranceOrgnization, writeDate, insurancePerson,insuranceIdCard, licenseNumber, insurancePrice, insuranceRate, returnPrice, status, uid, uName, createTime, flag, type, insuranceType, insuranceName, insuranceNum, sign) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                c = cursor.executemany(sql_content, data_list)
        else:
            print('没有数据可以入库')


class MysqlUsage:
    def __init__(self):
        pass

    @classmethod
    def check_attachment_exist(cls, time_title):
        print('正在查询邮件名：{} 是否已存在'.format(time_title))
        with mysql() as cursor:
            sql_content = "SELECT * from attachmentData WHERE emailTitle='{}'".format(time_title)
            cursor.execute(sql_content)
            infos = cursor.fetchall()
        if infos:
            print('查库结果： 已存在')
            return False
        return True

    @classmethod
    def insert_data(cls, time_title, file_name, email_account, email_name, email_type, origin_name):
        with mysql() as cursor:
            sql_content = "INSERT INTO attachmentData(email,emailName,fileName,uploadTime,emailTitle,emailType,originName) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(
                email_account, email_name, file_name, datetime.datetime.now(), time_title, email_type, origin_name)
            cursor.execute(sql_content)

    @classmethod
    def get_main_data(cls):
        pass

    # 从库里把 同一个邮件的Excel一起拉出来
    @classmethod
    def get_excel_info_from_mysql(cls, email_title):
        with mysql(get_type='list') as cursor:
            sql_content = "select emailType,fileName from attachmentData where emailTitle='{}'".format(
                email_title)
            cursor.execute(sql_content)
            result = cursor.fetchall()
        return result


class ProcessEmail:
    def __init__(self):
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
        with pop_usage() as server:
            # 使用list()返回所有邮件的编号，默认为字节类型的串
            resp, mails, octets = server.list()
            total_mail_numbers = len(mails)
            current_path = 'static'
            save_path = os.path.join(current_path, 'excel_attachment')
            if not os.path.exists(save_path):  # 如果文件夹不存在，创建文件夹
                os.makedirs(save_path)
            sum_email_info = {'status': 0, 'mail_list': []}  # 记录所有 需要录的邮件信息
            # 从后往前 翻一遍邮箱
            for i in range(total_mail_numbers, 0, -1):
                resp, lines, octets = server.retr(i)
                msg_content = b'\r\n'.join(lines).decode('utf-8')
                msg = Parser().parsestr(msg_content)
                # 转换邮箱内的时间
                date_now = time.strftime("%Y%m%d-%H-%M-%S",
                                         time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S'))  # 格式化收件时间
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
                    # 处理 台账邮件
                    if keywords1 == value:
                        time_title = '{}{}'.format(keywords1, date_now)
                        file_save_name = '台账--{}.xlsx'.format(date_now)
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
                                    if 'xlsx' in true_file_name:
                                        # 发现附件 就解析附件
                                        data = part.get_payload(decode=True)
                                        file_save_path = os.path.join(save_path, file_save_name)
                                        with open(file_save_path, 'wb') as file:
                                            file.write(data)
                                        print('{} 下载成功'.format(true_file_name))
                                        MysqlUsage.insert_data(time_title=time_title, file_name=file_save_name,
                                                               email_type=0, email_account=from_address,
                                                               email_name=from_name, origin_name=true_file_name)
                                        sum_email_info['mail_list'].append(time_title)
                    # 处理 垫资邮件
                    elif keywords2 == value:
                        time_title = '{}{}'.format(keywords2, date_now)
                        # 检查库里情况===========================
                        check_response = MysqlUsage.check_attachment_exist(time_title)
                        if check_response:
                            sum_email_info['status'] = 1
                            # 遍历邮件内容
                            file_count = 1  # 控制多文件的文件名
                            for part in msg.walk():
                                # 分析附件名字
                                filename = part.get_filename()
                                if filename:
                                    # 文件名转码
                                    true_file_name = self.decode_str(filename)
                                    if 'xls' in true_file_name:
                                        # 发现附件 就解析附件
                                        data = part.get_payload(decode=True)
                                        file_save_name = '平安垫资--{}-{}.xls'.format(date_now, file_count)
                                        file_save_path = os.path.join(save_path, file_save_name)
                                        with open(file_save_path, 'wb') as file:
                                            file.write(data)
                                        print('{} 下载成功'.format(true_file_name))
                                        MysqlUsage.insert_data(time_title=time_title, file_name=file_save_name,
                                                               email_type=1, email_account=from_address,
                                                               email_name=from_name,origin_name=true_file_name)
                                        if time_title not in sum_email_info['mail_list']:
                                            sum_email_info['mail_list'].append(time_title)
                                        file_count += 1
                    else:
                        message = '发现新邮件,但邮件抬头里没有台账关键字,所以跳过'
                        print(message)
        return sum_email_info

    # 回信
    def return_excel(self,to_address):
        from email import encoders
        from email.header import Header
        from email.mime.text import MIMEText
        from email.utils import parseaddr, formataddr
        import smtplib

        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr(( \
                Header(name, 'utf-8').encode(), \
                addr.encode('utf-8') if isinstance(addr, unicode) else addr))

        from_addr = 'shiyugroup_cjj@163.com'
        password = raw_input('Password: ')
        to_addr = raw_input('To: ')
        smtp_server = raw_input('SMTP server: ')

        msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
        msg['From'] = _format_addr(u'Python爱好者 <%s>' % from_addr)
        msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
        msg['Subject'] = Header(u'来自SMTP的问候……', 'utf-8').encode()

        server = smtplib.SMTP(smtp_server, 25)
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()

    # 格式化输出
    def print_info(self, msg):
            # 邮件的From, To, Subject存在于根对象上:
        value = msg.get('Subject', '')
        if value:
            # 需要解码Subject字符串:
            value = self.decode_str(value)

        content_type = msg.get_content_type()
        if content_type == 'multipart/mixed':
            print(content_type)
            pass
        # if (msg.is_multipart()):
        #     # 如果邮件对象是一个MIMEMultipart,
        #     # get_payload()返回list，包含所有的子对象:
        #     parts = msg.get_payload()
        #     for n, part in enumerate(parts):
        #         print('%spart %s' % ('  ' * indent, n))
        #         print('%s--------------------' % ('  ' * indent))
        #         # 递归打印每一个子对象:
        #         self.print_info(part, indent + 1)
        # else:
        #     # 邮件对象不是一个MIMEMultipart,
        #     # 就根据content_type判断:
            # if content_type == 'text/plain' or content_type == 'text/html':
            #     # 纯文本或HTML内容:
            #     content = msg.get_payload(decode=True)
            #     # 要检测文本编码:
            #     charset = self.guess_charset(msg)
            #     if charset:
            #         content = content.decode(charset)
            #     print('%sText: %s' % ('  ' * indent, content + '...'))
            # else:
            #     print(content_type)
            #     # 不是文本,作为附件处理:
            #     print('%sAttachment: %s' % ('  ' * indent, content_type))


# 计算差价
def calculate_differ(now_data_dict, month_time):
    now_time = datetime.datetime.now()
    now_year = now_time.year
    now_month = month_time if month_time > 10 else '0{}'.format(month_time)
    strange_date = '{}{}'.format(now_year, now_month)
    info = MysqlAnalyzeUsage.get_info(month=strange_date, organization_name='聚仁')
    # 如果当月有数据
    if info:
        print('data exist')
        data_dict = {'month': now_month,
                     0: {'inPrice': 0,
                         'inCharges': 0},
                     2: {'inPrice': 0,
                         'inCharges': 0}
                     }
        for i in info:
            data_dict[i['inType']]['inPrice'] += i['inPrice']
            data_dict[i['inType']]['inCharges'] += i['inCharges']
            #data_dict[i['inType']]['count'] += i['countInfo']
        for i in [0, 2]:
            data_dict[i]['inPrice']  = now_data_dict[i]['inPrice'] - data_dict[i]['inPrice']
            data_dict[i]['inCharges'] = now_data_dict[i]['inCharges'] - data_dict[i]['inCharges']
            #data_dict[i]['count'] = now_data_dict[i]['count'] - data_dict[i]['count']
        return data_dict
    # 当月没有数据的话，直接入金额
    else:
        print('new month')
        now_data_dict['month'] = now_month
        return now_data_dict


#  查询 已有保单信息，避免重复入库
def get_all_info():
    print('正在获取 数据库里 所有保单信息')
    time_before = datetime.datetime.now()
    with mysql_analyze(get_type='list') as cursor:
        sql_content = 'select distinct writeDate,insurancePrice,insuranceNum from insurance_info'
        cursor.execute(sql_content)
        result = cursor.fetchall()
    time_after = datetime.datetime.now()
    print('总数据查询 用时 {}秒'.format((time_after-time_before).seconds))
    return list(result)


# 处理零售业务
class ProcessExcelRetail:
    def __init__(self, insurance_list):
        self.insurance_list = insurance_list

    # 读取 零售和过账不垫资 表格
    def load_excel_retail(self, excel_name):
        import re
        name_reg = re.compile('代理人-(\d{1,2})月')
        try:
            self.excel = open_workbook(excel_name)
            sheet_names = self.excel.sheet_names()
            for name in sheet_names:
                month = re.findall(name_reg, name)
                if month:
                    self.month = int(month[0])
                    break
        except Exception:
            self.excel = load_workbook(self.excel_name)
            sheet_names = self.excel.sheetnames
            print(sheet_names)
            input('')

    # 处理零售业务的表格
    def process_retail_data(self, sheet):
        company_name_dict = {'太平洋': '太平洋保险',
                                  '平安': '平安保险',
                                  '人保': '人保',
                                  '中保': '',
                                  '中华联合': '中华联合',
                                  '天安': '天安保险',
                                  '利宝': '利宝车险',
                                  '永诚': '永诚财产保险',
                                  '华安': '华安保险',
                                  '大地': '大地保险',
                                  '华泰': '华泰保险',
                                  '锦泰': '锦泰保险',
                                  '阳光': '阳光保险',
                                  '中煤': '中煤保险',
                                  '珠峰': '珠峰保险',
                                  '众安保险': '众安保险',
                                  '太保': '太平保险',
                                  '浙商': '浙商保险'
                                  }
        insurance_info_insert_list = []
        for i in range(sheet.nrows):
            row_value = sheet.row_values(i)
            if '保险公司' in row_value:
                print('检测到标题')
                head_row = i
                insur_sum_price_column = row_value.index('保费合计')
                insur_type_column   = row_value.index('保险公司分类')
                plate_num_column    = row_value.index('车牌号')
                owner_name_column   = row_value.index('被保险人')
                comm_price_column   = row_value.index('商业险')
                comm_rate_column    = row_value.index('商业险手续费率（收）')
                comm_income_column  = row_value.index('应收商业险手续费收入')
                comp_price_column   = row_value.index('交强险')
                comp_rate_column    = row_value.index('交强险手续费率（收）')
                comp_income_column  = row_value.index('应收交强险手续费收入')
                id_num_column       = row_value.index('身份证号码')
                try:
                    sign_date_column    = row_value.index('签单日期')
                except Exception:
                    sign_date_column = row_value.index('日期')
                comm_num_column     = row_value.index('商业保单号')
                comp_num_column     = row_value.index('交强保单号')
                insur_income_column = row_value.index('应收手续费收入合计')
                break
        insur_price = 0
        insur_income_price = 0
        # 条数统计，暂时不用
        count_times = 0
        status = 2
        uName = 'cjj_python'
        createTime = datetime.datetime.now()
        uid = 8
        flag = 1
        type_flag = 2
        sign = str(int(time.time()*1000))
        print('开始处理子信息')
        for i in range(head_row + 1, sheet.nrows):
            row_value = sheet.row_values(i)
            if row_value[0]:
                count_times += 1
                #后端数据处理
                organization = '四川聚仁'
                insuranceCompany = row_value[insur_type_column]
                company = company_name_dict[insuranceCompany]
                insuranceOrgnization = '四川聚仁保险代理有限公司'
                writeDate = xldate_as_datetime(row_value[sign_date_column],0)
                insurancePerson = row_value[owner_name_column]
                insuranceIdCard = row_value[id_num_column]
                licenseNumber = row_value[plate_num_column]
                comm_num = row_value[comm_num_column]
                comp_num = row_value[comp_num_column]
                if comm_num:
                    comm_price = Decimal(row_value[comm_price_column]).quantize(Decimal('0.00')) if row_value[comm_price_column] else Decimal('0.00')
                    if (writeDate, comm_price, comm_num) not in self.insurance_list:
                        comm_rate  = Decimal(row_value[comm_rate_column]).quantize(Decimal('0.00')) if row_value[comm_rate_column] else Decimal(0)
                        comm_income = row_value[comm_income_column]
                        insuranceType = 2
                        insuranceName = '机动车商业行业示范汽车保险'
                        single_info = (organization, company, insuranceCompany, insuranceOrgnization, writeDate, insurancePerson, insuranceIdCard, licenseNumber, comm_price, comm_rate, comm_income, status, uid, uName, createTime, flag, type_flag, insuranceType, insuranceName, comm_num, sign)
                        self.insurance_list.append((writeDate, comm_price, comm_num))
                        insurance_info_insert_list.append(single_info)
                if comp_num:
                    comp_price = Decimal(row_value[comp_price_column]).quantize(Decimal('0.00')) if row_value[comp_price_column] else Decimal('0.00')
                    if (writeDate, comp_price, comp_num) not in self.insurance_list:
                        comp_rate = Decimal(row_value[comp_rate_column]).quantize(Decimal('0.00')) if row_value[comp_rate_column] else Decimal(0)
                        comp_income = row_value[comp_income_column]
                        insuranceType = 1
                        insuranceName = '交强险'
                        single_info = (organization, company, insuranceCompany, insuranceOrgnization, writeDate, insurancePerson, insuranceIdCard, licenseNumber, comp_price, comp_rate, comp_income, status, uid, uName, createTime, flag, type_flag, insuranceType, insuranceName, comp_num, sign)
                        self.insurance_list.append((writeDate, comp_price, comp_num))
                        insurance_info_insert_list.append(single_info)
                # 前端数据处理
                if row_value[insur_sum_price_column] != '':
                    insur_price += float(row_value[insur_sum_price_column])
                if row_value[insur_income_column] != '':
                    insur_income_price += float(row_value[insur_income_column])
            else:
                break
        print('子信息处理完毕')
        MysqlAnalyzeUsage.insert_single_insur(insurance_info_insert_list)
        insur_price = Decimal(round(insur_price, 2) / 10000).quantize(Decimal('0.000000'))
        insur_income_price = Decimal(round(insur_income_price, 2) / 10000).quantize(Decimal('0.000000'))
        return [insur_price, insur_income_price, count_times]  # , count_times# 条数，暂时不用

    # 处理零售业务===============================================
    def load_sheet_retail(self):
        sheet1 = self.excel.sheet_by_name('代理人-{}月'.format(self.month))
        sheet2 = self.excel.sheet_by_name('批发其他-代理点-{}月'.format(self.month))
        print('正在处理 代理人表')
        data1 = self.process_retail_data(sheet1)
        print('正在处理 批发其他-代理点表')
        data2 = self.process_retail_data(sheet2)
        sum_data = []
        for i, value in enumerate(data1):
            sum_data.append(value + data2[i])
        return sum_data

    # 处理不垫资业务===============================================
    def load_sheet_unloan(self):
        sheet = self.excel.sheet_by_name('批发过账-{}月'.format(self.month))
        for i in range(sheet.nrows):
            row_value = sheet.row_values(i)
            if '保险公司' in row_value:
                head_row = i
                tax_column = row_value.index('应收手续费收入合计')
                break
        tax_price = 0
        # 条数统计，暂时不用
        count_times = 0
        for i in range(head_row + 1, sheet.nrows):
            row_value = sheet.row_values(i)
            if row_value[1]:
                count_times += 1
                if row_value[tax_column] != '':
                    tax_price += float(row_value[tax_column])
            else:
                break
        tax_price_min = Decimal(round(tax_price, 2) / 10000).quantize(Decimal('0.000000'))
        insur_price = Decimal((tax_price * 4) / 10000).quantize(Decimal('0.000000'))
        return [insur_price, tax_price_min, count_times]  # , count_times# 条数，暂时不用


# 处理垫资业务
class ProcessExcelLoan:
    def __init__(self, insurance_list):
        self.insurance_list = insurance_list

    def load_excel_info(self, excelName):
        excel = open_workbook(excelName)
        self.sheet = excel.sheet_by_index(0)

    def process_data(self):
        head_row = ''
        status = 2
        uName = 'cjj_python'
        createTime = datetime.datetime.now()
        uid = 8
        flag = 1
        type_flag = 1
        sign = str(int(time.time() * 1000))
        organization = '四川聚仁'
        company = '平安保险'
        insuranceCompany = '平安'
        insuranceOrgnization = '四川聚仁保险代理有限公司'
        insurance_info_insert_list = []
        loan_insur_price = 0
        loan_income = 0
        total_dict = {}
        for i in range(0, self.sheet.nrows):
            row_value = self.sheet.row_values(i)
            if '领导审批:' in row_value:
                break
            elif head_row:
                writeDate = parse(row_value[sign_date_column])
                date_format = writeDate.strftime("%Y-%m")
                if date_format not in total_dict:
                    total_dict[date_format] = {'loan_insur_price': 0,
                                               'loan_income': 0}
                insur_num = row_value[insur_num_column]
                insur_code_type = row_value[insur_type_column]
                if insur_code_type in ['C01', 'C00']:
                    insuranceType = '2'
                    insuranceName = '商业险'
                elif insur_code_type in ['C51', 'C50']:
                    insuranceType = '1'
                    insuranceName = '交强险'
                else:
                    insuranceType = '3'
                    insuranceName = insur_code_type
                owner_name = row_value[owner_name_column]
                insur_sum_price = Decimal(row_value[insur_sum_price_column]).quantize(Decimal('0.00'))
                income = Decimal(row_value[income_column]).quantize(Decimal('0.00'))
                total_dict[date_format]['loan_insur_price'] += insur_sum_price
                total_dict[date_format]['loan_income'] += income
                rate = Decimal(row_value[rate_column]).quantize(Decimal('0.00'))
                additional_info = row_value[additional_info_column]
                if (writeDate, insur_sum_price, insur_num) not in self.insurance_list:
                    single_info = (
                    organization, company, insuranceCompany, insuranceOrgnization, writeDate, owner_name, '', '',
                    insur_sum_price, rate, income, status, uid, uName, createTime, flag, type_flag, insuranceType,
                    insuranceName, insur_num, sign)
                    self.insurance_list.append((writeDate, insur_sum_price, insur_num))
                    insurance_info_insert_list.append(single_info)
            elif '支付申请号生成日期:' in row_value:
                for i in row_value:
                    try:
                        month_value = parse(i).month
                        excel_month = month_value if month_value > 9 else '0{}'.format(month_value)
                        print(excel_month)
                        break
                    except Exception:
                        pass
            elif '保单号' in row_value:
                print('检测到标题')
                head_row = i
                insur_num_column = row_value.index('保单号')
                insur_type_column = row_value.index('险种')
                owner_name_column = row_value.index('客户')
                insur_sum_price_column = row_value.index('保费收入')
                sign_date_column = row_value.index('出单时间')
                rate_column = row_value.index('本次比例%')
                income_column = row_value.index('本次手续费/经纪费(人民币)')
                additional_info_column = row_value.index('合作网点')
        MysqlAnalyzeUsage.insert_single_insur(insurance_info_insert_list)
        for month_date_format, value in total_dict.items():
            year_date, month_date = month_date_format.split('-')
            loan_insur_price = Decimal(value['loan_insur_price'] / 10000).quantize(Decimal('0.000000'))
            loan_income = Decimal(value['loan_income'] / 10000).quantize(Decimal('0.000000'))
            data_dict = {'month': month_date,
                         1: {'inPrice': loan_insur_price,
                             'inCharges': loan_income}}
            MysqlAnalyzeUsage.insert_data(data_dict, year_time=year_date)


# 主任务流程
def main_job():
    try:
        write_down_error('开始执行主任务')
        ruuning_time_count = 0
        sum_list = get_all_info()
        while True:
            mail = ProcessEmail()
            email_info = mail.get_excel_from_email()
            print(email_info)
            # print(sum_list)
            if email_info['status'] == 1:
                for email_title in email_info['mail_list']:
                    c = MysqlUsage.get_excel_info_from_mysql(email_title)
                    for excel_type, excel_name in c:
                        excel_path = os.path.join(save_path, excel_name)
                        print(excel_path)
                        # 零售 + 过账不垫资业务
                        if excel_type == 0:
                            print(excel_name, '====零售 + 过账不垫资业务')
                            # 初始化读取零售过账业务的模板
                            excel_process = ProcessExcelRetail(sum_list)
                            # 模板读表信息
                            excel_process.load_excel_retail(excel_path)
                            retail_data_inPrice, retail_data_inCharge, retail_data_count = excel_process.load_sheet_retail()
                            unloan_data_inPrice, unloan_data_inCharge, unloan_data_count = excel_process.load_sheet_unloan()
                            data_info = {0: {'inPrice': retail_data_inPrice,
                                             'inCharges': retail_data_inCharge,
                                             'count': retail_data_count},
                                         2: {'inPrice': unloan_data_inPrice,
                                             'inCharges': unloan_data_inCharge,
                                             'count': unloan_data_count}}
                            print('excel data:', data_info)
                            # 因为是累加式的数据，所以我们需要做个减法在录入
                            differ = calculate_differ(data_info, month_time=excel_process.month)
                            print('after data:', differ)
                            # 插入数据
                            MysqlAnalyzeUsage.insert_data(differ)
                        # 垫资业务
                        elif excel_type == 1:
                            print(excel_name, '====垫资业务')
                            # 初始化一个读取垫资的模板
                            excel_process = ProcessExcelLoan(sum_list)
                            # 模板读表
                            excel_process.load_excel_info(excel_path)
                            # 处理数据
                            excel_process.process_data()
            ruuning_time_count += 1
            next_time = '本次扫描结束，下次扫描时间 {}'.format(datetime.datetime.now() + timedelta(minutes=5))
            print(next_time)
            write_down_time(next_time)
            time.sleep(60 * 5)
    except Exception as e:
        print('发生未知错误，详情请看日志')
        write_down_error('run {} times '.format(ruuning_time_count) + '\n' + str(e))
        print('系统将在1小时后重启： {}'.format(datetime.datetime.now() + timedelta(minutes=60)))
        time.sleep(60 * 60)
        main_job()


if __name__ == '__main__':
    main_job()
