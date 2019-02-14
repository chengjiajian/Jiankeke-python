# 放所有工具方法
import base64
from PIL import Image
import requests
import datetime

# 记录错误信息
def write_down_error(message):
    with open('errorMessage.txt', 'a', encoding='utf-8') as fn:
        fn.write('{} \n {} \n ==============================================='.format(datetime.datetime.now(), message))

# 记录错误信息
def write_down_error_check_or_pay(message):
    with open('errorMessage_check_or_pay.txt', 'a', encoding='utf-8') as fn:
        fn.write('{} \n {} \n ==============================================='.format(datetime.datetime.now(), message))



# 验证码 校验 接口
def dpi_request(path, code_type=1004):
    try:
        print('正在分析验证码')
        with open(path, 'rb') as s:
            print(path)
            ls_f = base64.b64encode(s.read())  # 读取文件内容，转换为base64编码
            params = {
                "key": '889fdc9bc1d1e5e678e52623b23c1f7a',  # 您申请到的APPKEY
                "codeType": code_type,
                "base64Str": ls_f,  # 图片文件
                "dtype": "",  # 返回的数据的格式，json或xml，默认为json

            }
        url = "http://op.juhe.cn/vercode/index"
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
        return dpi_request(path)


# 验证码截取 + 校验
def crop_valid_code(save_path, driver, image_element):
    driver.save_screenshot(save_path)
    #('')
    location = image_element.location  # 获取验证码x,y轴坐标
    location["x"] = 1262
    location['y'] = 387
    size = image_element.size  # 获取验证码的长宽
    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']+10),
              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
    i = Image.open(save_path)  # 打开截图
    frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save(save_path)  # 保存接下来的验证码图片 进行打码
    validcode_num = dpi_request(save_path)
    return validcode_num

# 支付码
def crop_pay_picture(save_path, driver, image_element):
    driver.save_screenshot(save_path)
    location = image_element.location  # 获取验证码x,y轴坐标
    size = image_element.size  # 获取验证码的长宽
    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
    i = Image.open(save_path)  # 打开截图
    frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save(save_path)  # 保存接下来的验证码图片 进行打码
    validcode_num = dpi_request(save_path)
    return validcode_num

if __name__ == '__main__':
    pass