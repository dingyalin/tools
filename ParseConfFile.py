# encoding=utf-8
'''
Created on 2016年9月20日

@author: dWX347607
'''

import re
import sys
sys.path.append('/opt/mateinfo/maintenance/encrypt')
import json
import logging
import ConfigParser
from encrypt import EnCrypt


## 重写方法，解决解析配置文件不区分大小写问题
class MyConfigParser(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr

# parse conf to dict
def parse_conf(conf_path):
    try:
        parse_data = {}

        encrypt = EnCrypt() 
        conf_parse = MyConfigParser()
        conf_parse.read(conf_path)
        
        sections = conf_parse.sections()
        for each_section in sections:
            parse_data[each_section] = {}
            options = conf_parse.options(each_section)
            for each_option in options:
                value = conf_parse.get(each_section, each_option)
                mat = re.match(r"ENC\((.+)\)", value)
                if mat != None:
                    parse_data[each_section][each_option+"__ENC"] = mat.group(1)
                    value = encrypt.getdecryptkey(mat.group(1))
                parse_data[each_section][each_option] = value
    
        return parse_data
    except Exception, ex:
        logging.exception(ex)
    
def parse_json(json_path):
    try:
        json_file = open(json_path, 'r')
        json_data = json.load(json_file)
        json_file.close()
    
        return json_data
    except Exception, ex:
        logging.exception(ex)