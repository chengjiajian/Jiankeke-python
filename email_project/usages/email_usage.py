import contextlib
import poplib
from usages.settings import now_email
import smtplib

# 切换 取数据的来源
@contextlib.contextmanager
# useraccount='17601228909@163.com'
# useraccount='shiyugroup_cjj@163.com'
def pop_usage(useraccount=now_email, password='cjj941208', pop3_server='pop.163.com'):
    # 邮件服务器地址。如果你的邮箱是163，那么可以这么写。qq的话就是pop.qq.com
    server = poplib.POP3(pop3_server)
    # 可选项： 打开或者关闭调试信息，1为打开，会在控制台打印客户端与服务器的交互信息
    server.set_debuglevel(1)
    # 可选项： 打印POP3服务器的欢迎文字，验证是否正确连接到了邮件服务器
    print(server.getwelcome().decode('utf8'))
    server.user(useraccount)
    server.pass_(password)
    try:
        yield server
    finally:
        server.quit()

# 切换 取数据的来源
@contextlib.contextmanager
def smtp_usage(fromaddr='shiyugroup2018@qq.com', password='fmykbojxotfedjei'):
    server = smtplib.SMTP_SSL()
    server.connect('smtp.qq.com', 465)
    server.login(fromaddr, password)
    try:
        yield server
    finally:
        server.close()
