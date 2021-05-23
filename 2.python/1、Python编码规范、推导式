###### 说明:不要为了遵守PEP约定而破坏兼容性

```python
# 1、主动换行
def foo_bar(self, width, height, color='black',
           design=None )

# 2、合理使用括号实现隐式连接
if (width == 0 and height == 0 and
   color == 'red' ):
# 3、使用圆括号实现隐式连接行
x = ('这是一首简单的小情歌，唱着我心头的曲折，'
    '我想我们很快乐')

# 4、注释中，如何出现URL，请写在一行
> http://www.xxx.com/asdfsdf

# 5、不要在返回值或条件语句中使用括号，除非需要数学计算或行连接

# 6、函数参数与起始变量对齐
foo = long_function_name(var_one, var_two,
                         var_three,var_four)

# 7、顶级定义之间空两行，方法定义之间空一行

# 8、括号参数里面不要有空格

# 9、逗号，冒号，分号后面添加空格

# 10、不要空格垂直对齐注释

# 11、文档注释

# 12、代码块中，对于复杂的操作，应该再其操作开始前写若干行注释

# 13、如果一个类不继承其他类，就显式的从object继承，嵌套也一样
class OuterClass(object):
    
    class InnerClass(object):
        pass
    
# 15、避免在循环中用+和+=操作符来累加字符串，由于字符串是不可变的，这样做会创建不必要的临时变量。可以将每个子串加入列表，用join()连接列表

# 16、为多行字符串使用三重双引号“”“而非三重单引号‘’‘

# 17、关闭类文件对象的方法，对于不支持使用“with”语句的类似文件的对象，使用contextlib.closing()
import contextlib

with contextlib.closing(urllib.urlopen("http://www.python.org/"))as front_page:
    for line in front_page:
        print(line)

# 18、为临时代码使用TODO注释
# TODO：优化函数

# 19、每个导入独占一行，顺序如下：1、标注库导入；2、第三方库导入；3、应用程序制定导入

# 20、在没有else的情况，if语句可以独占一行

# 21、在单下划线（_）开头表示模块变量或函数时proteced（在其他文件中导入属性时不包含）

# 22、用双下划线（__）开头的实例变量或方法表示类私有

# 23、将相关的类和顶级函数放在同一个模块中，没必要限制一个类一个模块
```

### 推导式

##### 列表推导式

```python
li = [f'data{i}' for i in range(10)]
```

##### 字典推导式

```python
{i : random.randint(10, 100) for i in range(1, 5)}
```

