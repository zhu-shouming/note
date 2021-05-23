##### 1、ddt原理：【Data driver test】

- ddt是一个装饰器

- ddt会根据你传递进来的数据来决定要生成几个测试用例

- 安装

  > pip install ddt

##### 2、ddt实现数据驱动

```python
# 测试用例类
@ddt
class RegisterTestCase(unittest.TestCase):
    excel = ReadExcel(r'cases.xlsx', 'Sheet1')	
    cases = excel.read_data_obj()
    @data(*cases)
    def test_login(self, case):
        # 表格读取的数据只有字符串和数字类型，转化为python类型
        excepted = eval(case.excepted)	
        data = eval(case.data)
        result = login_check(*data)
        try:
            self.assertEqual(excepted, result)
        except AssertionError as e:
            print('测试用例未通过')
            print(f'期望结果：{excepted}')
            print(f'实际结果：{result}')
            self.excel.write_data(case.case_id + 1, 4, 'Fail')	# 测试结果写入到excel
            raise e
        else:
            print('测试用例通过')
            print(f'期望结果：{excepted}')
            print(f'实际结果：{result}')
            self.excel.write_data(case.case_id + 1, 4, 'Success')
```

```python
# 测试套件存放的类
import unittest
from HTMLTestRunnerNew import HTMLTestRunner

suite = unittest.TestSuite()
loader = unittest.TestLoader()
# 通过discover加载测试用例，测试用例的py文件需要以test开头命名
suite.addTest(loader.discover(r'测试用例存放的路径'))
with open('report.html', 'wb')as fb:
    runner = HTMLTestRunner(stream=fb,
                            verbosity=2,
                            title='测试注册函数',
                            description=None,
                            tester='小明')
    runner.run(suite)
```

##### 3、ddt显示测试用例标题

```python
# 找到ddt函数，修改test_data_docstring，确保表格用例设计标题为title
# test_data_docstring = _get_test_data_docstring(func, v)
test_data_docstring = v.title
```

