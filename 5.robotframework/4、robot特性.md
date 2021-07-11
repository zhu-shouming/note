web自动化框架：

1、PO模式-4层（pageobject、pagelocator、testcase、testdata）--业务有关

2、写用例-数据驱动

3、封装：basepage：

​	1）基础操作-屏蔽了元素查找/元素等待，只调用元素操作即可。

​	2）执行日志、失败截图、捕获异常

4、pytest测试框架：参数化、重运行、运行用例、生成html、allture报告、组织用例、前后置处理、conftest.py共享、给用例打标记、命令行设置运行参数

### 一、<font color='red'>`*** Settings ***`</font>用法

1、引入外部文件：标准库文件、三方库文件、资源文件、变量文件

```python
*** Settings ***
Library    DateTime		# 引入标准库
Library    SeleniumLibrary	# 引入第三方库文件
Resource    我的资源.resource	# 引入资源文件
Variables    vars.py	# 引入变量文件
```

2、前后置条件设置

```python
Test Setup    Open Browser    https://www.ketangpai.com/#/login    gc
Test Teardown    Close Browser

Suite Setup    NONE
Suite Teardown    NONE
```

3、打全局标记

- **Default Tags**：默认标记，当用例有标记时用例使用自身的标记，无标记时使用默认的标记
- **Force Tags**：强制标记，当用例有标记时，强制标记后用例本身有两个标记。

### 二、前后置条件

- 针对测试用例前后置（Test Setup、Test Teardown）

- 针对测试套件前后置（Suite Setup、Suite Teardown）

### 三、RF命令参数

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
|                                             |                                 |

