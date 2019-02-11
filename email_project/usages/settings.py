import os
# 保存地址管理
admin_phone = 17601228909  # 成佳健
quanlian_phone = 15221437270  # 刘文才
juren_phone = 13671924601  # 张婉怡
current_path = 'static'
main_path = os.path.join(current_path, 'excel_attachment')
# 关键字管理
keywords1 = '聚仁台账'  # 普通台账关键字
keywords2 = '聚仁垫资'  # 垫资关键字
keywords3 = '全联表格'  # 刘文才 关键字
official_info = {'receive_list_type': 1,
                 'insert_server': 'ggcx',
                 'info_server': 'insurance_info',
                 'email': 'shiyugroup_cjj@163.com'}
test_info = {'receive_list_type': -1,
             'insert_server': 'ggcx_test',
             'info_server': 'insurance_info_temp',
             'email': '17601228909@163.com'}
# 切换数据源
using_data = test_info     # 测试
#using_data = official_info  # 正式
# 切换 邮箱号
now_email = using_data['email']
# 切换 入库数据入口
insert_server = using_data['insert_server']
# 切换 单条数据 入库
info_server = using_data['info_server']