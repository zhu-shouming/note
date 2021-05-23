### 一、自动化测试框架特征

1. 提供用例管理功能：用例编写、用例运行、用例运行配置
2. 提供日志功能、测试报告功能、异常信息捕获功能
3. 提供基本工具库：数据库操作、用例数据操作、basepage关键字封装等

### 二、robotframework-RED安装步骤

##### 1、python安装+robotframework库安装

```
robotfrmaework安装：
pip命令：pip install robotframework==3.1.2
```

##### 2、jdk1.8安装

##### 3、RED编辑器的安装和配置

- RED插件下载地址： https://github.com/nokia/RED 


##### 4、RED中配置robot

- 配置robotframework版本

  ```
  在打开的eclipse当中，选择windows->Preferences-RobotFramework->Install frameworks中配置python下的robotframework版本
  ```

- 配置robot脚本编写时关键字自动补全

  ```
  windows->Preferences->RobotFramework->Editor->Content Assit
  在Auto activation triggers中添加：
  .qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM$@&*:[
  ```

- 配置robot脚本文件的编码格式为utf-8

  ```
  windows->Preferences->General->Workspace
  ```

### 三、什么是关键字

- 关键字：一定好的功能

  python函数分为：内置函数、第三方库函数及用户自定义函数
  <font color='red'>**robot关键字分为：内置关键字、第三方库关键字及用户关键字**</font>

