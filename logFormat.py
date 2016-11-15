# encoding=utf-8

import logging
import datetime


'''
Created on 2016年11月15日

@author: dWX347607
'''

#配置日志打印 
def set_logging_format():
    now = datetime.datetime.now()
    dateStr = now.strftime("%Y-%m-%d-%H-%M")
    logFile = '../log/update_description_%s.log' % dateStr
    logging.basicConfig(level=logging.INFO,
            format='[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s] %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename= logFile,
            filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(filename)s][%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
