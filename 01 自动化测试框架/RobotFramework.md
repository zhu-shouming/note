#### 一、自动化框架介绍及安装

##### 自动化测试框架特征

1. 提供用例管理功能：用例编写、用例运行、用例运行配置
2. 提供日志功能、测试报告功能、异常信息捕获功能
3. 提供基本工具库：数据库操作、用例数据操作、basepage关键字封装等

##### robotframework-RED安装步骤

- robotframework库安装

```
pip install robotframework==3.1.2
```

- jdk1.8安装

- RED编辑器的安装和配置，RED插件下载地址： https://github.com/nokia/RED 


###### RED中配置robot

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

#### 二、RF标准库介绍

| 标准库           | 作用                         |
| ---------------- | ---------------------------- |
| Builtln          | 内置基本使用                 |
| Collections      | 列表、字典、元组等序列的操作 |
| DateTime         | 时间的操作                   |
| Dialogs          | 与用户的一些交互             |
| Process          | 进程                         |
| Reserved         | 控制流操作                   |
| Operating System | 与操作系统交互的一些操作     |
| Screenshot       | 截图操作                     |
| String           | 字符串操作                   |
| Telnet           | 远程连接                     |
| XML              | XML解析                      |

#### 三、RF关键字

- 关键字：定义好的功能

  python函数分为：内置函数、第三方库函数及用户自定义函数
  <font color='red'>**robot关键字分为：内置关键字、第三方库关键字及用户关键字**</font>

#### 四、Robot的关键字使用

##### 内置关键字的使用

**内置关键字从<font color="red">Library</font>中引用**

```robot
*** Settings ***
Library    DateTime   # 导入需要使用的标准库 

*** Test Cases ***
第一个用例
    Log    hello,robotframe    
    Should Be Equal As Integers   100    2 
    
第二个用例
    ${date}=    Get Current Date  
```

##### 第三方关键字的使用

**第三方关键字从<font color="red">Library</font>中引用**

```
# 1、安装第三方库；2、导入第三方库；3、调用第三方库关键字
*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
第三个用例
    Open Browser    http://www.baidu.com    Chrome
```

##### 用户关键字

区域`*** Keywords ***`定义用户关键字，存放用户关键字的文件常放在**<font color="red">Resource</font>**中

```python
*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
打开谷歌浏览器，访问百度
    Open Browser    http://www.baidu.com    chrome
    Input Text    id=kw    hello,robotframework
    
两数求和
	# Evaluate计算python表达式
    [Arguments]    ${a}    ${b}=500
    ${sum}=    Evaluate    ${a}+${b}
    [Return]    ${sum}
    
*** Test Cases ***
第四个用例	
	# 调用用户定义的关键字
	${sum}=    两数求和    2    4
    打开谷歌浏览器，访问百度
```

#### 四、区域

```
*** Comments ***	注释
*** Keywords ***	关键字
*** Settings ***	配置，库的导入，用例的前后置条件
*** Test Cases ***	测试用例
*** Variables ***	变量
```

#### 五、常用设置

```python
[Documentation]	文档说明
[Arguments]		常用于关键字传参，参数可指定默认值
[Return]		返回值
[Tags]			打标签
[Teardown]		清除环境
[Timeout]		超时
```

#### 六、变量和流程控制

##### 1.变量

###### 变量的类型

- ${变量名}：存储一个值

- @{变量名}：列表，存储多个值

- &{变量名}：字典

###### 变量的赋值

- 关键字创建创建并赋值

  **Set Variable**：设置一个变量

  **Create List**：创建一个列表

  **Create Dictionary**：创建一个字典

  ```python
  *** Test Cases ***
  第五个用例
      ${hi}    Set Variable    Hello,world!
      @{list}    Create List    a    b    c
      ${list}    Create List    a    b    c
      &{dict}    Create Dictionary    a=b    c=d
  ```

  ```
  # Message Log打印结果
  INFO : ${hi} = Hello,world!
  INFO : @{list} = [ a | b | c ]
  INFO : ${list} = ['a', 'b', 'c']
  INFO : &{dict} = { a=b | c=d }
  ```

  注：注意变量的作用域，定义在某个用例的变量只能在该用例中使用

- <font color="red">`*** Variables ***`</font>定义变量：当前文件全局有效

  ```python
  *** Variables ***
  ${say}    hello,robotframework
  @{list_1}    22    33    44    55    66    77
  &{dict_1}    today=Monday   
  
  *** Test Cases ***
  第六个用例
      Log    ${list_1}
      Log    ${list_1[1]}    # list下标索引取值
      Log    ${dict_1.today}  # dict.key获取value
  ```

  注：使用定义列表、字典的变量是，前置符号需要改过来。

###### robot引入python文件创建的变量

```python
# vars.py
my_str = 'hello,python'
my_list = [1,2,3,4,5,6]
my_dict = {'hello':'world'}
```

```python
# robot文件
*** Settings ***
Variables    vars.py	# 引入变量文件

*** Test Cases ***
第七个用例
    Log    ${my_str}
    Log    ${my_list[2]}
    Log    ${my_dict['hello']}	# dict[key]获取value
```

注：py文件列表和字典变量名加前缀：`LIST__变量名`、`DICT__变量名`，可使用robot的语法获取变量

##### 2.异常处理

<font color='red'>Run Keyword And Return Status</font>关键字处理异常

