from selenium import webdriver
from pymongo import MongoClient
from PIL import Image
from 爬虫工具.testapi import dpi_request
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def rollingInTheDeep():
    global pacas
    js = "var q=document.body.scrollTop=100000"
    pacas.execute_script(js)

conn = MongoClient('140.143.238.224', 27017)
conn['cookieDB'].authenticate('root','cjj941208',mechanism='SCRAM-SHA-1')
db = conn.cookieDB
cookiesTable = db.cookiesTable
#打开浏览器
pacas = webdriver.Chrome()
#调整页面大小
pacas.set_window_size(1280,800)

#访问首页
pacas.get(r'https://pacas-login.pingan.com.cn/cas/PA003/ICORE_PTS/login')
#密码登录
username = pacas.find_element_by_xpath(r'//*[@id="username"]')
pwd = pacas.find_element_by_xpath(r'//*[@id="password"]')
validcode = pacas.find_element_by_xpath(r'//*[@id="randCodeText"]')
validImage = pacas.find_element_by_xpath(r'//*[@id="randCode"]')
#保存验证码打码
imgSavePath = r'C:\Users\ASUS\Desktop\python\insurance\test.png'
pacas.save_screenshot(imgSavePath)
location = validImage.location  # 获取验证码x,y轴坐标
size = validImage.size  # 获取验证码的长宽
print(location)
print(size)
#input('locate')
rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
          int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
i = Image.open(imgSavePath)  # 打开截图
frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
frame4.save(imgSavePath) # 保存接下来的验证码图片 进行打码

validcodeNum = dpi_request(imgSavePath)

username.send_keys('YLJRGX-00001')
pwd.send_keys('ZZZZZ000')
validcode.send_keys(validcodeNum)
LoginBotton = pacas.find_element_by_xpath(r'//*[@id="loginButton"]')
LoginBotton.click()
try:
    element = WebDriverWait(pacas,10).until(
        EC.presence_of_element_located((By.ID, "mainWrap"))
    )
except Exception as e:
    print()
    input("error")
changeHref = pacas.find_element_by_xpath(r'//*[@id="nav"]/li[3]/a')
changeHref.click()

while True:
    pacas.switch_to.frame('main_c')
    botton = pacas.find_element_by_xpath(r'//*[@id="toibcsWriter"]')
    time.sleep(1)
    botton.click()
    windows = pacas.window_handles
    pacas.switch_to.window(windows[1])
    element = WebDriverWait(pacas, 10).until(
        EC.presence_of_element_located((By.ID, "mainNav"))
    )
    print('located')
    time.sleep(2)
    pacas.switch_to.frame('main')
    botton = pacas.find_element_by_xpath(r'//*[@id="mainContent"]/div[2]/div[2]/form/div[2]/div/div/button[1]')
    botton.click()
    cookieDict = pacas.get_cookies()
    element = WebDriverWait(pacas, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'quotationNo'))
    )
    print('ready to start')
    time.sleep(5)
    rollingInTheDeep()
    #交强险
    botton = pacas.find_element_by_xpath(r'//*[@id="taxInfoTitle"]/div/div/label/input')
    botton.click()
    #商业险
    botton = pacas.find_element_by_xpath(r'//*[@id="auto0Div"]/div/div[3]/div/div[2]/form[2]/div/div[1]/div[1]/div/div[1]/label/input')
    botton.click()
    time.sleep(2)
    #<td>机动车损失保险</td>
    botton = pacas.find_element_by_xpath(r'//*[@id="c01PlanTable"]/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/input')
    botton.click()
    rollingInTheDeep()
    time.sleep(20)
    # cookiesTable.update({'name':'test'},{'$set':{'value':cookieDict}})
    # input('c')
    # time.sleep(30)
    print(time.time())
    pacas.close()
    pacas.switch_to.window(windows[0])