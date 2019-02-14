import requests
from selenium import webdriver
import pymysql
from mysqlUsage import updateCookies,processCookie,getCookies


s = requests.Session()
#==========================初始化
s.headers
mainUrl = r'http://yi.zhufengic.com/ipartner/login/user'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
response = s.get(mainUrl,headers=headers)
print('mainUrl',s.cookies)

#==========================处理验证码
captchaUrl = r'http://yi.zhufengic.com/ipartner/captcha'
captchaResponse = s.get(captchaUrl,headers=headers).content
with open('captcha.jpg','wb') as fn:
    fn.write(captchaResponse)
captcha = input('captcha code=')
#==========================mac验证
macAddress = r'http://yi.zhufengic.com/ipartner/insure/macAddress.json'
macHeaders={'Accept':'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Connection':'keep-alive',
'Content-Length':'18',
'Content-Type':'application/x-www-form-urlencoded',
'Host':'yi.zhufengic.com',
'Origin':'http://yi.zhufengic.com',
'Referer':'http://yi.zhufengic.com/ipartner/login/user/login_error',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
'X-Requested-With':'XMLHttpRequest'}
mac_data={'LOGIN_ROLE':'vehicle'}
macResponse = s.post(macAddress,data=mac_data,headers=macHeaders)
#==========================登录验证
login_data = {'j_username':'51000273',
'j_password':'zf8848',
'_captcha_token_paramter':captcha,
'roleCode':'vehicle'}
login_headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Content-Length':'83',
'Content-Type':'application/x-www-form-urlencoded',
'Host':'yi.zhufengic.com',
'Origin':'http://yi.zhufengic.com',
'Referer':'http://yi.zhufengic.com/ipartner/login/user/login_error',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
login_url = r'http://yi.zhufengic.com/ipartner/j_spring_security_check?targeturl='
login_response = s.post(login_url,data=login_data,headers=login_headers)
mainPageUrl = r'http://yi.zhufengic.com/ipartner/index'
mainPageHeaders={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'yi.zhufengic.com',
'Referer':'http://yi.zhufengic.com/ipartner/login/user/login_error',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
mainResponse = s.get(mainPageUrl,headers=mainPageHeaders)
cookies = processCookie(s.cookies.get_dict())
updateCookies(1,cookies)
nowCookie = getCookies(1)['cookie']
print(nowCookie)
#==============跳转报价
outUrl = r'http://yi.zhufengic.com/ipartner/insure/initInsureDirectly'
outHeaders={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'yi.zhufengic.com',
'Cookie':'{}'.format(nowCookie),
'Referer':'http://yi.zhufengic.com/ipartner/index',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
outResponse = requests.get(outUrl,headers=outHeaders)
#print(outResponse.text)
#print(s.cookies.get_dict())
#===================根据车架号计算车价
calculate_url = r'http://yi.zhufengic.com/ipartner/queryVehicleList.json'
calculate_headers={'Accept':'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Connection':'keep-alive',
'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie':'{}'.format(nowCookie),
'Host':'yi.zhufengic.com',
'Origin':'http://yi.zhufengic.com',
'Referer':'http://yi.zhufengic.com/ipartner/insure/initInsureDirectly',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
'X-Requested-With':'XMLHttpRequest'}
calculate_data={'plateNo':'川YV1157',
'vinCode':'LGWEF4A58GF482916',
'fstRegYm':'2017-01-20',
'flag':'0',
'rows':'100',
'page':'1',
'sidx':'vehiclePrice',
'sord':'asc'}
calculate_response = requests.post(calculate_url,data=calculate_data,headers=calculate_headers)
print(calculate_response.json())