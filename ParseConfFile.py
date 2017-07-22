# encoding=utf-8
'''
Created on 2016年9月20日

@author: dWX347607
'''

import json
import ConfigParser


def parse_conf_file(conf_path):
    """ parse ini file """

    conf_parse = ConfigParser.ConfigParser()
    # 重写方法，解决解析配置文件不区分大小写问题
    conf_parse.optionxform = lambda optionstr: optionstr
    with open(conf_path) as conf_fp:
        conf_parse.readfp(conf_fp)

    return conf_parse


def parse_json_file(json_path):
    """ parse json file """

    with open(json_path) as json_fp:
        json_data = json.load(json_fp)

    return json_data


def main():
    """ main """
    parse = parse_conf_file("env.conf")
    print parse.options('env')


if __name__ == '__main__':
    main()
