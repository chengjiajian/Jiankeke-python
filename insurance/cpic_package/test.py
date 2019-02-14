import re


message = r'地址:abcdffffaa哎哎哎111-..-__-'
#message = re.sub('：',':',message)
print(message)
reg = re.compile('姓名:(.*?)')
print(re.findall(reg,message))