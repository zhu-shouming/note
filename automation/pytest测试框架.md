##### 一、安装

- pip install -U pytest    #安装pytest
- pip install pytest -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com # 指定镜像源安装
- pytest --version	# 查看安装的版本

##### 二、pytest设计用例规则

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

##### 三、pytest执行用例规则

1. pycharm设置运行

   - 打开PyCharm，依次打开Settings--->Tools--->Python Integrated Tools， 将Testing里的Default test runner选择项选为pytest，保存即可

   - 右键运行

2. 命令行执行：pytest [参数] 文件名

3. main函数运行：pytest.main([参数, 文件名], plugins)

4. 常用参数
   - -s：带控制台输出结果，也是输出详细运行日志	
   - -m：指定标签运行
   - -k：模糊匹配，测试用例的部分字符串，指定执行测试用例
   - -n：支持多线程或者分布式运行测试用例（需安装：pytest-xdist插件）
   - –reruns NUM：失败用例重跑，跑几次（需安装：pytest-rerunfailures插件）
   - -x：表示只要有一个测试用例报错，则执行停止
   - –maxfail=2：表示出现2个用例报错，则执行停止
   - –html ./report/report.html：生成html格式的测试报告（需安装：pytest-html插件）
   - order：改变用例默认执行顺序，使用@pytest.mark.run(order=1)标记测试用例
   - skip：指定条件跳过某些用例@pytest.mark.skip()

5. 用例执行后的状态
   - PASSED：测试通过
   - FAILED：断言失败
   - ERROR：用例本身写的质量不行，本身代码报错（例如：fixture 不存在，fixture 里面有报错）
   - XFAIL：预期失败，加了 @pytest.mark.xfail()

##### 四、pytest标签功能

1. 自定义标签、执行

   - 使用@pytest.mark.标签名 装饰用例函数

   - 使用类属性打标签：pytestmark=[pytest.mark.标签1, ...]

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

     ```bash
     pytest.main(['-m success', '脚本'])	# 方式一：py文件中运行带success标签的用例
     pytest -m "success" 脚本	# 方式二：命令行运行
     ```

   - 注册mark标记，消除pytest告警

     ```bash
     # pytest.ini配置文件中配置，若没有则新建pytest.ini文件
     [pytest]
     markers =
         success : marks test as success
         login   : marks test as login
     
     addopts = --strict
     ```

     注：pytest.ini配置文件中addopts添加--disable-warnings参数忽略其它告警信息

2. 内置标签的使用

   - @pytest.mark.skip：满足某些条件才执行用例，否则pytest会跳过运行改用例
   - @pytest.mark.skipif(condition, reason="") 希望有条件地跳过某些测试用例。注意：condition 需要返回 True 才会跳过。

#####  五、pytest环境管理

1. 测试用例前后置条件
   - 模块级（开始于模块始末，全局的）：setup_module()、teardown_module()
   - 函数级（只对函数用例生效，不在类中）：setup_function()、teardown_function()
   - 类级（只在类中前后运行一次，在类中）：setup_class()、teardown_class()
   - 方法级（开始于方法始末，在类中）：setup_method()、teardown_method()
   - 方法细化级（运行在调用方法的前后）：setup()、teardown()

2. pytest夹具-fixture

   **fixture的参数列表**

   ```python
   @pytest.fixture(scope="function", params=None, autouse=False, ids=None, name=None)
   ```

   - scope：fixture的作用域，默认function，还有class、module、package、session
   - params：一个可选的参数列表，它将导致多个参数调用 fixture 功能和所有测试使用它
   - autouse：默认：False，需要用例手动调用该 fixture；如果是 True，所有作用域内的测试用例都会自动调用该 fixture
   - ids：每个字符串 id 的列表，每个字符串对应于 params，这样他们就是测试ID的一部分。如果没有提供ID，它们将从 params 自动生成
   - name：默认为装饰器的名称，同一模块的 fixture 相互调用建议写不同的名称

