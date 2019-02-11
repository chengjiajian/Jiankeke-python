import datetime
import base64
import requests
from usages.settings import admin_phone
from urllib.request import quote
# 记录错误信息的方法
def sendsSMS(phone=admin_phone):
    appkey = '5b6e27fbda7d20bfa0a2429919206c33'  # 您申请的短信服务appkey
    tpl_id = '65100'  # 申请的短信模板ID,根据实际情况修改
    code = datetime.datetime.now().strftime('%m%d%H%M')
    tpl_value = '#code#={}'.format(code)  # 短信模板变量,根据实际情况修改
    response = getValue(appkey, phone, tpl_id, tpl_value)  # 请求发送短信
    document = {
        'sid':response['result']['sid'],
        'code':code,
        'phoneNumber':phone,
        'sendTime':datetime.datetime.now()
    }
    return document

def getValue(appkey, mobile, tpl_id, tpl_value):
    sendurl = 'http://v.juhe.cn/sms/send'  # 短信发送的URL,无需修改
    Data = {"mobile" : mobile, #接收短信的手机号码
            "tpl_id" : tpl_id, #短信模板ID，请参考个人中心短信模板设置
            "tpl_value" : quote(tpl_value), #变量名和变量值对。
            "key" : appkey, #应用APPKEY(应用详细页查询)
            }
    response = requests.post(url=sendurl,data=Data).json()
    print(response)
    return response

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

if __name__ == '__main__':
    sendsSMS(17601228909)
    #sendsSMS()