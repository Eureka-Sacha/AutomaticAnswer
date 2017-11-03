#!/home/tops/bin/python
# -*- coding: utf-8 -*-
import paramiko

from Logger import init_logger
import ConfigReader


class SSHClient:
    def __init__(self, config):
        if isinstance(config, ConfigReader.ConfigReader):
            self.ip = config.get('ip')
            self.port = config.get('port')
            self.user = config.get('user')
            self.pwd = config.get('pwd')
        else:
            self.ip = config['ip']
            self.port = config['port']
            self.user = config['user']
            self.pwd = config['pwd']
        self.sshClient = paramiko.SSHClient()
        self.sftpClient = None
        self.transport = None
        self.logger = init_logger("SSHClient", "SSHClient.log")

    def start(self):
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(self.ip, int(self.port), self.user, self.pwd)
        self.logger.info("SSH %s:%s start" % (self.ip, self.port))

    def stop(self):
        self.sshClient.close()
        self.logger.info("SSH %s:%s stop" % (self.ip, self.port))

    def exec_command(self, command):
        stdin, stdout, stderr = self.sshClient.exec_command(command)
        self.logger.info("SSH %s:%s exec command: <%s>" % (self.ip, self.port, command))
        err_message = stderr.read()
        if err_message:
            self.logger.error("SSH %s:%s command fail: cmd=%s message=%s" % (self.ip, self.port, command, err_message))
        return stdout.read()

    def open_sftp(self):
        self.transport = paramiko.Transport((self.ip, int(self.port)))
        self.transport.connect(username=self.user, password=self.pwd)
        self.sftpClient = paramiko.SFTPClient.from_transport(self.transport)
        self.logger.info("SFTP %s:%s start" % (self.ip, self.port))

    def close_sftp(self):
        self.sftpClient.close()
        self.transport.close()
        self.logger.info("SFTP %s:%s stop" % (self.ip, self.port))

    def put(self, local, remote):
        self.sftpClient.put(localpath=local, remotepath=remote)
        self.logger.info("SFTP %s:%s put %s  to %s" % (self.ip, self.port, local, remote))

    def get(self, local, remote):
        self.sftpClient.get(remotepath=remote, localpath=local)
        self.logger.info("SFTP %s:%s get %s  from %s" % (self.ip, self.port, local, remote))


if __name__ == '__main__':
    ssh = SSHClient({'ip': '', 'port': 22, 'user': 'root', 'pwd': '1234'})
    ssh.start()
    print ssh.exec_command('ps -ef')
    ssh.open_sftp()
    ssh.put('D:/tmp/demo/test.py', '/tmp/test.py')
    ssh.stop()
