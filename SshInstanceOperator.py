# encoding=utf-8
'''
Created on 2016年5月6日

@author: dWX347607
'''

import socket
import logging
import paramiko


class SshInstanceOperator():
    '''
    classdocs
    '''
    _recv_buffer = 65535

    def __init__(self, ip, username, passwd, hostname="", port=22):
        self.ssh = None
        self.sftp = None
        self.channel = None
        self.hostname = hostname
        self.connect(ip, username, passwd, port)

    def connect(self, ip, username, passwd, port=22):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(ip, port, username, passwd, timeout=5)
            self.sftp = self.ssh.open_sftp()
            self.channel = self.ssh.invoke_shell()

        except Exception, ex:
            logging.error(ex)

    def exec_command(self, cmd):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            # stdin.write("Y")   #简单交互，输入 ‘Y’
            out = stdout.readlines()
            err = stderr.readlines()
            for each_out in out:
                logging.info(self.hostname + each_out.strip())
            for each_err in err:
                logging.info(self.hostname + each_err.strip())
        except Exception, ex:
            logging.error(ex)

    def put(self, source_path, target_path):
        try:
            ftp_rst = self.sftp.put(source_path, target_path)
            logging.info("put file %s-->%s" % (source_path, target_path))
            return ftp_rst
        except Exception, ex:
            logging.error(ex)

    def change_to_root_user(self, root_password):
        logging.info("Ready to change user to root")
        self.channel.send("su\n")
        response_string = self.channel.recv(self._recv_buffer)
        while not response_string.strip().endswith(':'):
            response_string += self.channel.recv(self._recv_buffer)

        logging.info("Input root password")
        self.channel.send("%s\n" % root_password)
        response_string = self.channel.recv(self._recv_buffer)
        # 这里采用 find 的原因是 suse 的root 不是以 # 结尾，而是特殊字符
        while not response_string.find('#'):
            response_string += self.channel.recv(self._recv_buffer)

        logging.info("Change user to root success")

    # 从 root 用户上退出来
    def exit_from_root_user(self):
        logging.info("Ready to exit from root user")
        self.channel.send("exit\n")
        response_string = self.channel.recv(self._recv_buffer)
        while not response_string.strip().endswith('$') and not response_string.strip().endswith('~>'):
            response_string = self.channel.recv(self._recv_buffer)

        logging.info("Exit from root user success")

    # 使用root用户在打开的连接上执行一条指令
    def exec_command_with_root_user(self, cmd, root_password):
        try:
            self.change_to_root_user(root_password)
        except socket.timeout:
            logging.error("Change user to root error...")
            return

        self.channel.send("%s\n" % cmd)
        response_string = ''
        while not response_string.endswith('# '):
            response_string += self.channel.recv(self._recv_buffer)

        self.exit_from_root_user()

    def close(self):
        try:
            self.channel.close()
            self.sftp.close()
            self.ssh.close()
        except Exception, ex:
            logging.error(ex)
