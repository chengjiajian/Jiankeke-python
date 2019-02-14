# coding=gbk
import contextlib
import pymysql
import datetime
from decimal import *

offical_info = {'shop_list': 'buyer',
                'name_list': 'buyer_info',
                'pre_list': 'pre_order'}
test_info = {'shop_list': 'buyer_copy',
             'name_list': 'buyer_info_copy',
             'pre_list': 'pre_order_copy'}
using_server = offical_info
#using_server = test_info
buyer_db = using_server['shop_list']
buyer_info_db = using_server['name_list']
pre_order_db = using_server['pre_list']

reverse_type_dict = {'衣服': '5',
                     '零食': '4',
                     '专柜': '3',
                     '药妆': '2',
                     '日上':'1'}

type_dict = {'5': '衣服',
             '4': '零食',
             '3': '专柜',
             '2': '药妆',
             '1': '日上'}

#now_trip_name = '20181004大阪'
now_trip_name = '20181219东京'

@contextlib.contextmanager
def mysql(get_type='dict', host='140.143.238.224', port=3306, user='root', passwd='941208', db='car_data', charset='utf8'):
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

def getTypeList():
    type_dict = {'5': '衣服',
                 '4': '零食',
                 '3': '专柜',
                 '2': '药妆',
                 '1': '日上'}
    with mysql(get_type='list') as cursor:
        sql_content1 = "SELECT distinct productType FROM {} order by creatTime DESC".format('pre_order')
        c = cursor.execute(sql_content1)
        result = cursor.fetchall()
        result = [type_dict[a[0]] for a in result]
    return result


def getPreBuyerInfo():
    with mysql() as cursor:
        sql_content1 = "select productName,productPrice,sum(productCount),productType from {} WHERE tripName='{}' GROUP BY productName,productType ".format(pre_order_db, now_trip_name)
        c = cursor.execute(sql_content1)
        result1 = cursor.fetchall()
    data_dict = {}
    for i in result1:
        productType_name = type_dict[i['productType']]
        if productType_name not in data_dict:
            data_dict[productType_name] = [{'productName': i['productName'],
                                            'productPrice':i['productPrice'],
                                            'productCount': i['sum(productCount)']},]
        else:
            data_dict[productType_name].append({'productName': i['productName'],
                                                'productPrice': i['productPrice'],
                                                'productCount': i['sum(productCount)']})
    return data_dict


def confirmPreProducts(product_name, product_count):
    with mysql() as cursor:
        sql_content = 'SELECT * from {} where productName="{}" and tripName="{}" and remainCount>0 '.format(pre_order_db, product_name, now_trip_name)
        cursor.execute(sql_content)
        result = cursor.fetchall()
        index_count = 0
        finish_id = []
        buyer_insert_list = []
        while index_count < len(result):
            pre_value = result[index_count]
            id = pre_value['id']  # 此条id
            productCount = pre_value['productCount']  # 需要买多少
            buyerName = pre_value['buyerName']  # 买家名
            productName = pre_value['productName']  # 产品名
            productPrice = pre_value['productPrice']
            tripName = pre_value['tripName']
            picturePath = pre_value['picturePath'] if pre_value['picturePath'] else 'default.png'
            # 如果提交数量不足以抵消此人的购买数
            if product_count - productCount < 0:
                sql_content = 'UPDATE {} SET remainCount={} where id={}'.format(pre_order_db, productCount-product_count, id)
                cursor.execute(sql_content)
                insert_value = [buyerName, productName, product_count, productPrice, picturePath, tripName]
                buyer_insert_list.append(insert_value)  # 转存到买到的地方
                break
            # 相反，够的话
            else:
                finish_id.append(id)  # 完成列表
                insert_value = [buyerName, productName, productCount, productPrice, picturePath, tripName]
                buyer_insert_list.append(insert_value)  # 转存到买到的地方
                product_count -= productCount  # 减少总量
            index_count += 1
        if finish_id:
            if len(finish_id) > 1:
                sql_content = 'UPDATE {} SET remainCount=0 where id in {}'.format(pre_order_db, tuple(finish_id))
            else:
                sql_content = 'UPDATE {} SET remainCount=0 where id={}'.format(pre_order_db, finish_id[0])
            cursor.execute(sql_content)
            insertManyBuyerInfo(buyer_insert_list)

# 批量 新建买家信息
def insertManyBuyerInfo(data_list):
    with mysql() as cursor:
        sql_content = "INSERT INTO {}(buyerName,productName,productCount,productPrice,picturePath,tripName) VALUES \
(%s,%s,%s,%s,%s,%s)".format(buyer_db)
        c = cursor.executemany(sql_content, data_list)


