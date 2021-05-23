### RF框架-利用RequestsLibrary关键字实现接口自动化

#### 一、安装第三库，提供接口测试的关键字

```python
pip install requests
pip install robotframework-requests
```

#### 二、引入RequestsLibrary

```robotframework
*** Settings ***
Library    RequestsLibrary
```

#### 三、RequestsLibrary中的关键字

- 第一类：与服务端的会话
- 第二类：请求类型
- 第三类：响应结果转json

#### 四、RF实现数据驱动

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

