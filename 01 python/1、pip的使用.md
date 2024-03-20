pip（python包管理工具）

#### pip安装第三方库

命令：pip install 库名

python默认使用PYPI下载第三方库，在网络原因或有公司内部仓库时，可以修改python下载源

- 临时更换下载源：pip install 报名 -i 下载源地址

- 永久更换下载源

  windows在文件路径在输入%APPDATA%，进入路径后新建pip目录和pip.ini文件

  ```python
  # pip.ini
  [global]
  timeout = 6000
  index-url = http://mirrors.aliyun.com/pypi/simple/
  trusted-host = mirrors.aliyun.com
  ```

  linux用户可在用户目录下创建pip目录和pip.conf文件，如：/root/.pip/pip.conf

#### pip安装过程报错

ERROR：THESE PACKAGE DO NOT MATCH THE HASHES FROM THE REQUIRMENTS FILES

原因：下载包时期望得到hash值不是真正的hash

```bash
# 解决方法，pip包安装时添加--no-cache-dir
pip install 包名 --no-cahce-dir
# 如果依旧报比对hash不一致，升级安装包
pip install --upgrade 包名
```

#### pip一键安装/导出/卸载

```bash
pip freeze > requirement.txt	# 一键把本地已安装第三方库库信息收集到requirement.txt
pip install -r requirement.txt # 读取信息一键安装
pip uninstall -r mudule.txt -y	# 一键卸载mudule.txt所记录的三方库
```

