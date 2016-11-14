#!/usr/local/bin/python
# encoding: utf-8
__author__ = 'l00289062'

import socket
import logging

import paramiko
from paramiko.ssh_exception import AuthenticationException


# 实例操作类
class InstanceOperator:
    _time_out = 10
    _ssh_port = 22
    _recv_buffer = 65535

    # 构造函数，唯一参数是主机实例，Instance对象
    def __init__(self, instance):
        self.instance = instance

    # 验证账号密码是否正确
    def check_user_and_password(self):
        if self.__connect_to_instance():
            return True
        return False

    # 修改用户名和密码
    def change_password(self, new_mateinfo_password, new_root_password):
        # cmd = "/bin/echo %s|/usr/bin/passwd --stdin %s" % (new_password, self.instance.username)
        change_mateinfo_password_cmd = """(echo "%s";sleep 1; echo "%s")| passwd mateinfo""" % (new_mateinfo_password,
                                                                                                new_mateinfo_password)
        change_root_password_cmd = """(echo "%s";sleep 1; echo "%s")| passwd root""" % (new_root_password,
                                                                                        new_root_password)

        logging.info("Ready to connect instance %s..." % self.instance.private_ip_address)
        if not self.__connect_to_instance():
            logging.error("Can't Not Connect To Instance %s" % self.instance.private_ip_address)
            return False
        logging.info("Connect to instance %s success..." % self.instance.private_ip_address)

        logging.info("Ready to change user `%s` password" % self.instance.username)
        if not self.__send_command_to_instance_with_root_user(change_mateinfo_password_cmd):
            return False
        logging.info("Change user `%s` password success..." % self.instance.username)

        logging.info("Ready to change user `root` password")
        if not self.__send_command_to_instance_with_root_user(change_root_password_cmd):
            return False
        logging.info("Change user `root` password success...")

        print "change `%s@%s` and `root@%s` password succeed" % (self.instance.username,
                                                                 self.instance.private_ip_address,
                                                                 self.instance.private_ip_address)

        return True

    # 修改 log 用户的目录权限
    def change_log_permission(self):
        if not self.__connect_to_instance():
            logging.error("Can't Not Connect To Instance %s" % self.instance.private_ip_address)
            return False
        logging.info("Connect to instance %s success..." % self.instance.private_ip_address)

        logging.info("Ready to change dir permission")
        if not self.__send_command_to_instance_with_normal_user("chmod 750 /opt/mateinfo"):
            logging.error("Change permission of `/opt/mateinfo` failed")
            return False
        logging.info("Change permission of `/opt/mateinfo` success")

        if not self.__send_command_to_instance_with_normal_user("chmod -R 750 /opt/mateinfo/logs"):
            logging.error("Change permission of `/opt/mateinfo/logs` failed")
            return False
        logging.info("Change permission of `/opt/mateinfo/logs` success")

    # 连接实例，获取 Channel 、标准输入 和 标准输出
    def __connect_to_instance(self):
        self.transport = paramiko.Transport((self.instance.private_ip_address, self._ssh_port))

        try:
            self.transport.connect(username=self.instance.username, password=self.instance.password)
        except AuthenticationException:
            logging.error("Connecttion to `%s@%s` error" % (self.instance.username, self.instance.private_ip_address))
            return False

        # 成功建立连接之后打开一个 channel
        self.channel = self.transport.open_session()
        # 设置会话超时时间
        self.channel.settimeout(5)
        # 打开远程终端
        self.channel.get_pty()
        # 激活远程终端
        self.channel.invoke_shell()

        return True

    # 使用普通用户在打开的连接上执行一系列命令
    def __send_commands_to_instance_with_normal_user(self, cmds):
        for cmd in cmds:
            self.__send_command_to_instance_with_normal_user(cmd)

    # 使用普通用户在打开的连接上执行一条指令
    def __send_command_to_instance_with_normal_user(self, cmd):
        self.channel.send("%s\n" % cmd)
        response_string = self.channel.recv(self._recv_buffer)
        while not response_string.strip().endswith('$') and not response_string.strip().endswith('~>'):
            response_string = self.channel.recv(self._recv_buffer)

    # 使用root用户在打开的连接上执行一系列命令
    def __send_commands_to_instance_with_root_user(self, cmds):
        for cmd in cmds:
            self.__send_command_to_instance_with_normal_user(cmd)

    # 使用root用户在打开的连接上执行一条指令
    def __send_command_to_instance_with_root_user(self, cmd):
        try:
            self.__change_to_root_user()
        except socket.timeout:
            logging.error("Change user to root error...")
            return False

        self.channel.send("%s\n" % cmd)
        response_string = self.channel.recv(self._recv_buffer)
        while not response_string.find('#'):
            response_string = self.channel.recv(self._recv_buffer)

        self.__exit_from_root_user()
        return True

    # 切换到 root 用户
    def __change_to_root_user(self):
        logging.info("Ready to change user to root")
        self.channel.send("su\n")
        response_string = self.channel.recv(self._recv_buffer)
        while not response_string.strip().endswith(':'):
            response_string = self.channel.recv(self._recv_buffer)

        logging.info("Input root password")
        self.channel.send("%s\n" % self.instance.root_password)
        response_string = self.channel.recv(self._recv_buffer)
        # 这里采用 find 的原因是 suse 的root 不是以 # 结尾，而是特殊字符
        while not response_string.find('#'):
            response_string = self.channel.recv(self._recv_buffer)

        logging.info("Change user to root success")

    # 从 root 用户上退出来
    def __exit_from_root_user(self):
        logging.info("Ready to exit from root user")
        self.channel.send("exit\n")
        response_string = self.channel.recv(self._recv_buffer)
        while not response_string.strip().endswith('$') and not response_string.strip().endswith('~>'):
            response_string = self.channel.recv(self._recv_buffer)

        logging.info("Exit from root user success")

    # 关闭连接
    def close(self):
        self.channel.close()
        self.transport.close()
