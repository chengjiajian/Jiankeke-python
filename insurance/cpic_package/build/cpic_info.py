# 所有信 息

insuranceList = ['chesuanInsurance',  # 车损
                 'disanfangInsurance',  # 第三方
                 'chedaoInsurance',  # 全车盗抢
                 'sijiInsurance',  # 司机座位责任险
                 'chenkeInsurance',  # 乘客座位责任险
                 'boliInsurance',  # 玻璃单独破碎险
                 'huahenInsurance',  # 车身划痕损失险
                 'ziranInsurance',  # 自燃损失险
                 'fadongjiInsurance',  # 发动机涉水损失险
                 'zhuanxiuInsurance',  # 指定专修厂特约条款
                 'teyueInsurance',  # 无法找到第三方特约险
                 'jiaoqiangInsurance',  # 交强险
                 'chechuanInsurance']  # 车船税

officialList = {'DAMAGELOSSCOVERAGE':{'name':'机动车损失保险','nickname':'车损'},
                'THIRDPARTYLIABILITYCOVERAGE':{'name':'机动车第三者责任保险','nickname':'三者'},
                'INCARDRIVERLIABILITYCOVERAGE':{'name':'机动车车上人员责任保险-司机','nickname':'司机'},
                'INCARPASSENGERLIABILITYCOVERAGE':{'name':'机动车车上人员责任保险-乘客','nickname':'乘客'},
                'THEFTCOVERAGE':{'name':'机动车全车盗抢保险','nickname':'盗抢'},
                'GLASSBROKENCOVERAGE':{'name':'玻璃单独破碎险','nickname':'玻璃'},
                'SELFIGNITECOVERAGE':{'name':'自燃损失险','nickname':'自燃'},
                'CARBODYPAINTCOVERAGE':{'name':'车身划痕损失险','nickname':'划痕'},
                'PADDLEDAMAGECOVERAGE':{'name':'发动机涉水损失险','nickname':'发动机涉水'},
                'APPOINTEDREPAIRFACTORYSPECIALCLAUSE':{'name':'指定修理厂险','nickname':'指定厂'},
                'DAMAGELOSSCANNOTFINDTHIRDSPECIALCOVERAGE':{'name':'机动车损失保险无法找到第三方特约险','nickname':'第三方特约险'}}

cpic = {1:'身份证',
        2:'',
        3:'',
        4:'',}

plateInfo = {1: '蓝', 2: '黄', 3: '黑', 4: '其他', 5: '蓝M', 6: '黄D', 7: '黄M', 8: '黄N', 9: '黄T', 'a': '黄J',
             'b': '白', 'c': '白M', 'd': '渐变绿', 'e': '黄绿双拼'}