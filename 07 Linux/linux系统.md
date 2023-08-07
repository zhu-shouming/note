#### 区分linux系统

一般来说linux系统基本分为两大类：

- RedHat系列：Redhat、Centos、Fedora等
  - 常见的安装包格式 rpm包,安装rpm包的命令是“rpm -参数”
  - 包管理工具 yum
  - 支持tar包
- Debian系列：Debian、Ubuntu等
  - 常见的安装包格式 deb包,安装deb包的命令是“dpkg -参数”
  - 包管理工具 apt-get
  - 支持tar包

|                  | centos                  | ubuntu               |
| ---------------- | ----------------------- | -------------------- |
| 查看系统版本命令 | cat /etc/redhat-release | cat /etc/lsb-release |
| 包管理工具       | yum                     | apt-get              |

#### linux系统目录结构

| 目录名      | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| /           | 根目录，一般根目录只存放目录，不要存放文件。/etc、/bin、/dev、/lib、/sbin应该和根目录放置一个分区 |
| /bin        | binary，存放系统中二进制可执行文件，功能和/usr/bin类似，普通用户都可以使用 |
| /sbin       | system binary，存放的是用于系统管理的二进制文件，是系统管理员专用的 |
| /boot       | 存放linux内核和系统启动文件                                  |
| /dev        | 存放所有的设备文件，包括硬盘、分区、键盘、鼠标、USB等        |
| /etc        | 存放系统所有的配置文件，如passed存放用户账户信息、hostname存放主机信息、fstab存放自动挂载分区信息等 |
| /home       | 用户目录的默认位置                                           |
| /lib        | 存放共享的库文件，包含许多被/bin和/sbin中程序使用的库文件    |
| /lost+found | 在ext2或ext3文件系统中，当系统意外崩溃或计算意外关机，而产生的一些文件碎片存放位置 |
| /media      | 即插即用型设备的挂载点自动在该目录下创建                     |
| /mnt        | 用作于被挂载的文件系统的挂载点                               |
| /proc       | 存放所有标志为文件的进程，它们是通过进程号或其他的系统动态信息进行标识 |
| /opt        | 作为可选文件和程序的存放目录                                 |
| /root       | 跟用户的主目录                                               |
| /srv        | 存放系统所提供的服务数据                                     |
| /sys        | 将操作设备组织或层次化结构，并向用户提供详细的内核信息       |
| /tmp        | 临时文件目录。/var/tmp目录和这个目录相似                     |
| /usr        | 存放与用户直接有关的文件和目录                               |
| /usr/bin    | 用户管理员的标准命令                                         |
| /var        | 存放经常被修改的东西，比如各种的日志文件                     |
| /run        | 存放系统启动以来的信息。如果系统重启，这个目录下的文件应该被删掉或清除 |

#### 防火墙配置

防火墙分类：Iptables(静态防火墙)、Firewalld(动态防火墙)

防火墙常用命令

```bash
systemctl enable/disable firewalld	# 设置开机启用/禁用防火墙
systemctl start/stop firewalld	# 启动/关闭防火墙
systemctl status firewalld	# 检查防火墙状态，等同于firewall-cmd --state
firewall-cmd --zone=public --add-port=80/tcp --permanent	# 开放tcp80端口
firewall-cmd --zone=public --add-port=9595/udp --permanent	#开放udp9595端口
firewall-cmd --zone=public --remove-port=80/tcp --permanent	# 关闭tcp80端口
firewall-cmd --reload	# 配置立即生效
firewall-cmd --list-ports	# 查看防火墙所有开放的端口
# 查看监听的端口
netstat -ntlp	# TCP
netstat -nulp	# UDP
```

注：iptables和firewaldl是linux防火墙的两种管理程序，真正的防火墙执行者位于内核的neifilter。只是两种防火墙管理程序使用方法不一样，配置防火墙时，建议只使用其中的一种。

##### Failed to start firewalld - dynamic firewall daemon.

- 原因一：系统安装的python版本原因。usr/sbin/firewalld文件头部的python版本和安装的python版本不一致导致的

  1. 先查看linux系统的Python版本：python --version

  2. 查看firewalld在那个路径下：which firewalld

  3. 查看firewalld文件和firewalld-cmd文件头是否一致且与Python一致，如果不一致，需要改成与Python版本一致。

     ```bash
     head -n 10 /usr/sbin/firewalld
     head -n 10  /usr/bin/firewall-cmd
     ```

- 原因二：firewalld的进程问题

  ```bash
  pkill -f firewalld
  ```

  







