# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: dWX347607
'''

# pylint: disable-msg=C0111,W0703,E0704,W1201

import time
import logging
from functools import wraps


def exception_hander():
    """ 方法异常处理 """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                logging.exception(ex)
                return ex
        return wrapper
    return decorator


def retry_hander(tries=3, delay=1):
    """ 重试 """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    mtries -= 1
                    logging.warning("%s, Retrying in %s s...[%s]" % (
                        str(ex), mdelay, tries - mtries))

                    # 超出重试次数,抛出异常
                    if mtries <= 0:
                        logging.error("An error occurred (Throttling) when calling the %s operation (reached max retries: %s): Rate exceeded" % (
                            func.name, mtries))
                        logging.exception(ex)
                        raise

                    time.sleep(mdelay)
        return wrapper
    return decorator


@retry_hander(tries=3, delay=1)
def main():
    a = 1 / 0
    return a


if __name__ == '__main__':
    main()
