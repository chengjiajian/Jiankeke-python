from openpyxl import load_workbook
from xlrd import open_workbook
from email_process.usages.mysql_usage import *
import os
import pyexcel_xlsx
import re


# 分析词类
def processWord(word):
    word = str(word)
    vin_reg = re.compile('[A-Z0-9*]{17}')
    phone_reg = re.compile('1[0-9*]{10}')
    money_reg = re.compile('[0-9.]+')
    name_reg = re.compile('[\u4E00-\u9FA5]{2,4}')
    if len(word) == 17 and re.findall(vin_reg, word):
        return 'vin'
    elif re.findall(phone_reg, word):
        return 'phone'
    elif 4 >= len(word) >= 2 and re.findall(name_reg, word):
        return 'name'
    elif 6 >= len(word) >= 2 and re.findall(money_reg, word):
        try:
            word = str(float(word))
            if 6 >= len(word) >= 4:
                return 'price'
            else:
                return 'remark'
        except Exception as e:
            return 'remark'
    else:
        return 'remark'


# 分析列类
def analyzeSheet(values):
    from collections import Counter
    row_analyze_dict = {}
    name_list = []  # 建立防止重复名字字典
    nrows = len(values)
    for row_value in values:
        for i, word in enumerate(row_value):
            word_type = processWord(word)
            if word_type not in row_analyze_dict:
                row_analyze_dict[word_type] = [i, ]
            else:
                if word_type == 'name':
                    if word not in name_list:
                        name_list.append(word)
                        row_analyze_dict[word_type].append(i)
                else:
                    row_analyze_dict[word_type].append(i)
    result_dict = {}
    for key, value in row_analyze_dict.items():
        a = list(Counter(value).items())
        a.sort(key=lambda x: x[1], reverse=True)
        if a[0][1] > 0.9 * nrows:
            result_dict[key] = a[0][0]
    return result_dict


# 根据cationNumber 获取保单机构名字
def getCationNumberValue(cationNumber):
    with mysql_analyze('list') as cursor:
        sql_content = "select organization,inCompany from baoli_advances where cationNumber='{}'".format(cationNumber)
        #print(sql_content)
        cursor.execute(sql_content)
        result = cursor.fetchall()
    return result

# 分析excel
def processSheet(values, cationNumber, sheet_col_dict={}):
    basic_values = getCationNumberValue(cationNumber)
    if basic_values:
        basic_values = basic_values[0]
        organization = basic_values[0]
        insuranceCompany = company = basic_values[1]
        # 常量
        states = 5
        row_count = 0
        amount_count = 0
        uName = 'cjj_python_additional'
        uid = 8
        flag = 1
        status = 2
        type_flag = 1
        nesstype = 2
        postpone = 2
        insert_list = []  # 录入列表
        end_feature_list = ['合计：', '总计:', '合计', '', None]
        stop_hint = 0
        for row_value in values:
            if len(sheet_col_dict) > len(row_value):
                pass
            else:
                for end_feature in end_feature_list:
                    if end_feature in row_value:
                        stop_hint = 1
                        break
                if not stop_hint:
                    returnPrice = row_value[sheet_col_dict['price']]
                    try:
                        returnPrice = float(returnPrice)
                        ownerName = '' if 'name' not in sheet_col_dict else row_value[sheet_col_dict['name']]
                        row_count += 1
                        amount_count += returnPrice
                        remark = '' if 'remark' not in sheet_col_dict else row_value[sheet_col_dict['remark']]
                        detail_list = [company, insuranceCompany, organization, ownerName, returnPrice, remark, uName, uid, flag,
                                       status, type_flag, nesstype, states, postpone, cationNumber]  # 详细信息
                        insert_list.append(detail_list)  # 插表 的 列表
                    except Exception as e:
                        print(e)
        return [insert_list, row_count, amount_count]


if __name__ == '__main__':
    file_folder = r'C:\Users\ASUS\Desktop\批增表格范例'
    files = os.listdir(file_folder)
    for file in files:
        pure_file_name, extra_file_name = os.path.splitext(file)
        cationNumber = re.findall('SYCX[0-9]{13}', pure_file_name)
        if 'xls' in extra_file_name:
            excel_data_dict = pyexcel_xlsx.read_data(os.path.join(file_folder, file))
            if cationNumber:
                cationNumber = cationNumber[0]
                promt_count, money_count = 0, 0
                # 遍历页名， 行
                data_list = []
                for sheet_name, values in excel_data_dict.items():
                    # 建立文本区分字典
                    sheet_col_dict = analyzeSheet(values)
                    if 'price' in sheet_col_dict:
                        insert_list, row_count, amount_count = processSheet(values, cationNumber, sheet_col_dict)
                        promt_count += row_count
                        money_count += amount_count
                        data_list.extend(insert_list)
                MysqlAnalyzeUsage.update_advance_counts(promt_count, money_count, cationNumber)
                MysqlAnalyzeUsage.insert_additional_detail(data_list)