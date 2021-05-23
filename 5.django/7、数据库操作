### 1、c（create）：创建数据

- 方式一：通过创建模型类实例，调用save()执行sql语句

```python
# django提供的命令行终端：python manage.py shell，或视图中均可创建数据
from pools.models import Projects
one = Projects(name='测试开发平台项目', leader='小明', is_excute=True)
one.save()

# 查看生成的SQL语句
from django.db import connection
connection.queries
```

- 方式二：使用模型类manager对象（模型类.objects）的**create()**方法

```python
Projects.objects.create(name='某某某金融项目', leader='小明', dess='描述')
```

- 添加子表数据

```python
one_project = Projects.objects.create(name='某某某金融项目', leader='小明', dess='描述')
# 方式一：通过从表生成的字段(projects_id)关联父表中的数据
Interface.objects.create(name='登录接口', tester='anny', projects_id=one_project.id)

# 方式二：通过从表的类属性(projects)关联父表的实例(one_project)
Interfaces.objects.create(name='登录接口', tester='jack', projects=one_project)
# 注：从表外键字段常命名为父表类名小写
```

### 2、r（retrieve）：读取数据

- **all()方法**：People.objects.all()获取模型类所有数据

  > 返回QuerySet对象（类似列表），支持for循环迭代、索引取值和切片，但不能支持负值索引
  >
  > QuerySet对象特性：
  >
  > ​	1、惰性查找，需要用到数据时才执行sql获取数据
  >
  > ​	2、链式调用：查询集对象可以都次调用filter()进行过滤，逻辑与关系
  >
  > ​	3、支持first()方法，取出查询集中的第一个元素，为模型类对象
  >
  > ​	4、last()方法，取出查询集中的最后一个元素，为模型类对象
  >
  > ​	5、len()、count()方法，获取查询集长度
  >
  > ​	6、exits():判断查询集是否有元素，有元素返回True，否则返回False
  >
  > ​	7、字段排序操作：查询集对象.order_by('字段名1', '-字段名2')，可以在字段前添加-，代表以降序排序

- **get()方法**：Projects.objects.get(id=1)读取一条数据

  注：如果查询的结果为空或超过一条，会抛出异常。常用于id主键查询或唯一约束字段查询

- **filter()方法**：People.objects.filter(**字段名__查询类型 = 具体值**)，返回QuerySet对象  

  查询类型的种类有：

  > | 查询类型   | 含义                  |例子|
  > | ---------- | --------------------- | --------------------- |
  > | exac       | =                     |id__exac=3|
  > | gt         | >                     |id__gt=2|
  > | gte        | >=                    ||
  > | lt         | <                     ||
  > | lte        | <=                    ||
  > | in         | 对列表中的值进行过滤  |id__in=[1, 3]|
  > | contains   | 包含                  |name__contains='金融'|
  > | icontains  | 包含，忽略大小写      ||
  > | startwith  | 以...开头          ||
  > | istartwith | 以...开头，忽略大小写 ||
  > | endwith    | 以...结尾           ||
  > | iendwith   | 以...结尾，忽略大小写 ||
  > | isnull     | 是否为空              ||

- **exclude()方法**：反向查询

  ```python
  # exclude与filter为反向关系
  People.objects.filter(id__gt=3)	# 等价于
  People.objects.exclude(id__lte=3)
  ```
  
- **多条件查找**

  - 逻辑与查询

    ```python
    People.objects.fileter(name__contains='xiaoming').filter(age=18) # 写法一
    People.objects.fileter(name__contains='xiaoming', age=18)	# 写法二
    ```

  - 逻辑或查询

    ```python
    from django.db.models import Q
    # 多个Q对象使用|为或的关系，使用&为与的关系
    People.objects.filter(Q(name_contains='xiao') | Q(age=18))
    ```

- **关联查询**：Projects.objects.filter(`关联模型类名小写__字段名__查询类型=具体值`)

  > 如:查询项目表中包含登录接口的项目信息
  >
  > 写法一：`Projects.objects.filter(interfaces__name__contains='登录')`
  >
  > 写法二：1、获取登录接口名查询集对象；2、取出查询对象关联外键字段
  >
  > ​	qs = Interfaces.objects.filter(name__contains='登录')
  >
  > ​	qs[0].projects	
  >
  > 注：若是有三张以上的表关联，可使用‘`关联模型类1小写__ 关联模型类1外键名__关联模型类2字段名__查询类型=具体指`’

### 3、u（update）：更新数据

- 方式一：获取模型类对象，重新赋值，调用save()提交修改

```python
one_project = Projects.objects.get(id=4)
one_project.name = 'xiaolin'
one_project.save()
```

- 方式二：manager对象的update()方法

```python
Projects.objects.filter(id=4).update(leader='安妮')
```

### 4、d（delete）：删除数据

- 方式一：调用模型类中的delete方法

```python
one = People.objects.get(pk=1)
one.delete()
```

- 方式二：使用查询集对象.delete()

```python
People.objects.filter(name__contains='xiao').delete()
```

### 5、聚合运算

```python
from django.db.models import Count, Min, Max, Avg
'''
values和annotate为固定用法
聚合运算的别名会自动设置从表小写__聚合函数名小写 ，可以给聚合运算设置关键词参数作为聚合运算的别名
'''
# 聚合运算需要设置为从表名小写，如：Count('interfaces')，使用外键id作为关联条件，同时也会把外键id作为分组条件，默认查询id和聚合运算的值
Projects.objects.values('id').annotate(Count('interfaces'))	# 查询每个项目下的接口总数
Projects.objects.values('id').annotate(haha=Count('interfaces'))
```



```python
# 随机创建20条接口信息
import random
import string
names = ['登录接口', '注册接口', '订单接口', '购物车接口']
for i in range(20):
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    interface_name = random.choice(names) + random_str
    Interfaces.objects.create(name=interface_name, test='xxx', people_id=random.choice([1,2,3,4]))
"""
需求：开发5个接口，前端可以对项目进行增删改查操作
1.需要能获取到项目的列数数据（获取所有数据）
	url: /projects/
    method：GET
    response data: json
2.需要能获取到项目的详情数据（获取前端指定某一条数据）
	url: /projects/<int:pk>/
    method：GET
    response data: json
3.能够创建项目（创建一个项目）
	url: /projects/
    method：POST
    request data: json
    response data: json
4.能够更新项目（只更新某一个项目）
    url: /projects/<int:pk>/
    method：PUT
    request data: json
    response data: json
5.能够删除项目（只删除某一个项目）
    url: /projects/<int:pk>/
    method：DELETE

总结：
1.获取列表数据&获取详情数据
	a.数据库读取操作
	b.将模型类对象转化为python中的基本类型，也叫序列化操作
2.创建数据
	a.数据校验
	b.将json字符串转化为python的基本类型，也叫反序列化操作
	c.数据库写入操作
3.更新数据
	a.数据校验
	b.反序列化操作
	c.数据库更新操作
4.删除数据
	a.数据校验
	b.数据库删除操作
"""
```



