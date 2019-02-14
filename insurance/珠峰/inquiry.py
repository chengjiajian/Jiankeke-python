import requests
import time
import re
import datetime
from pymongo import MongoClient
from insurance.usage import calculateTomorrowAndNextYear

conn = MongoClient('140.143.238.224', 27017)
conn['cookieDB'].authenticate('root','cjj941208',mechanism='SCRAM-SHA-1')
db = conn.cookieDB
cookiesTable = db.cookiesTable
inputData=db.inputData
carData = db.carData
responseData = db.responseData
for i in cookiesTable.find({'company_id': 1}):
    cookie = '{}={}'.format(i['cookie_name'], i['cookie_value'])


def postData():
    with open(r'C:\Users\ASUS\Desktop\postdata_shangye.txt','r') as fn:
        f = fn.readlines()
        data={}
        for i in f:
            c = i.split(':',1)
            key = re.sub('\.','`',c[0])
            value = re.sub('\n','',c[1])
            data['{}'.format(key)]=value
        return data
#=======================================计算实际车价的模块
def calculateValue(start_time, carprice):
    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    times = now.split("-")
    now_year = times[0]
    now_month = times[1]
    now_day = times[2]
    starttime = start_time
    starttimes = starttime.split("-")
    start_year = starttimes[0]
    start_month = starttimes[1]
    start_day = starttimes[2]
    years = int(now_year) - int(start_year)
    months = int(now_month) - int(start_month)
    sum_months = years * 12 + months
    if (int(start_day) - 1) - int(now_day) > 0:
        sum_months -= 1
    nowvalue = round(int(carprice) * (1 - (sum_months * 0.006)))
    return nowvalue

#=======================================计算车辆信息的模块
def inquiryCarPrice(plateNo,vinCode,fstRegYm='1900-01-01'):
    global cookie
    url = r'http://yi.zhufengic.com/ipartner/queryVehicleList.json'
    post_data={'plateNo':plateNo,
    'vinCode':vinCode,
    'fstRegYm':fstRegYm,
    'flag':'0',
    'rows':'100',
    'page':'1',
    'sidx':'vehiclePrice',
    'sord':'asc'}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
             'Cookie':cookie}
    response = requests.post(url,post_data,headers=headers)
    return response.json()

#=======================================续保查询（请填写号牌号码、发动机号和车架号其中的两项!）
def rewCar(vehiclePlateNo=None,vehicleEnginNo=None,vehicleVinNo=None):
    rew_data={'lastYearAppPolicyNo':'',
          'insuredPerson':'',
          'vehiclePlateNo':'vehiclePlateNo',
          'vehicleEnginNo':'vehicleEnginNo',
          'vehicleVinNo':'vehicleVinNo',
          'policyVersion':1
          }
    rew_headers={'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Connection':'keep-alive',
                'Content-Length':'122',
                'Content-Type':'application/x-www-form-urlencoded',
                'Cookie':cookie,
                'Host':'yi.zhufengic.com',
                'Origin':'http://yi.zhufengic.com',
                'Referer':'http://yi.zhufengic.com/ipartner/insure/initInsureDirectly',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
                'X-Requested-With':'XMLHttpRequest'}
    rew_url = r'http://yi.zhufengic.com/ipartner/insure/renewAppFormQuery.json'
    response = requests.post(rew_url,data=rew_data,headers=rew_headers)
    return response.json()

def calculateInsurance(data):
    headers={'Accept':'application/json, text/javascript, */*; q=0.01',
             'Accept-Encoding':'gzip, deflate',
             'Accept-Language':'zh-CN,zh;q=0.8',
             'Content-Type':'application/x-www-form-urlencoded',
             'Cookie': cookie,
             'Host':'yi.zhufengic.com',
             'Origin':'http://yi.zhufengic.com',
             'Referer':'http://yi.zhufengic.com/ipartner/insure/initInsureDirectly',
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
             'X-Requested-With':'XMLHttpRequest'}
    post_data=data
    urls = r'http://yi.zhufengic.com/ipartner/core/premiumcal.json'
    response = requests.post(urls,post_data,headers=headers)
    return response.json()

fuelType={'汽油':0,
          'xxx':1}

