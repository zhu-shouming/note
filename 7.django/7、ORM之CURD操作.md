#### 一、使用创建模型类实例方式实现CURD操作

```python
# 查看执行的SQL语句
from django.db import connection
connection.queries
```

##### 1、创建数据

```python
# django提供的命令行终端：python manage.py shell，或视图中均可创建数据
# 1、导入模型类
from projects.models import Project
# 2、创建模型类实例，关键字参数的形式添加参数
a = Project(name='测试开发平台项目', leader='xiaoming')
# 3、保存数据  
one.save()
```

##### 2、读取数据

```python
# 通过对象实例.属性值获取数据
>>>one.name	
'测试开发平台项目'
```

##### 3、更新数据

```python
# 1.通过对象实例.属性值=值 修改属性值
one.leader = 'xiaohong'
# 2.通过save()保存修改的数据
one.save()
```

##### 4、删除数据

```python
one.delete()
```

#### 二、使用模型类manager对象实现CURD操作

模型类manager对象：<font color="red">模型类.objects</font> 

##### 1、创建数据

> 使用manager对象create()方法，通过关键字传参的方式传递数据

```python
# 导入父表、子表模型类
from projects.models import Project
from interfaces.models import Interface
one_project = Project.objects.create(name='xxx金融项目2', leader='xiaofang')

# 添加子表数据
# 方式一：通过project_id=one_project.id关联父表的id
Interface.objects.create(name='登录接口', tester='jack', project_id=one_project.id)
# 方式二：通过project=one_project关联父表数据
Interface.objects.create(name='注册接口', tester='anny', project=one_project)
```

##### 2、查询数据

- 查询一条数据

  ```python
  # 方式一：使用manager对象的get()方法，返回一个Project模型类对象。
  # 当get查询的数据为空或者多条时，会抛出异常。
  one_project = Project.objects.get(id=8)
  
  # 方式二：使用manager对象的filter()方法，返回一个QuerySet对象。
  # 当filter查询的数据为空，返回空的QuerySet对象
  # 当filter查询的数据多条时，返回的结果也会在QuerySet对象中
  one_project = Project.objects.filter(id=8)
  ```

- 查询表中所有数据：all()方法

  ```python
  # 返回一个QuerySet查询集对象
  all_projects = Project.objects.all()
  ```

##### 3、更新数据

```python
# 获取待修改的数据取出（查询集对象），调用update()方法更新数据
Project.objects.filter(id=5).update(leader='小红')
```

##### 4、删除数据

```python
Project.objects.filter(name__contains='xxx').delete()
```

#### 三、filter方法的使用

```python
Projects.objects.filter(字段名__查询类型=具体值)
```

- **对数字、日期进行操作**

| 查询类型 | 含义         |
| -------- | ------------ |
| exac     | =            |
| gt       | >            |
| gte      | >=           |
| lt       | <            |
| lte      | <=           |
| in       | 在成员范围中 |

- **对字符串进行操作**

| 查询类型   | 含义                  |
| ---------- | --------------------- |
| contains   | 包含                  |
| icontains  | 包含，忽略大小写      |
| startwith  | 以...开头             |
| istartwith | 以...开头，忽略大小写 |
| endwith    | 以...结尾             |
| iendwith   | 以...结尾，忽略大小写 |
| isnull     | 是否为空              |

- **exclude()方法**：反向查询

  ```python
  # exclude与filter为反向关系
  People.objects.filter(id__gt=3)	# 等价于
  People.objects.exclude(id__lte=3)
  ```

#### 四、关联查询

1、通过<font color='red'> `关联模型类小写__关联模型类中的字段名__查询类型=具体值`</font>

```python
# 需求：查找某个项目下的登录接口
Project.objects.filter(interface__name__contains='登录')
# 需求：获取某个项目下的所有接口
# 可以在interface后面加上_set进行反向查询，如果关联字段定义了related_name='interface'，可以直接使用interface来反向获取数据
Projct.objects.get(id=x).interface.all()
```

2、获取接口的查询集对象，查询集对象取值.父表模型类小写

```python
# 需求：获取登录接口所属的项目
qs = Interface.objects.filter(name__contains='登录')
qs[0].project
```

3、多表关联：`关联模型类1小写__关联模型类1中的外键名__关联模型类2中的字段名__查询类型=具体值`

#### 五、多条件查询

- 逻辑与

  ```python
  Project.objects.fileter(name__contains='商').filter(leader='a') # 写法一
  Project.objects.fileter(name__contains='商', leader='a')	# 写法二
  ```

- 逻辑或

  ```python
  from django.db.models import Q
  # 多个Q对象使用|为或的关系，使用&为与的关系
  Project.objects.filter(Q(name_contains='商') | Q(leader='a'))
  ```

#### 六、查询集对象特性

1. 惰性查找：需要用到数据时才执行sql语句
2. 类似列表：支持for循环迭代、切片、索引取值（不支持负索引）
3. 链式调用
4. first()：取出查询集中的第一个元素，为模型类对象
5. last()：取出查询集中的最后一个元素，为模型类对象
6. len()、count()方法：获取查询集长度
7. exits():判断查询集是否有元素，有元素返回True，否则返回False
8. 字段排序操作：查询集对象.order_by('字段名1', '-字段名2')，可以在字段前添加-，代表以降序排序

#### 七、聚合运算

> **values**和**annotate**为固定用法
>
> 聚合运算需要设置为从表名小写，使用外键id作为关联条件，同时会把外键id作为分组条件
>
> 默认查询id和聚合运算的值，聚合运算的别名会自动设置为从表名__聚合函数名小写
>
> annotate中使用关键字传参的方式，键作为聚合运算的别名

```python
from django.db.models import Count, Min, Max, Avg

# 查询每个项目下的接口总数
Project.objects.values('id').annotate(Count('interface'))
# 查询每个项目下的接口总数，并把聚合运算取名为haha
Project.objects.values('id').annotate(haha=Count('interface'))
```

