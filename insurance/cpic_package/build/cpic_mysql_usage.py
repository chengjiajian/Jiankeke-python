import pymysql
import contextlib
from build.cpic_settings import *
import re
# mysql的初始设置
@contextlib.contextmanager
def mysql(host='121.40.207.59', port=3306, user='root', passwd='MmlAN8kX', db=using_db, charset='utf8'):
    """
    :param host:
    :param port:
    :param user:
    :param passwd:
    :param db:
    :param charset:
    :return:
    """
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        yield cursor
    finally:
        conn.commit()
        cursor.close()
        conn.close()


# mysql各种方法
class MysqlUsage:
    def __init__(self):
        pass

    # 获取input里单条数据
    @classmethod
    def get_one_piece_query(cls):
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
            sql_content = "SELECT * from inquiry_input WHERE state=0 and companyName='太平洋保险' ORDER BY createTime LIMIT 1"
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

    # 获取一条支付或者核保信息
    @classmethod
    def get_one_piece_check_or_pay(cls):
        pass

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

# 格式化print
def json_print(dict_data):
    import json
    json_dicts = json.dumps(dict_data, ensure_ascii=False, indent=4)
    print(json_dicts)
