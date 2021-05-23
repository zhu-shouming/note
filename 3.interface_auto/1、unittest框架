#### 一、unittest框架核心概念

- **TestCase**：测试用例，一个testcase的实例就是测试用例
- **TestSuite**：测试套件，多个测试用例集合在一起。TestLoader：用来加载TestCase到Testsuite中
- **TextTestRunner**：测试运行程序，用来执行测试用例
- **fixture**：测试环境搭建和销毁

#### 二、创建测试用例

```python
# 被测函数login_check
def login_check(username, password):
    if 6 <= len(password) <= 18:
        if username == 'xiaoming' and password == '123456':
            return {'code': 0, 'msg': '登录成功'}
        else:
            return {'code': 1, 'msg': '账号或密码不正确'}
    else:
        return {'code': 0, 'msg': '密码长度在6-18为之间'}
'''
设计测试用例：
1、账号、密码正确                ---》{'code': 0, 'msg': '登录成功'}
2、账号正确，密码长度在6-18为之间 ---》{'code': 1, 'msg': '账号或密码不正确'}
3、账号正确，密码长度小于6位      ---》{'code': 0, 'msg': '密码长度在6-18为之间'}
4、账号正确，密码长度大于6位      ---》{'code': 0, 'msg': '密码长度在6-18为之间'}
5、账号错误，密码正确            ----》{'code': 1, 'msg': '账号或密码不正确'}
'''
```

```python
class LoginTestCase(unittest.TestCase):
    """测试登录功能函数的测试用例"""

    # 方法名需要以test开头，一个方法代表一个用例
        def test_login_success(self):
        """登录成功"""
        excepted = {'code': 0, 'msg': '登录成功'}
        res = login_check('xiaoming', '12456')
        try:
            self.assertEqual(excepted, res)	
        except AssertionError as e:
            print('用例执行未通过')	# print可以输出内容到测试报告
            print(f'预期结果：{excepted}')
            print(f'实际结果：{res}')
            raise e	# 捕获断言异常后，必须抛出。unittest通过异常判断用例是否通过
        else:
            print('用例执行通过')
            print(f'预期结果：{excepted}')
            print(f'实际结果：{res}')

    def test_password_error1(self):
        excepted = {'code': 0, 'msg': '登录成功'}
        res = login_check('xiaoming', '12345')
        self.assertEqual(excepted, res)
    ...
```

- 注：类和用例添加文档注释，在生成HTML测试报告时给接口和测试方式也添加响应注释

#### 三、生成测试套件

```python
suite = unittest.TestSuite()	# 创建测试套件
# 方法一：将一个用例用addTest(模块名('方法名'))添加到测试套件
suite.addTest(LoginTestCase('test_login_success'))

# 方法二：通过测试用例类来加载用例-loadTestsFromTestCase(测试用例类)
loader = unittest.TestLoader()	# 创建一个loader对象来加载用例
suite.addTest(loader.loadTestsFromTestCase(LoginTestCase))

# 方法三：通过测试类所在模块来加载用例-loadTestsFromModule(模块)
suite.addTest(loader.loadTestsFromModule(login_test))

# 方式四：添加一个路径下的所有测试用例-discover()，识别test开头的py文件作为测试用例
suite.addTest(loader.discover(r"模块所在目录路径"))
```

#### 四、执行测试用例

```python
runner = unittest.TextTestRunner()
runner.run(suite)
```

#### 五、断言

| 方法                 | 检查            |
| -------------------- | --------------- |
| assertEqual(a, b)    | a==b            |
| assertNotEqual(a, b) | a!=b            |
| assertTrue(a)        | boo(a) is True  |
| assertFalse(a)       | boo(a) is False |
| assertIs(a, b)       | a is b          |
| assertIsNot(a, b)    | a is not b      |
| assertIn(a, b)       | a in b          |
| assertInNot(a, b)    | a not in b      |

#### 六、生成HTML测试报告

```python
# github下载HTMLTestRunnerNew.py放在python下lib库中
from HTMLTestRunnerNew import HTMLTestRunner
with open('report.html', 'wb')as fb:
    runner = HTMLTestRunner(stream=fb,
                            verbosity=2,
                            title='小明测试',
                            description='接口测试用例',
                            tester='xiaoming')
    runner.run(suite)
```

#### 七、测试运行环境

```python
def setUp(self):
	pass	# 测试用例执行前执行
def tearDown(self):
    pass	# 测试用例执行后执行
@classmethod
def setUpClass(cls):
    pass	# 测试用例类执行前执行
@classmethod
def tearDownClass(cls):
    pass	# 测试用例类执行后执行
```

