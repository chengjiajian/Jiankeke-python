import requests

s = requests.Session()
datas = {'lastYearAppPolicyNo':'',
'insuredPerson':'成佳健',
'vehiclePlateNo':'沪AEX529',
'vehicleEnginNo':'',
'vehicleVinNo':'',
'policyVersion':'1'}
dialog_url = r'http://yi.zhufengic.com/ipartner/insure/renewAppFormQuery.json'
#需要实时cookies！
dialog_headers={'Accept':'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.8',
'Content-Type':'application/x-www-form-urlencoded',
'Cookie':'JSESSIONID=Uzx0vhItoQ7Mvh-vz-3W2aKmHdKrKZ-zBfyOc35r7lm1uGXx5lUd!1287677248',
'Host':'yi.zhufengic.com',
'Origin':'http://yi.zhufengic.com',
'Referer':'http://yi.zhufengic.com/ipartner/insure/initInsureDirectly',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
'X-Requested-With':'XMLHttpRequest'}
response = requests.post(dialog_url,data=datas,headers=dialog_headers)
print(response.text)