info={'车主姓名':'尹露杰',
      '投保人类型（个人1，团体2）':'1',
      '证件类型（居民身份证01，护照02，军人证03，驾驶证04，港澳台同胞证05，其他99':'01',
      '证件号':'513722199301050512',
      '手机号':'17601228908',
'车牌号':'川YV1157',
'车架号':'LGWEF4A58GF482916',
'发动机号':'',
'初登日期':'2017-01-20',
'车牌颜色':'01',
      }
info={'车主姓名':'成佳健',
      '投保人类型（个人1，团体2）':'1',
      '证件类型（居民身份证01，护照02，军人证03，驾驶证04，港澳台同胞证05，其他99':'01',
      '证件号':'310225199412086018',
      '手机号':'17601228908',
'车牌号':'沪AEX529',
'车架号':'LVSHEFAC49F437951',
'发动机号':'',
'初登日期':'2009-12-28',
'车牌颜色':'01',
      }
if __name__ == '__main__':
    for i in inputData.find():
        a = i
        aa=inquiryCarPrice(info['车牌号'],info['车架号'],info['初登日期'])
        a.pop('type')
        a.pop('_id')
        data = eval(re.sub('`','.',str(a)))
        CarData=aa['vhlList'][0]
        nowDate = datetime.datetime.now().strftime('%Y-%m-%d')
        tommorow,nextYear = calculateTomorrowAndNextYear()
        firstRst = info['初登日期']
        nowValue = calculateValue(firstRst, CarData['vehiclePrice'])#计算现存价值
        data['vehDTO.issueDate']=nowDate
        data['commPolDTO.startDate']=tommorow
        data['commPolDTO.endDate']=nextYear
        data['compPolDTO.startDate']=tommorow
        data['compPolDTO.endDate']=nextYear
        data['appName']=data['insuredMan.insuredName']=data['vehDTO.vehicleOwner']=data['vehDTO.regOwner']=data['vehTax.taxPayerName']=info['车主姓名']
        data['appType']=data['insuredMan.appType']=data['vehDTO.ownerType']=info['投保人类型（个人1，团体2）']
        data['appCertiType']=data['insuredMan.insuredCertiType']=data['vehDTO.idcardTyp']=data['vehTax.idType']=info['证件类型（居民身份证01，护照02，军人证03，驾驶证04，港澳台同胞证05，其他99']
        data['appCertiCode']=data['insuredMan.insuredCertiCode']=data['vehDTO.idNo']=data['vehTax.taxpayerNo']=info['证件号']
        data['appBirthDate']=data['insuredMan.insuredBirthDate']='{}-{}-{}'.format(info['证件号'][7:11],info['证件号'][11:13],info['证件号'][13:15]),
        data['appCellphone']=data['insuredMan.insuredCellphone']=info['手机号']
        data['vehDTO.plateNo']=info['车牌号']
        data['vehDTO.vin']=info['车架号']
        data['vehDTO.engNo']=CarData['engineNumber']
        data['vehDTO.fstRegYm']=data['vehDTO.ticketDate']=data['vehDTO.certDate']=firstRst
        data['vehDTO.modelNme']=data['vehDTO.noticeType']=data['vehDTO.curModelNme']= CarData['vehicleName']
        data['vehDTO.modelCde']=data['vehDTO.jyModelCode']=CarData['vehicleId']
        data['vehDTO.limitLoadPerson']=CarData['vehicleSeat']
        data['']=fuelType[CarData['fuelType']]
        data['vehDTO.newPurchaseValue']=CarData['vehiclePrice']
        data['vehDTO.actualValue']=data['vehDTO.negotiatedActualValue']=data['vehDTO.consultPrice']=nowValue
        data['vehDTO.carBrand']=CarData['vehicleBrand']
        data['vehDTO.displacement']=CarData['vehicleDisplacement']
        data['vehDTO.plateColor']=info['车牌颜色']
        data['vehTax.vehicleQuality']=CarData['curbWeightMin']
        data['commerceList[0].insuredAmt']=data['commerceList[2].insuredAmt']=data['commerceList[9].insuredAmt']=nowValue
        data['vehTax.displacement']=CarData['vehicleDisplacement']/1000
        data['vehTax.taxPeriod']="{}-01-01".format(datetime.datetime.now().year)
        #print(data)
        responseData.insert(calculateInsurance(data))
