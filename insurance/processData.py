import re
from pymongo import MongoClient

def postData():
    with open(r'C:\Users\ASUS\Desktop\inputCJJ.txt','r') as fn:
        f = fn.readlines()
        data={}
        for i in f:
            c = i.split(':',1)
            key = re.sub('\.','`',c[0])
            value = re.sub('\n','',c[1])
            data['{}'.format(key)]=value
        return data

if __name__ == '__main__':
    conn = MongoClient('140.143.238.224', 27017)
    conn['cookieDB'].authenticate('root', 'cjj941208', mechanism='SCRAM-SHA-1')
    db = conn.cookieDB
    cookiesTable = db.cookiesTable
    inputData = db.inputData
    carData = db.carData
    responseData = db.responseData
    inputData.insert(postData())

