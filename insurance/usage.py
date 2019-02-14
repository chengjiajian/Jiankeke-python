import datetime
from datetime import timedelta
import time
from dateutil.parser import parse

def calculateTomorrowAndNextYear(today=datetime.datetime.now()):
    a = parse(today.strftime('%Y-%m-%d'))
    tomorrow = str(a+timedelta(days=1))
    nextYear = '{} 23:59:59'.format((a+timedelta(days=365)).strftime('%Y-%m-%d'))
    return tomorrow,nextYear
if __name__ == '__main__':
    c=calculateTomorrowAndNextYear()
    print(c)