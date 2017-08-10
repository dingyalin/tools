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
    key = "eaff35d8c21a0448ff743b235830416231b2329bd248d1b7d27a5d99847f7bde980de97242a37597fc59312bbe115cb1e18bedb5f9a471813a1719fda3cd3bbe"

    # key = encrypt_key("OSUsermat_n%i")
    print key
    print decrypt_key(key)
