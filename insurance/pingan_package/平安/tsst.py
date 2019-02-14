def test():
    generators = (x for x in range(10))
    for i in generators:
        yield i

def logger(func):
    def inner(*args, **kwargs):  # 1
        print("Arguments were: %s, %s" % (args, kwargs))
        return func(*args, **kwargs)  # 2
    return inner

@logger
def foo1(x, y=1):
    return x * y


class test:

    def __init__(self):
        print('s')

    @classmethod
    def proptest(cls):
        print('a')

def openHtml():
    aa = [(1, 2), (2, 3), (3, 4)]
    for a, b in aa:
        print(a)
        print(b)
    input('')
    html = open('test.html', 'r', encoding='utf-8')
    from bs4 import BeautifulSoup
    htmlf = html.read()
    print(htmlf)
    htmlsoup = BeautifulSoup(htmlf, 'lxml')
    a = htmlsoup.find_all(attrs={'class': 'ng-binding'})
    import re
    reg = re.compile('''<td>
    					<label class="ng-binding">(.*?)</label>
    				</td>
    				<td>
    					<label class="ng-binding">流程号：(.*?)</label>
    				</td>''')
    # print(htmlf)
    print(list(set(re.findall(reg, htmlf))))
    # for i in a:
    # print(i.get_text())
    # print(a)
    # print(htmlsoup)
    # print(htmlsoup.prettify())

def crewDetail(quotationNo):
    import re
    urls = r'https://icorepnbs.pingan.com.cn/icore_pnbs/quotationDetail.tpl?voucherNo=Q268902390001209523037&isFromCNBS=false&moduleType=detail&_u=d0281dd81cd686402e890c6c26086e175a22f399'
    headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, br',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'WT-FPC=id=2201b2f48dc52a009651519713429025:lv=1519713443108:ss=1519713429025:fs=1519713429025:pn=6:vn=1; BSFIT_OkLJUJ=NF1Y5QY94RH75AIP; BSFIT_KaLeL=a597a29bfc4f3bb7af61ed9799df3331; BIGipServerICORE-PNBS_DMZ_PrdPool=561126572.42357.0000; CAS_SSO_COOKIE=9e90f8465e5298ac015e7041fa150006-ed47aca7140b434983615d7ae9671d89; JSESSIONID=w4oTgp9ofdDx4mr4uW18HJURuEqoSDiuMLBxj9Y3Ua5HMTFGD2pf!1776892685; _WL_AUTHCOOKIE_JSESSIONID=oZiAO3Ty7FQKXWBWwe5K',
'Host':'icorepnbs.pingan.com.cn',
'Referer':'https://icorepnbs.pingan.com.cn/icore_pnbs/apply_track.tpl?_v=',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36'}
    response = requests.get(url=urls, headers=headers)
    response.encoding='utf-8'
    #print(response.text)
    #print(response.text)
    #html = open('test.html', 'r', encoding='utf-8')
    #htmlf = html.read()
    #print(htmlf)
    origion_data = re.findall('var quotationDTO = (\{.*\})', response.text)[0]
    origion_data = origion_data.replace('true', 'True')
    origion_data = origion_data.replace('false','False')
    #print(origion_data)
    data = eval(origion_data)
    insur_info = data['voucherDetailList'][0]['voucher']
    comm_info = insur_info['c01DutyList']
    comp_info = insur_info['c51BaseInfo']


def dpi_request(path, codeType):
    import base64
    import requests
    try:
        print('接口调用成功')
        with open(path, 'rb') as s:
            ls_f = base64.b64encode(s.read())  # 读取文件内容，转换为base64编码
            #print(ls_f)
            #print(ls_f)

            params = {
                "key": '889fdc9bc1d1e5e678e52623b23c1f7a',  # 您申请到的APPKEY
                "codeType": codeType,
            # 验证码的类型，&lt;a href=&quot;http://www.juhe.cn/docs/api/id/60/aid/352&quot; target=&quot;_blank&quot;&gt;查询&lt;/a&gt;
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
        dpi_request(path, codeType)


if __name__ == '__main__':
    a = '2018-09-01'
    print(a.split('-',maxsplit=-1))
