#### 1.安装

```python
pip install httprunner==2.3.0
hrun -V	# 查看HTTPRunner版本
hrun -h	# 查看httpRunner帮助文档
hrun --startproject [projectname]	# 创建项目
```

#### 2.httprunner 2.x项目结构

- api目录：存放接口的最小执行单元（正向用例）

- reports目录：用于存放测试报告

- testcases目录：用于处理接口的复杂执行逻辑

- testsuites目录：

  - 添加多条测试用例，批量执行
  - 处理数据驱动测试

- .env文件：用于定义全局环境变量

- debugtalk.py文件：用于处理动态参数或处理参数化动态数据

  ```
  YAML配置文件的格式要求：
  	1.yaml是一种强缩进的数据格式，同级键值对缩进必须一致
  	2.yaml配置文件的后缀为.yaml或.yml
  	3.yaml配置文件中使用#进行注释，不可以在yaml数据行内进行注释
  	4.数据格式为key: value，且在同一区域的key不能重复
  	5.yaml中的value含有字母，会识别为字符串类型，可以为其添加单引号或双引号指定为字符串类型
  	6.yaml中的value为数字，自动识别为int类型
  	7.yaml使用-表示数组结构
  ```

#### 3.httprunner api

##### 1.api中编写用例

```yaml
# 指定当前用例的名称
name: "登录接口-正向用例"
variables:
    var1: value1
    var2: value2

# 指定接口的请求信息
request:
    # 指定当前用例的url
    url: 'http://127.0.0.1:8000/user/login/'
    # 指定当前接口的请求方式
    method: POST
    # 指定请求头中的信息
    headers:
        Content-Type: "application/json"
    # 指定传入的json数据
    json:
        username: 'zhushouming'
        password: '123456'
# 断言
validate:
    - eq: ["status_code", 200]
```

##### 2.执行用例

```python
# Terminal中执行用例
hrun yaml文件的绝对路径/相对路径
```

##### 3.api中yaml用例编写规则

```yaml
# 1.指定传入x-www-form-urlencoded数据时，需要用到data关键字替换json并在请求头中指定Content-Type类型。传参key值与requests.request接口参数完全一致。
    headers:
        Content-Type: "application/x-www-form-urlencoded"
    data:
        username: 'zhushouming'
        password: '123456'
# 2、指定运行用例的日志级别
hrun api/login_api.yml --log-level debug
# 3.断言方式
#	断言的格式：- 断言方式: ["实际值", "期望值"]
#	断言方式：lt(小于)、le(小于等于)、gt(大于)、ge(大于等于)、contains(包含)...源码中validator、built_in可查看
#	实际值：status_code, cookies, elapsed, headers, content, text, json, encoding, ok, reason, url.
#	a.判断响应体是都包含token键
validate:
    - contains: ["content", "token"]	
#	b.判断响应体中user_id的值是否小于2，通过json.user_id调用key中的value
validate:
    - lt: ["json.user_id", 2]
#	c.实际值部分支持jsonpath提取
#	d.也支持正则表达式，*正则表达式*
# 4.全局提取base_url，会自动拼接url
base_url: "http://127.0.0.1:8000"
request:
	url: '/user/login/'
# 5.定义变量
#	a.在variables区域下定义变量在yaml全局有效，使用变量 $变量名
variables:
    uname: 'zhushouming'
    pwd: '123456'
    
    data:
    	username: $uname
    	password: $pwd
#	b.在.env配置环境变量，使用环境变量 ${ENV(环境变量名)}
	data:
        username: ${ENV(USERNAME)}
        password: ${ENV(PASSWORD)}
# 5.动态生成数据，
#	- 在debugtalk.py文件中定义函数
#	- 在yaml文件中使用 ${函数名()} 即可调用
```

#### 3.httprunner testcases

##### 1.模板

```yaml
# variables优先级顺序
#	1.config中variables
#	2.teststeps中的variables
#	3.api中的variables
# validate校验逻辑：
#	1.如果teststeps中的校验方式和api不一致，会合并校验
#	2.api中的validate一般为基础断言方式（如响应状态码等）
# config定义全局配置信息
config:
	name: "demo testcase"
	variables: 
		device_sn: "abc"
		username: ${ENV(USERNAME)}
		password: ${ENV(PASSWORD)}
	base_url: "http://127.0.0.1:5000"

# teststeps定义每个测试步骤
teststeps:
-
	name: demo step 1
	api: path/toapi1.yal
	variables:
		user_agent: "iOS/10.3"
		device_sn: $device_sn
	# extract用于创建变量提取参数，下方测试步骤中该变量均能调用
	extract:
		- token: content.token
	validate:
		- eq: ["status_code", 200]
	
	name: demo step 2
	api: path/to/api2/yml
	variables:
		token: $token
```

##### 2.testcases编写用例

```yaml
# projects_testcase.yml	获取项目列表接口测试用例
config:
	name: "测试获取项目列表数据接口"
	
teststeps:
-
	name: "先登录"
	api: "api.login_api.yml"
	extract:
		- token: content.token
	
	name: "获取项目列表数据"
	api: "api/projects_api.yml"
	
# projects_api.yml	获取项目列表数据api
name: "获取项目列表数据接口-正向用例"
base_url: ${ENV(URL)}
request:
	url: '/projects/'
    method: GET
    # 请求头中添加参数
    headers:
    	Authorization: "JWT $token"
    # 添加查询字符串参数
    params:
    	p: "2"
    	s: "3"
validate:
	- eq: ["content", 200]
```

#### 4.httprunner testsuites

##### 1.模板

```yaml
# config定义所有用例的公共信息
config:
	name: "demo testsuite"
	variables:
		device_sn: "XYZ"
	base_url: "http://127.0.0.1:5000"
	
testcases:
-
	name: call demo_testcase with data1
	testcase: path/to/projects_testcases.yml
	variables:
		device_sn: $device_sn
-
	name: call demo_testcase with data2
	testcase: path/to/projects_testcases.yml
	variables:
		device_sn: $device_sn
```

##### 2.testsuites数据驱动

```yaml
config:
	name: "demo testsuite"

testcases:
-
	name: "测试登录接口"
	testcase: path/to/login_testcase.yml
	# parameters定义数据驱动参数
	parameters:
		# 定义传参的内容，和下面的数据一一对应
		- title-username-password-status_code-msg
			- ['正常登录', 'zsm', '123456', 200, 'token']
			- ['密码错误', 'zsm', '1234657', 400, 'non_filed_errors']
```

##### 3.测试数据存放

- 存放在csv中，使用${P(csv文件路径)}

  ```
  # csv文件的数据使用,相隔
  - title-username-password-status_code-msg: ${P(data/data.csv)}
  ```

- 存放在函数返回中，直接调用函数

  ```
  - title-username-password-status_code-msg: ${函数()}
  ```

#### 5.执行入口

```python
# 新建入口py文件执行yaml文件
from httprunner.api import HttpRunner
obj = HttpRunner(log_level="DEBUG")
obj.run("yml文件路径")
res = obj.summary	# 获取执行yml文件的所有信息
```



