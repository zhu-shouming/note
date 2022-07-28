#### 一、变量

> python中的变量就像便利贴
>
> 变量的命名规范：包含数字、字母和下划线，不能以数字开头，尽量做到见名知意
>
> 变量的赋值：python中的变量赋值不需要类型声明，每个变量在内存中创建，都包括变量的标识和数据信息。
>
> 每个变量在使用前必须赋值，变量赋值以后该变量才会被创建。等号（=）用来给变量赋值，等号（=）的左边是变量名，等号（=）右边是存储变量中的值。如：a = 10

#### 二、字符串表示

> python可以使用引号（'）、双引号（"）、三引号（'''或"""）来表示字符串

#### 三、标识符

> 在python的pep8规范里，标识符由数字、字母和下划线组成
>
> 在python中，所有标识符可以包括数字、字母和下划线，但不能以数字开头
>
> python中的标识符是区分大小写的：函数、变量名、模块名、项目名，不能用python中的关键字命名
>
> ```python
> # python中的关键字
> import keyword
> print(keyword.kwlist)
> ```

#### 四、行和缩进

> 4个空格（一个tab键）

#### 五、控制台输入

> input输入：从控制台获取一个数据，获取到的类型是字符串类型。

#### 六、注释

> 单行注释采用#开头，快捷键ctrl+l
>
> python中的多行注释采用''''''三引号括起来

#### 七、pip

python的安装包程序

- python默认使用PYPI下载第三方库，在网络原因或公司内部仓库，可修改python下载源

  - 临时更换：pip install 报名 -i 下载源地址

  - 永久更换：1、linux在user目录下创建pip目录，目录里新建pip.ini文件；2、windows在文件路径在输入%APPDATA%，进入路径后新建pip目录和pip.ini文件

    ```ini
    # pip.ini
    [global]
    timeout = 6000
    index-url = http://mirrors.aliyun.com/pypi/simple/
    trusted-host = mirrors.aliyun.com
    ```

- pip install 第三方库报ERROR：THESE PACKAGE DO NOT MATCH THE HASHES FROM THE REQUIRMENTS FILES。下载包时期望得到hash值不是真正的hash

  ```bash
  # 解决方法，pip包安装时添加--no-cache-dir
  pip install 包名 --no-cahce-dir
  # 如果依旧报比对hash不一致，升级安装包
  pip install --upgrade 包名
  ```

- 一键安装第三方库

  ```bash
  # 需求：当需要当前项目所需库导出来，在另一个项目上一键安装
  pip freeze > requirement.txt # 将本机安装包版本信息导入txt文件中
  pip install -r requirement.txt # 读取txt信息安装对应包
  ```