​	**fixture夹具的使用**

 1. 将夹具装饰的函数作为参数传递到测试用例函数中

    ```python
    import pytest
    
    @pytest.fixture()   # 声明函数是一个fixture
    def fixturefun():
        return 123
    
    def test_case(fixturefun):  # 测试用例的参数化包含fixture函数，则测试用例运行前会执行此函数。如果fixture函数有返回值，则将返回值传递给测试用例函数
        assert fixturefun == 123
    ```

	2. 使用@pytest.mark.usefixtures(fixture_name)装饰测试方法

    ```python
    import pytest
    
    @pytest.fixture()
    def fixture_fun():
        return 123
    
    @pytest.mark.usefixtures(fixture_fun)
    def test_case():
        assert fixture_fun == 123	# 这行代码会出错，当使用这种方法初始化测试用例，夹具函数中的返回值不会传到测试用例中
    ```

	3. fixture 设置 autouse=True，在所有作用域内的测试用例都会自动调用该 fixture

    ```python
    import pytest
    
    @pytest.fixture(autouse=True) 
    def fixturefun():
        return 123
    
    def test_case(): 
        assert fixturefun == 123	#这行代码报错，使用这种方法返回值也不会传入测试用例中
    ```

    注：1.在fixture夹具中断言失败，结果为error;

    2.在类声明上加@pytest.mark.usefixtures(fixture_fun)，代表整个类里面所有测试用例都会调用fixture

	4. fixture的实例化顺序

    > fixture 的 scope 实例化优先级：session > package > module > class > function
    >
    > 自动使用（autouse=True）的 fixture 将在显式使用（传参或装饰器）的 fixture 之前实例化
    >
    > 具有相同作用域的 fixture 遵循测试函数中声明的顺序，并遵循 fixture 之间的依赖关系。在 fixture_A 里面依赖的 fixture_B 优先实例化，然后到 fixture_A 实例化

	5. fixture重命名

    ```python
    import pytest
    
    @pytest.fixture(name="test")
    def fixture_fun():
        return 123
    
    def test_case(test):
        assert test == 123
    ```

	6. fixture之yield：测试后执行

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

	7. conftest.py之fixture

    > 可以把所有fixture放到conftest.py文件中
    >
    > 作用范围是当前文件所在目录及子目录的测试模块
    >
    > conftest.py文件位置必须在执行运行命令的目录下

##### 六、pytest参数化

```python
import pytest

test_data = [{"user": "xiaoming"}, {"user": "xiaohong"}]

@pytest.mark.parametrize('data', test_data)
def test_login(data):
    print(data)
```

##### 七、断言

- assert xx ：判断 xx 为真
- assert not xx ：判断 xx 不为真
- assert a in b ：判断 b 包含 a
- assert a == b ：判断 a 等于 b
- assert a != b ：判断 a 不等于 b

##### 八、生成测试报告

- 简易html报告，下载：pip install pytest-html

  ```bash
  pytest -v --html=report/result.html 要执行的文件
  pytest -v --html=测试报告的路径 --self-contained-html 要执行的文件	# 不生成assets目录
  ```
  
- 生成allure报告

  1. 安装allure-pytest插件：pip install allure-pytest

  2. 执行脚本，生成json格式测试结果：**pytest --alluredir=report --clean-alluredir 执行的文件或文件所在目录** 

     - --alluredir=指定生成结果路径
     - --clean-alluredir：先清空目录，再生成测试结果

  3. 将json执行结果转换成html报告：**allure generate 生成测试结果数据 -o 生成报告的路径 --clean**，

     1. 安装jdk，配置环境变量
     2. 下载allure开源测试框架，解压allure压缩包，将allure路径下bin文件加入环境变量

     3. 终端输入allure --version检测是否配置完成

  4. Allure常用特性

     - @allure.feature(用于描述被测试产品需求)
     - @allure.story(用于描述feature的用户场景，即测试需求)
     - @allure.description(描述测试用例)
     - @allure.step()或with allure.step():用于描述测试步骤，将会输出到报告中
     - allure.attach：用于向测试报告中输入一些附加的信息，通常是一些测试数据，截图等
     - @allure.title:给测试用例添加标题
     - allure.dynamic：有很多属性，如title、feature，动态添加allure相关注释

##### 九、pytest重运行

- 安装：pip install pytest-returnfailures

  > 执行：pytest --reruns 3 --reruns-delay 5
  >
  > 3表示重运行次数，5表示两个用例间隔时间秒

##### 十、pytest控制用例执行顺序

- 通过`pytest-ordering`插件来控制用例执行顺序

1. 安装：pip install pytest-ordering

2. pytest-ordering的使用方法：在测试方法上加装饰器即可

   ```python
   @pytest.mark.run(order=x)	# x是正整数，如x为0表示第一个执行
   ```





