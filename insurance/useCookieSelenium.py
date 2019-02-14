from selenium import webdriver
from pymongo import MongoClient
import time



conn = MongoClient('140.143.238.224', 27017)
conn['cookieDB'].authenticate('root','cjj941208',mechanism='SCRAM-SHA-1')
db = conn.cookieDB
cookiesTable = db.cookiesTable

options = webdriver.ChromeOptions()
options.add_argument('Cache-Control=max-age=0')
options.add_argument('Referer=https://pacas-login.pingan.com.cn/cas/PA003/ICORE_PTS/login')
options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36')
pacas = webdriver.Chrome(chrome_options=options)
pacas.get(r'https://www.baidu.com')
pacas.delete_all_cookies()
for i in cookiesTable.find({'name':'test'}):
    cookieList = i['value']

for cookie in cookieList:
    print(cookie)
    pacas.add_cookie({'name':cookie['name'],'value':cookie['value']})
print(pacas.get_cookies())
input('check')
pacas.get(r'https://icore-pts.pingan.com.cn/ebusiness/login.do')