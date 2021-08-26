#### 一、安装

> pip install -U pytest	# 安装pytest
>
> pip install pytest -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com	# 指定镜像源安装
>
> pytest --version	# 查看安装的版本

#### 二、pytest设计用例规则

1.  文件名以 `test_*.py` 文件和 `*_test.py` 文件 
2.  以 test_ 开头的函数 
3.  以 Test 开头的类， 以 test_ 开头的的方法，且不能包含` __init__ `方法  
4.  所有的包 Package 必须要有` __init__`.py 文件 

```python
# test_demo.py

class TestDemo:
    def test_one(self):
        x = "this"
        assert 'h' in x
```

#### 三、pytest执行用例规则

##### 1、pycharm设置运行

1.  打开PyCharm，依次打开Settings--->Tools--->Python Integrated Tools， 将Testing里的Default test runner选择项选为pytest，保存即可  
2.  右键运行 

##### 2.命令执行

| 命令                                | 作用                                             |
| ----------------------------------- | ------------------------------------------------ |
| pytest                              | 目录下执行所有的用例                             |
| pytest 文件名.py                    | 执行单独一个pytest模块                           |
| pytest 文件名.py::类名              | 执行某个模块里面的某个类                         |
| pytest 文件名.py::类名::方法名      | 执行某个模块里面某个类里的方法                   |
| pytest -v 文件名.py                 | -v打印运行日志信息（详细）                       |
| pytest -q 文件名.py                 | -q打印运行日志信息（简略）                       |
| pytest -v -s 文件名.py              | -s是带控制台输出结果，也是输出详细运行日志       |
| pytest -m login                     | 将运行用 @pytest.mark.login 装饰器修饰的所有测试 |
| pytest -x 文件名.py                 | -x用例运行失败则立即停止执行                     |
| pytest -v -k "one" 文件名.py        | 执行测试用例名称包含 one 的所有用例              |
| pytest -v -k "not one" 文件名.py    | 执行测试用例名称不包含 one 的所有用例            |
| pytest -v -k "one or two" 文件名.py | 执行测试用例名称包含 one 或 two 的所有用例       |
| pytest 文件名.py --maxfail=1        | 用例运行时允许的最大失败次数，超过则立即停止     |

##### 3、pytest.main()设置运行

**main函数有2个可选参数**

-  args：命令行参数列表
-  plugins：初始化期间要自动注册的插件对象列表 

| 命令                                                 | 作用                                              |
| ---------------------------------------------------- | ------------------------------------------------- |
| pytest.main()                                        | 等价于直接运行pytest命令                          |
| pytest.main(["-s"])                                  | 在命令行运行pytest -s                             |
| pytest.main(["-s", "-x"])                            | 在命令行运行pytest -s -x                          |
| pytest.main(["test/case"])                           | 执行test/case文件夹下的全部用例                   |
| pytest.main(["test/case/test_case1.py"])             | 执行test/case/test_case1.py文件里的全部用例       |
| pytest.main(["test/case/test_case1.py::test_login"]) | 执行test/case/test_case1.py文件里的test_login用例 |
| pytest.main(["test/case"], plugins=[插件名])         | 加载指定插件                                      |

##### 4、用例执行后的状态

> PASSED：测试通过
>
> FAILED：断言失败
>
> ERROR：用例本身写的质量不行，本身代码报错（例如：fixture 不存在，fixture 里面有报错）
>
> XFAIL：预期失败，加了 @pytest.mark.xfail()

#### 四、pytest标签功能

##### 1、自定义标签

- 使用@pytest.mark.标签名 装饰用例函数

```python
import pytest

@pytest.mark.success
def test_login():
    assert True

@pytest.mark.login
def test_1():
    assert False
```

- 选择执行用例，标签名之间可以使用or/and/not选择执行

  > 方式一：py文件里pytest.main(['-m success'])
  >
  > 方式二：pytest -m "success"

- 注册mark标记，消除pytest告警

  ```python
  # 执行目录下新建pytest.ini文件
  [pytest]
  markers =
      success : marks test as success
      login   : marks test as login
  
  addopts = --strict
  ```

##### 2、内置标签

- @pytest.mark.skip：满足某些条件才执行用例，否则pytest会跳过运行改用例
- @pytest.mark.skipif(condition, reason="") 希望有条件地跳过某些测试用例。注意：condition 需要返回 True 才会跳过。

##### 3、用例打标签的方式

- 使用装饰器打标签：@pytest.mark.标签名
- 使用类属性打标签：pytestmark=[pytest.mark.标签1, ...]

####  五、pytest环境管理

