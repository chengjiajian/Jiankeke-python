import contextlib
import pymysql
from usages.settings import insert_server, info_server, using_data
import datetime
from decimal import *
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

    # 插表  大数据 非单条
    @classmethod
    def insert_data(cls, data, organization_name='聚仁', year_time='2018', file_name=''):
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
                        now_month, now_day, 0, file_name)
                    insert_list.append(single_info)
                else:
                    print('两数字都为0')
            if insert_list:
                with mysql_analyze() as cursor:
                    sql_content = "INSERT INTO insurance_analy(inMonth, inOrganization, inType, inPrice, inCharges, inRate\
            , creatTime, state, month, day, countInfo,fileName) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    c = cursor.executemany(sql_content, insert_list)
                print('数据：{}'.format(insert_list))
            else:
                print('没有需要入库的保费/手续费数据')
        else:
            print('没取到数据')

    # 批量 插入 单条数据
    @classmethod
    def insert_single_insur(cls, data_list):
        if data_list:
            #print(data_list)
            print('正在将 {} 条保单数据数据入库'.format(len(data_list)))
            with mysql_analyze() as cursor:
                sql_content = "INSERT INTO {}(organization, company, insuranceCompany, insuranceOrgnization, writeDate, insurancePerson,insuranceIdCard, licenseNumber, insurancePrice, insuranceRate, returnPrice, status, uid, uName, createTime, flag, type, insuranceType, insuranceName, insuranceNum, sign, cationNumber, payment, payrate, nesstype, states, contractId, proName) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(info_server)
                #print(sql_content)
                c = cursor.executemany(sql_content, data_list)
        else:
            print('没有 单条的 数据可以入库')

    # 获取当前的rate值
    @classmethod
    def get_ratio_info(cls, company_name):
        with mysql_analyze() as cursor:
            sql_content = "SELECT payRatio,incomeRatio,noCarRatio from baoli_rate WHERE company='{}' ORDER by id DESC LIMIT 1".format(company_name)
            c = cursor.execute(sql_content)
            infos = cursor.fetchall()
        return infos

    # 垫款数据 入库
    @classmethod
    def insert_loan_info(cls, single_list, db_name='baoli_advances_middle'):
        if single_list:
            print('正在将 垫款数据 入库')
            with mysql_analyze() as cursor:
                sql_content = "INSERT INTO {}(cationDate, organization, inCompany, cationNumber, amount, policyCount, advance, state, contractId, proName) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(db_name)
                c = cursor.executemany(sql_content, single_list)
        else:
            print('没有 垫款数据 可以入库')

    # 查询 项目名称
    @classmethod
    def get_proName_by_contractId(cls, contractId):
        with mysql_analyze() as cursor:
            sql_content = "SELECT proName from contract WHERE contractId='{}'".format(contractId)
            c = cursor.execute(sql_content)
            result = cursor.fetchall()
        if result:
            result = result[0]
        else:
            result = '没有找到'
        return result

    @classmethod
    def process_middle_to_advance(cls):
        with mysql_analyze() as cursor:
            sql_content = 'SELECT * from baoli_advances_middle where cationNumber in (select distinct cationNumber from baoli_advances_middle as tmp1) and cationNumber not in (select cationNumber from (select cationNumber from baoli_advances) as tmp2)'
            cursor.execute(sql_content)
            result = cursor.fetchall()
            if result:
                data_dict = {}
                for i in result:
                    cationSign = i['cationNumber']
                    if cationSign not in data_dict:
                        data_dict[cationSign] = {'cationDate': i['cationDate'],
                                                 'organization': i['organization'],
                                                 'company': i['inCompany'],
                                                 'contractId': i['contractId'],
                                                 'proName': i['proName'],
                                                 'amount': i['amount'],
                                                 'policyCount': i['policyCount'],
                                                 'advance': i['advance']}
                    else:
                        data_dict[cationSign]['amount'] += i['amount']
                        data_dict[cationSign]['policyCount'] += i['policyCount']
                        data_dict[cationSign]['advance'] += i['advance']
                for cationSign, value in data_dict.items():
                    cationDate = value['cationDate']
                    organization = value['organization']
                    company = value['company']
                    contractId = value['contractId']
                    proName = value['proName']
                    amount = value['amount']
                    policyCount = value['policyCount']
                    advance = value['advance']
                    advance_insert_list = [(cationDate, organization, company, cationSign, amount, policyCount, advance, 4, contractId, proName), ]
                    MysqlAnalyzeUsage.insert_loan_info(advance_insert_list, db_name='baoli_advances')

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
            sql_content = "select emailType,emailTitle from attachmentData where emailTitle='{}'".format(
                email_title)
            cursor.execute(sql_content)
            result = cursor.fetchall()
        return result


# 计算差价
def calculate_differ(now_data_dict, month_time):
    now_time = datetime.datetime.now()
    now_year = now_time.year
    now_month = month_time if month_time >= 10 else '0{}'.format(month_time)
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
        sql_content = 'select writeDate,returnPrice,insuranceNum from {}'.format(info_server)
        cursor.execute(sql_content)
        result = cursor.fetchall()
    time_after = datetime.datetime.now()
    print('总数据查询 用时 {}秒'.format((time_after-time_before).seconds))
    return list(result)

def get_receive_list(type='normal'):
    with mysql(get_type='list') as cursor:
        if type == 'normal':
            sql_content = 'select email_account from sendAccounts where account_type="{}"'.format(using_data['receive_list_type'])
        else:
            sql_content = 'select email_account from sendAccounts where account_type="-2"'
        cursor.execute(sql_content)
        result = cursor.fetchall()
    if result:
        result = [x[0] for x in result]
    return result

if __name__ == '__main__':
    MysqlAnalyzeUsage.process_middle_to_advance()