a = '''SERVICE_TYPE=ACTION_SERVIC&CODE_TYPE=UTF-8&BEAN_HANDLE=baseAction&ACTION_HANDLE=perform&SERVICE_NAME=policyQueryBizAction&SERVICE_MOTHOD=qryUnderwirttenStateList&DW_DATA=<data><dataObjs type="MULTI_SELECT"  dwName="policy.app_auditing_state_DW" dwid="dwid0.009217914922014514" pageCount="1" pageNo="1" pageSize="11" rsCount="0"/><filters colsInOneRow="2" dwName="policy.app_auditing_state_DW"><filter isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="true" name="null" width="150"/><filter checkType="Text" class="input400 mustinput read" codeKind="codeKind" codelistname="dataDptSet" cols="2" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="51978201" isGroupBegin="true" isGroupEnd="false" isHidden="false" isNullable="false" isReadOnly="false" isRowBegin="false" name="CDptCde" operator="2" rows="1" tableName="" title="机构部门" type="issSelect" width="430" issExtValue="51978201  青羊车商"/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="1" isGroupBegin="false" isGroupEnd="true" isHidden="false" isRowEnd="true" name="LoadSub" operator="2" rows="1" tableName="" title="包含下级" type="checkbox" width="70" issExtValue="1"/><filter isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="true" name="null" width="150"/><filter checkType="Select" codeKind="codeKind" codelistname="NewDataPermKind_List" cols="2" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="03" isGroupBegin="true" isGroupEnd="false" isHidden="false" isRowBegin="false" name="CKindNo" operator="*" relate="CProdNo" rows="1" title="产品" type="issSelect" width="160" issExtValue="03 机动车辆保险"/><filter checkType="Text" codeKind="codeKind" codelistname="NewDataPermProd_List" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="false" isGroupEnd="true" isHidden="false" isRowEnd="true" name="CProdNo" operator="4" rows="1" title="" type="issSelect" width="268" issExtValue="请选择"/><filter isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="true" name="null" width="150"/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="false" isRowEnd="false" maxLength="100" name="CAppNo" operator="8" rows="1" tableName="" title="投保申请单号" type="input" width="250" issExtValue=""/><filter checkType="Date" cols="1" dataType="DATE" dateFormat="yyyy-MM-dd" defaultValue="2018-09-01" isGroupBegin="true" isGroupEnd="false" isHidden="false" isNullable="false" label="投保申请日期" name="TAppTmStart" onchange="PlyDateChange(this, getFilterByObj(this, 'TAppTmEnd'),7);" operator="3" rows="1" tableName="" title="投保申请日期" type="input" width="115" issExtValue="2018-09-01"/><filter checkType="Date" cols="1" dataType="DATE" dateFormat="yyyy-MM-dd" defaultValue="2018-09-07" isGroupBegin="false" isGroupEnd="true" isHidden="false" isNullable="false" isRowEnd="true" name="TAppTmEnd" onchange="PlyDateChange(getFilterByObj(this, 'TAppTmStart'), this,7,1);" operator="1" promptInfo="投保单查询打印的投保申请日期不能为空。" rows="1" tableName="" title="-" type="input" width="115" issExtValue="2018-09-07"/><filter isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="true" name="null" width="150"/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="false" isRowEnd="false" maxLength="100" name="CPlateNo" operator="2" rows="1" tableName="" title="车牌号码" type="input" width="250" issExtValue=""/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowEnd="true" maxLength="100" name="CEngNo" operator="2" rows="1" tableName="" title="发动机号" type="input" width="250" issExtValue=""/><filter isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="true" name="null" width="150"/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="false" isRowEnd="false" maxLength="100" name="CFrmNo" operator="2" rows="1" tableName="" title="车架号" type="input" width="250" issExtValue=""/><filter checkType="Text" codeKind="yes_no" codelistname="SysStaDict_List" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="0" isGroupBegin="true" isGroupEnd="false" isHidden="false" isRowEnd="true" maxLength="100" name="CIsIsuMrk" operator="2" rows="1" tableName="" title="是否已生成保单" type="issSelect" width="100" issExtValue="否"/><filter isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="true" name="null" width="150"/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="true" isGroupEnd="true" isHidden="false" isRowBegin="false" isRowEnd="false" maxLength="100" name="CServiceCode" operator="8" rows="1" tableName="" title="服务代码" type="input" width="250" issExtValue=""/><filter checkType="select" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="true" isGroupEnd="false" isHidden="false" name="CAppInsName" operator="*" optioncontent="1$~$投保人名称$~$2$~$被保人名称$~$3$~$车主名称" rows="1" title="名称" type="select" width="100" issExtValue=""><option value="1">投保人名称</option><option value="2">被保人名称</option><option value="3">车主名称</option></filter><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="" isGroupBegin="false" isGroupEnd="false" isHidden="false" name="CAppNme" operator="*" relate="CAppNme" rows="1" title="" type="input" width="150" issExtValue=""/><filter checkType="Text" cols="1" dataType="STRING" dateFormat="yyyy-MM-dd HH:mm" defaultValue="1" isGroupBegin="false" isGroupEnd="true" isHidden="false" isRowEnd="true" name="CQueryFlag" operator="*" optioncontent="1$~$精确查询$~$2$~$前匹配$~$3$~$后匹配$~$4$~$前后匹配" rows="1" title="查询模式" type="select" width="110" issExtValue="1"><option value="1">精确查询</option><option value="2">前匹配</option><option value="3">后匹配</option><option value="4">前后匹配</option></filter></filters></data>&HELPCONTROLMETHOD=common&SCENE=UNDEFINED&BIZ_SYNCH_LOCK=&BIZ_SYNCH_MODULE_CODE=&BIZ_SYNCH_NO=&BIZ_SYNCH_DESC=&BIZ_SYNCH_CONTINUE=false&CUST_DATA=sysCde=POLY_AUTO###scene=A'''