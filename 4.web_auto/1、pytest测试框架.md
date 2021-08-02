#### 一、安装

> pip install -U pytest	# 安装pytest
>
>  pip install pytest -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com	# 指定镜像源安装
>
> pytest --version	# 查看安装的版本

#### 二、pytest设计用例规则

1.  文件名以 test_*.py 文件和 *_test.py 文件 
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

#### 四、设置运行pytest

##### 一、pycharm设置运行

1.  打开PyCharm，依次打开Settings--->Tools--->Python Integrated Tools， 将Testing里的Default test runner选择项选为pytest，保存即可  
2.  右键运行 

##### 二、pytest.main()设置运行

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

####  五、pytest前后置条件
- 模块级（开始于模块始末，全局的）：setup_module()、teardown_module()
- 函数级（只对函数用例生效，不在类中）：setup_function()、teardown_function()
- 类级（只在类中前后运行一次，在类中）：setup_class()、teardown_class()
- 方法级（开始于方法始末，在类中）：setup_method()、teardown_method()
- 方法细化级（运行在调用方法的前后）：setup()、teardown()
##### fixture
> - 命名方式灵活，不局限于 setup 和 teardown 这几个命名
> - conftest.py 配置里可以实现数据共享，不需要 import 就能自动找到 fixture
> - scope="module" 可以实现多个 .py 跨文件共享前置
> - scope="session" 可以实现多个 .py 跨文件使用一个 session 来完成多个用例
**1.fixture的参数列表**
```python
@pytest.fixture(scope="function", params=None, autouse=False, ids=None, name=None)
def test():
    print("fixture初始化的参数列表")
```
- scope:fixture的作用域，默认function，还有class、modUle、package、session
- params：一个可选的参数列表，它将导致多个参数调用 fixture 功能和所有测试使用它
- autouse：默认：False，需要用例手动调用该 fixture；如果是 True，所有作用域内的测试用例都会自动调用该 fixture
- ids：每个字符串 id 的列表，每个字符串对应于 params，这样他们就是测试ID的一部分。如果没有提供ID，它们将从 params 自动生成
- name：默认：装饰器的名称，同一模块的 fixture 相互调用建议写不同的名称
**2.测试用例调用fixture**
1.将 fixture 名称作为测试用例函数的输入参数
```python
import pytest

@pytest.fixture()   # 声明函数是一个fixture
def fixturefun():
    return 123

def test_case(fixturefun):  # 测试用例的参数化包含fixture函数，则测试用例运行前会执行此函数。如果fixture函数有返回值，则将返回值传递给测试用例函数
    assert fixturefun == 123
```
2.测试用例加上装饰器：@pytest.mark.usefixtures(fixture_name)
3.fixture 设置 autouse=True
注：
- 在类声明上面加 @pytest.mark.usefixtures() ，代表这个类里面所有测试用例都会调用该 fixture
- 可以叠加多个 @pytest.mark.usefixtures() ，先执行的放底层，后执行的放上层
- 可以传多个 fixture 参数，先执行的放前面，后执行的放后面
- 如果 fixture 有返回值，用 @pytest.mark.usefixtures() 是无法获取到返回值的，必须用传参的方式（方式一）
- 在fixture里面断言失败结果为error，测试用例断言失败为failed
**3.fixture的实例化顺序**
- fixture 的 scope 实例化优先级：session > package > module > class > function
- 具有相同作用域的 fixture 遵循测试函数中声明的顺序，并遵循 fixture 之间的依赖关系。在 fixture_A 里面依赖的 fixture_B 优先实例化，然后到 fixture_A 实例化
- 自动使用（autouse=True）的 fixture 将在显式使用（传参或装饰器）的 fixture 之前实例化
**4.fixture之request**