##### 1、测试用例前后置条件

- 模块级（开始于模块始末，全局的）：setup_module()、teardown_module()
- 函数级（只对函数用例生效，不在类中）：setup_function()、teardown_function()
- 类级（只在类中前后运行一次，在类中）：setup_class()、teardown_class()
- 方法级（开始于方法始末，在类中）：setup_method()、teardown_method()
- 方法细化级（运行在调用方法的前后）：setup()、teardown()
##### 2、pytest夹具-fixture
**a、fixture的参数列表**

```python
@pytest.fixture(scope="function", params=None, autouse=False, ids=None, name=None)
```
- scope：fixture的作用域，默认function，还有class、module、package、session
- params：一个可选的参数列表，它将导致多个参数调用 fixture 功能和所有测试使用它
- autouse：默认：False，需要用例手动调用该 fixture；如果是 True，所有作用域内的测试用例都会自动调用该 fixture
- ids：每个字符串 id 的列表，每个字符串对应于 params，这样他们就是测试ID的一部分。如果没有提供ID，它们将从 params 自动生成
- name：默认为装饰器的名称，同一模块的 fixture 相互调用建议写不同的名称

**b、fixture夹具的使用**

- 1、将夹具装饰的函数作为参数传递到测试用例函数中

  ```python
  import pytest
  
  @pytest.fixture()   # 声明函数是一个fixture
  def fixturefun():
      return 123
  
  def test_case(fixturefun):  # 测试用例的参数化包含fixture函数，则测试用例运行前会执行此函数。如果fixture函数有返回值，则将返回值传递给测试用例函数
      assert fixturefun == 123
  ```

- 2、使用@pytest.mark.usefixtures(fixture_name)装饰测试方法

  ```python
  import pytest
  
  @pytest.fixture()
  def fixture_fun():
      return 123
  
  @pytest.mark.usefixtures(fixture_fun)
  def test_case():
      assert fixture_fun == 123	# 这行代码会出错，当使用这种方法初始化测试用例，夹具函数中的返回值不会传到测试用例中
  ```

  注：在fixture夹具中断言失败，结果为error

- 3、fixture 设置 autouse=True，在所有作用域内的测试用例都会自动调用该 fixture

  ```python
  import pytest
  
  @pytest.fixture(autouse=True) 
  def fixturefun():
      return 123
  
  def test_case(): 
      assert fixturefun == 123	#这行代码报错，使用这种方法返回值也不会传入测试用例中
  ```

  注：在类声明上加@pytest.mark.usefixtures(fixture_fun)，代表整个类里面所有测试用例都会调用fixture

- 4、fixture的实例化顺序

  > fixture 的 scope 实例化优先级：session > package > module > class > function
  >
  > 自动使用（autouse=True）的 fixture 将在显式使用（传参或装饰器）的 fixture 之前实例化
  >
  > 具有相同作用域的 fixture 遵循测试函数中声明的顺序，并遵循 fixture 之间的依赖关系。在 fixture_A 里面依赖的 fixture_B 优先实例化，然后到 fixture_A 实例化

- 5、fixture重命名

  ```python
  import pytest
  
  @pytest.fixture(name="test")
  def fixture_fun():
      return 123
  
  def test_case(test):
      assert test == 123
  ```

- 6、fixture之yield：测试后执行

  ```python
  import pytest
  
  @pytest.fixture
  def fixture_fun():
      print("===测试前执行==")
      yield 123
      print("===测试后执行===")
  
  def test_case(fixture_fun):
      assert fixture_fun == 123
  ```

- 7、conftest.py之fixture

  > 1. 可以把所有fixture放到conftest.py文件中
  > 2. 作用范围是当前文件所在目录及子目录的测试模块
  > 3. conftest.py文件位置必须在执行运行命令的目录下

#### 六、pytest参数化

```python
import pytest

test_data = [{"user": "xiaoming"}, {"user": "xiaohong"}]

@pytest.mark.parametrize('data', test_data)
def test_login(data):
    print(data)
```

#### 七、断言

> assert xx ：判断 xx 为真
>
> assert not xx ：判断 xx 不为真
>
> assert a in b ：判断 b 包含 a
>
> assert a == b ：判断 a 等于 b
>
> assert a != b ：判断 a 不等于 b

#### 八、生成测试报告

- 简易html报告，下载：pip install pytest-html

  > 执行：pytest "--html=report/result.html"

#### 九、pytest重运行

- 安装：pip install pytest-returnfailures

  > 执行：pytest --reruns 3 --reruns-delay 5
  >
  > 3表示重运行次数，5表示两个用例间隔时间秒

