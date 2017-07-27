# -*- coding: utf-8 -*-
'''
Created on 2017年7月11日

@author: dWX347607
'''

import sys

sys.path.append('/opt/mateinfo/maintenance/encrypt')
from encrypt import EnCrypt
encrypt = EnCrypt()


def encrypt_key(key):
    return encrypt.encryptkey(key)


def decrypt_key(key):
    return encrypt.getdecryptkey(key)


if __name__ == "__main__":
    # key = "83681b0ee23cabdd7c1c5d93dc7482e90608d542fef16435c79f3a155493ca62"

    key = encrypt_key("OSUsermat_n&i")
    print key
    print decrypt_key(key)
