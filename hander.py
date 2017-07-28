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
                raise ex
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

                    # 超出重试次数,抛出异常
                    if mtries <= 0:
                        logging.error((
                            "An error occurred (Throttling) "
                            "when calling the %s operation "
                            "(reached max retries: %s)" % (
                                func.__name__, tries)))
                        logging.exception(ex)
                        raise

                    logging.warning("%s, Retrying in %s s...[%s]" % (
                        str(ex), mdelay, tries - mtries))
                    time.sleep(mdelay)
        return wrapper
    return decorator


@retry_hander(tries=3, delay=0.3)
def main():
    num = 1 / 0
    return num


if __name__ == '__main__':
    main()
