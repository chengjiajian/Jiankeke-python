import requests

s = requests.Session()
#第一步校验环节
checkUrl = r'http://pcis.jtxt.ejintai.com/cbs_auto_policy/j_spring_security_check'
checkHeader = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Content-Length':'41',
'Content-Type':'application/x-www-form-urlencoded',
'Host':'pcis.jtxt.ejintai.com',
'Origin':'http://pcis.jtxt.ejintai.com',
'Referer':'http://pcis.jtxt.ejintai.com/cbs_auto_policy/logon',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
checkResponse = s.post(url=checkUrl,data={
    'j_username':'V0006001',
    'j_password':'cb-6543210'
},headers=checkHeader)
#print(checkResponse.text)
#第二步校验mac
macUrl = r'http://pcis.jtxt.ejintai.com/cbs_auto_policy/toPage.do?name=mac'
macHeader = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'pcis.jtxt.ejintai.com',
'Referer':'http://pcis.jtxt.ejintai.com/cbs_auto_policy/logon',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
macResponse = s.get(url=macUrl,headers=macHeader)
#print(macResponse.text)
#第三步跳转页面
validateMacUrl = r'http://pcis.jtxt.ejintai.com/cbs_auto_policy/validateMAC.do'
validateHeader = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Content-Length':'5',
'Content-Type':'application/x-www-form-urlencoded',
'Host':'pcis.jtxt.ejintai.com',
'Origin':'http://pcis.jtxt.ejintai.com',
'Referer':'http://pcis.jtxt.ejintai.com/cbs_auto_policy/toPage.do?name=mac',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
validateResponse = s.post(url=validateMacUrl,data={'cMac':''},headers=validateHeader)
print(validateResponse.text)
#模拟登陆完成================================================================