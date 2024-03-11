import paramiko
from resource.utils.log import logger


class SSHConnection(object):
    def __init__(self, host, username, pwd, port=22, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd
        self.timeout = timeout
        self.try_times = 3

    def connect(self):
        """
        建立SSH连接
        :return:
        """
        while True:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                transport = paramiko.Transport(self.host, self.port)
                transport.connect(username=self.username, password=self.pwd)
                # 如果没有抛出异常说明连接成功，直接返回
                logger.info('连接 {} 成功'.format(self.host))
                self.__transport = transport
                return
            except Exception:
                if self.try_times != 0:
                    print('连接 {} 失败，进行重试'.format(self.host))
                    self.try_times -= 1
                else:
                    print('重试3次失败，结束程序')
                    exit(1)

    def close(self):
        """
        关闭SSH连接
        :return:
        """
        self.__transport.close()

    def cmd(self, command):
        """
        执行的命令
        :param command: 命令行。如：kubectl get pod -n springcloud6murotfd spring-gray-server-6d7967c876-q622h -o yaml
        :return: 执行结果
        """
        ssh = paramiko.SSHClient()
        ssh._transport = self.__transport
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        return str(result, encoding="utf-8")

    def upload(self, local_path, target_path):
        """
        上传信息
        :param local_path: 本地文件路径，包含文件名和后缀名
        :param target_path: 远端文件路径，包含文件名和后缀名
        :return:
        """
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        sftp.put(local_path, target_path)

    def download(self, remote_path, local_path):
        """
        下载
        :param remote_path: 是远端文件路径，包含文件名和后缀名
        :param local_path: 下载本地文件路径，包含文件名和后缀名
        :return:
        """
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        sftp.get(remote_path, local_path)


if __name__ == '__main__':
    ssh = SSHConnection("10.0.166.103", "root", "1qaz@WSX")
    ssh.connect()
    logger.info(ssh.cmd("curl http://10.0.166.103/demo-v1/"))
    # logger.info(ssh.cmd("kubectl get pod -n springcloud6murotfd spring-gray-server-6d7967c876-q622h -o yaml"))
    # ssh.upload("C:\\subjects.xlsx", "/root/subjects.xlsx")
    # ssh.download("/root/subjects.xlsx", "C:\\subjects.xlsx")
    ssh.close()
