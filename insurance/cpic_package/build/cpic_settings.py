import platform
# 所有设置信息
region_info = '四川'
company_info = ''

# 手动或自动验证码
#mode_change = {'query_mode': 'auto','wbdriver_type': 'invisible'}  # 自动
#mode_change = {'query_mode': 'noauto','wbdriver_type': 'visible'}  # 手动
mode_change = {'query_mode': 'auto','wbdriver_type': 'visible'}  # 演示手动
query_mode = mode_change['query_mode']
wbdriver_type = mode_change['wbdriver_type']
cpic_executable_path = r'D:\chromedriver_win32\chromedriver' if platform.system() == 'Windows' else '/usr/local/bin/chromedriver'

# 使用库的名称
using_db = 'ggcx'