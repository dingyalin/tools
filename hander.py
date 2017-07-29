# -*- coding: utf-8 -*-
'''
Created on 2017年5月23日

@author: dWX347607
'''

# pylint: disable-msg=C0111,W0703,E0704,W1201

import time
import random
import logging
from functools import wraps


def exception():
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


def retry(
        max_tries=15,
        max_delay=8,
        wait_random_min=0.1,
        wait_random_max=1):

    """ 重试 """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mtries = 0
            total_mdelay = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    mtries += 1

                    # 超出重试次数,抛出异常
                    if mtries > max_tries:
                        logging.error((
                            "An error occurred (Throttling) "
                            "when calling the %s operation "
                            "(reached max retries: %s) [%s]" % (
                                func.__name__, max_tries, mtries)))
                        logging.exception(ex)
                        raise

                    # 超出重试时间,抛出异常
                    if total_mdelay > max_delay:
                        logging.error((
                            "An error occurred (Throttling) "
                            "when calling the %s operation "
                            "(reached max delay: %s) [%s]" % (
                                func.__name__, max_delay, total_mdelay)))
                        logging.exception(ex)
                        raise

                    mdelay = random.uniform(wait_random_min, wait_random_max)
                    total_mdelay += mdelay
                    logging.warning("%s, Retrying in %s s...[%s]" % (
                        str(ex), mdelay, mtries))
                    time.sleep(mdelay)
        return wrapper
    return decorator


@retry()
def main():
    num = random.randint(1, 100)
    if num > 10:
        raise Exception("aa")

    print num


if __name__ == '__main__':
    main()
