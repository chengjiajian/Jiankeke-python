from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
import base64
import requests

def dpi_request(path,codeType):
    try:
        #print('接口调用成功,本接口为狮域购买的图片识别接口\n仅供测试使用，如果要投入正式使用请更改')
        with open(path, 'rb') as s:
            ls_f = base64.b64encode(s.read())  # 读取文件内容，转换为base64编码
            url = "http://op.juhe.cn/vercode/index"
            params = {
                "key": '889fdc9bc1d1e5e678e52623b23c1f7a',  # 您申请到的APPKEY
                "codeType": codeType,
                "base64Str": ls_f,  # 图片文件
                "dtype": "",  # 返回的数据的格式，json或xml，默认为json
            }
            f = requests.post(url=url, data=params, timeout=120)
            res = f.json()
            print('res', res)
            if res:
                error_code = res["error_code"]
                if error_code == 0:
                    # 成功请求
                    print(res["result"])
                else:
                    print("%s:%s" % (res["error_code"], res["reason"]))
            else:
                print("request api error")
        return res["result"]
    except Exception as e:
        dpi_request(path, codeType)


def cropValidcode(savePath, driver, imageElement, validType):
    driver.save_screenshot(savePath)
    location = imageElement.location  # 获取验证码x,y轴坐标
    size = imageElement.size  # 获取验证码的长宽
    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
    i = Image.open(savePath)  # 打开截图
    frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save(savePath)  # 保存接下来的验证码图片 进行打码
    validcodeNum = dpi_request(savePath,validType)
    return validcodeNum


class mainJob:
    def __init__(self, wbdriver='Phantomjs'):
        if wbdriver == 'Phantomjs':
            self.driver = webdriver.PhantomJS()
        elif wbdriver == 'Chrome':
            self.driver = webdriver.Chrome()


    def login(self):
        try:
            error_dict = {}
            self.driver.get(r'http://issue.cpic.com.cn/ecar/view/portal/page/common/login.html')
            username    = self.driver.find_element_by_xpath(r'//*[@id="j_username"]')
            username.clear()
            username.send_keys('w_CD_VSD_001')
            self.driver.find_element_by_xpath(r'//*[@id="_password"]').send_keys('Cpic1218')
            validCode   = self.driver.find_element_by_xpath(r'//*[@id="verifyCode"]')
            imageLocate = self.driver.find_element_by_xpath(r'//*[@id="capImg"]')
            savePath    = 'validcode.png'
            validcode   = cropValidcode(savePath=savePath, driver=self.driver, imageElement=imageLocate, validType=1004)
            validCode.send_keys(validcode)
            self.driver.find_element_by_xpath(r'//*[@id="j_login"]').click()
            while True:
                pageContent = self.driver.page_source
                if '终端及经办人选择' in pageContent:
                    if '何爱国' in pageContent:
                        break
                    time.sleep(1)
                elif '验证码错误' in pageContent or '用户名或密码错误' in pageContent or '验证码不能为空' in pageContent:
                    self.login()
            self.driver.find_element_by_xpath(r'//*[@id="__agent_2__"]').click()
            self.driver.find_element_by_xpath(r'//*[@id="loginBtn"]').click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'width-2')))
            time.sleep(1)
        except Exception as e:
            print(e)


    def refresh(self):
        self.driver.refresh()
        cookieList = self.driver.get_cookies()
        str_list = []
        for cookie in cookieList:
            str_list.append('{}={}'.format(cookie['name'], cookie['value']))
        cookies = ';'.join(str_list)
        return cookies

    def test(self):
        pass