```python
*** Test Cases ***
第八个用例
    ${num}    Set Variable    3.14
    ${passed}    Run Keyword And Return Status    Evaluate    4<${num}<10
    Run Keyword If    ${passed}    Log    passed为True    
    ...    ELSE    Log    passed为False
```

##### 3.条件判断

<font color='red'>Run Keyword If</font>关键字判断分支，ELSE和ELSE IF前面要加三个`.`。在分支判断里字符串判断需要给变量加上引号，数值类型可以直接比较。

```python
*** Test Cases ***
第九个用例
    ${num}    Set Variable    3.14
    Run Keyword If    ${num}>20    Log    变量num大于20
    ...    ELSE IF    ${num}>10    Log    变量num大于10小于20
    ...    ELSE IF    ${num}>1    Log    变量大于1小于10 
    ...    ELSE    Log    变量小于等于1
    ${str}    Set Variable    hello
    Run Keyword If    '${str}'=='hello'    Log    字符串等于hello
    ...    ELSE    Log    字符串不等于hello 
```

注：**字符串比较需要给变量加引号**

##### 4.循环

###### 1.普通循环:FOR...IN...END

```python
*** Test Cases ***
第十个用例
    FOR    ${item}    In    @{list_1}
        Log    ${item}
        Exit For Loop If    ${item}==55   # 条件成立退出循环 
    END
```

###### 2.FOR...IN RANGE...END循环

```python
*** Test Cases ***
第十一个用例
	${length}    Get Length    ${list_1}
    FOR    ${index}    IN RANGE    ${length}
        Log    ${list_1[${index}]}    
    END
```

###### 3.嵌套循环：把内层循环定义成关键字

```python
*** Keywords ***
内层循环
    ${length}    Get Length    ${list_1}
    FOR    ${index}    IN RANGE    ${length}
        Log    ${list_1[${index}]}       
    END
    
*** Test Cases ***
第十二个用例
    ${length}    Get Length    ${list_1}
    FOR    ${index}    IN RANGE    ${length}
        内层循环    
    END
```

#### 七、RF特性

##### 1.<font color='red'>`*** Settings ***`</font>用法

- 引入外部文件：标准库文件、三方库文件、资源文件、变量文件

```python
*** Settings ***
Library    DateTime		# 引入标准库
Library    SeleniumLibrary	# 引入第三方库文件
Resource    我的资源.resource	# 引入资源文件
Variables    vars.py	# 引入变量文件
```

##### 2.前后置条件设置

- 针对测试用例前后置（Test Setup、Test Teardown）
- 针对测试套件前后置（Suite Setup、Suite Teardown）

```python
Test Setup    Open Browser    https://www.ketangpai.com/#/login    gc
Test Teardown    Close Browser

Suite Setup    NONE
Suite Teardown    NONE
```

3、打全局标记

- **Default Tags**：默认标记，当用例有标记时用例使用自身的标记，无标记时使用默认的标记
- **Force Tags**：强制标记，当用例有标记时，强制标记后用例本身有两个标记。

##### 3.RF命令参数

RF内置robot命令，命令参数要区分大小写。

格式：<font color='red'>robot [参数] 测试用例全路径</font>

示例：>robot -i smoke D:\code\xxx.robot

| 参数                                        | 作用                            |
| ------------------------------------------- | ------------------------------- |
| -i,--include `<tag>`                        | 运行指定标签的用例              |
| -e,--exclude `<tag>`                        | 运行除指定标签外的用例          |
| -t,--test `<name>`                          | 运行指定的用例                  |
| -s,--suite `<name>`                         | 运行指定的用例套件              |
| -d,--outputdir `<dir>`                      | 执行文件输出的目录              |
| -o,--output `<file>`                        | 指定文件输出的文件名（xml文件） |
| -v,--variable `<name:value>`                | 设置运行时的变量                |
| -V,--variablefile `<path:args>`             | 设置运行时变量（从文件读取）    |
| -R,--returnfailed `<outputxml_file>`        | 设置重新运行失败的用例          |
| -S，--returnfailedsuites `<outputxml_file>` | 设置重新运行失败的用例套件      |

#### 八、RF做接口自动化

##### 1.安装第三库，提供接口测试的关键字

```python
pip install requests
pip install robotframework-requests
```

##### 2.引入RequestsLibrary

```robotframework
*** Settings ***
Library    RequestsLibrary
```

RequestsLibrary中的关键字

- 第一类：与服务端的会话
- 第二类：请求类型
- 第三类：响应结果转json

##### 3.RF实现数据驱动

```python
*** Settings ***
Test Template    两数求和   

*** Test Cases ***    a    b    excepted
个位数相加    1    1    2
十位数相加    10    10    20
百位数相加    100    100    200
      
*** Keywords ***
两数求和
    [Arguments]    ${a}    ${b}    ${excepted}
    ${sum}    Evaluate    ${a}+${b}    
    Should Be Equal As Integers    ${sum}    ${excepted}  
```

#### 九、扩展第三方库

- 1、采用函数创建第三方库

  - 可以参照标准库DateTime.py

- 2、采用类创建第三方库

  - 库名和类名保持一致

  - 初始化时一定要有默认值

    ```python
    # DoExcel.py
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = 1.0
    
    class DoExcel(object):
        def __init__(self, filename=None):
            pass
        def xxx(self):
            pass
    ```

##### 与jenkins集成

1. 安装插件

2. 命令运行

