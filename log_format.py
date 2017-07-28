# encoding=utf-8

'''
Created on 2016年11月15日

@author: dWX347607
'''

import logging


def set_logging_format(log_file):
    """ set log format """
    log_format = (
        '[%(asctime)s][%(filename)s][line:%(lineno)d]'
        '[%(levelname)s] %(message)s'
    )
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=log_file,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(filename)s][%(levelname)s] %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
