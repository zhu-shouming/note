#### ORM框架

##### 1、定义

- 把类和数据表进行映射
- 通过类和对象就能操作它所对应表格中的数据(CURD)

##### 2、创建数据库连接

- 配置数据库连接信息

  - 创建数据库和用户

    ```sql
    CREATE DATABASE my_database charset=utf-8mb4;
    GRANT ALL PRIVILEGES ON `*.*` TO 'xiaoming'@'%' IDENTIFIED BY '123456';
    flush privileges; 
    ```
    
  - 配置数据库，在全局配置文件下修改数据库配置

    ```python
    # 指定数据库的配置信息
    DATABASES = {
        # 使用的默认数据库信息
        'default': {
            # 指定使用的数据库引擎
            'ENGINE': 'django.db.backends.sqlite3',
            # 指定使用的数据库名称
            'NAME': BASE_DIR / 'db.sqlite3',
            # 指定数据库的用户名
            'USER': 'root',
            # 指定数据库的密码
            'PASSWORD': 123456,
            # 指定数据库的主机地址
            'HOST': 'localhost',
            # 指定数据库的端口号
            'PORT': 3306
        }
    }
    ```

  - 安装mysqlclient

##### 3.mysql中的对象与模型的关联

1. 数据库：需要手动创建数据库
2. 数据表
   - 与ORM中的模型类一一对应，在子应用的models.py中定义模型类
3. 字段
   - 与模型类的类属性一一对应
4. 记录
   - 与模型类对象一一对应

##### 4.定义一个模型并生成表

- 创建模型类

  > 1.定义模型类必须继承Model或Model子类，一个模型类相当于一个table
  >
  > 2.使用Field对象定义类属性，相当于表中的字段

  ```python
  class People(models.Model):
    	name = models.CharField(max_length=20)
      age = models.IntegerField()
  ```

- 生成迁移脚本

  会在子应用migrations/目录下生成迁移脚本

  > **python manage makemigrations [appname]**

  python manage.py -h可查看manage工具相关命令

  python manage.py sqlmigrate 应用程序 迁移脚本，查看创建表sql语句

- 执行迁移脚本

  生成的表名默认为：应用名_模型类名小写。默认会自动创建一个（自增、非空）的id主键。

  > **python manage migrate [appname]**

##### 5.模型类字段使用

- CharField指定varchar类型，必须设置max_length参数
- IntegerField设置整型字段
- AutoField设置字段自增
- BooleanField设置布尔类型字段
- TextField设置长文本类型字段
- DateTimeField指定日志时间类型字段

##### 6.模型类字段参数说明

- 字段参数设置primary_key=True后，ORM框架不会自动创建id主键
- db_index=True添加索引
- db_column指定字段名称，未设置字段名称默认为类属性名称
- 字段参数verbose_name、help_text指定中文描述，一般在admin后台站点或接口平台文档中使用
- unique=True设置唯一约束
- default设置当前字段默认值
- null指定当前字段是否允许为空值，blank指定前端在创建数据时是否允许不输入空值
- 参数auto_now_add=True，创建数据时，会自动把当前时间赋值给字段；auto_now=True，在更新数据时，会自动把当前时间赋值给字段。常用于DateTimeField模块

```python
# 项目表
class Projects(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id主键', help_text='id主键')
    name = models.CharField(unique=True, max_length=20, verbose_name='项目名称', help_text='项目名称')
    leader = models.CharField(max_length=20, verbose_name='项目负责人', help_text='项目负责人')
    is_execute = models.BooleanField(default=True, verbose_name='项目是否开展', help_text='项目是否展开')
    desc = models.TextField(null=True, verbose_name='项目描述信息', help_text='项目描述信息')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    
    # 模型类中添加文本描述
    def __str__(self):
    	return self.name
    
    class Meta:
        # 在模型类中定义一个Meta内部类修改当前表的元信息
        db_table = 'tb_project'	# 指定创建的数据表名称
        verbose_name = '项目表'	# 指定创建的数据表中文描述信息
        verbose_name_plural = '项目表'
```

##### 7、使用**ForeignKey**关联表

- 表与表之间的关联关系
  1. 一对多(ForeignKey)：Projects表与Interfaces表
  2. 一对一(OneToOneField)：人和身份证
  3. 多对多(ManyToManyField)：学生表和课程表

```python
# 接口表
from django.db import models
from projects.models import Projects

class Interfaces(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id主键', help_text='id主键')
    name = models.CharField(max_length=15, unique=True, verbose_name='接口名称', help_text='接口名称')
    tester = models.CharField(max_length=10, verbose_name='测试人员', help_text='测试人员')
    # 1.关联字段一般取名为父类名小写
    # 2.使用ForeignKey在从表中指定外键字段
    # 3.ForeignKey需要两个位置参数
    #	- 第一个位置参数，关联的父表：
    #		第一种写法：子类模型类中导入父类模型类，直接写父类模型类
    #		第二种写法：使用字符串表示，"应用名.父类模型类"。如"projects.Projects"
    #	- 第二个位置参数：级联删除策略
    #		on_delete=models.CASCADE：父表数据删除时，对应子表数据会自动删除
    #		on_delete=models.SET_NULL：父表数据删除时，对应子表数据设置为null
    #		on_delete=models.PROTECT：父表数据删除时，如果存在对应的从表数据，会抛出异常
    #		on_delete=models.SET_DEFAULT, default=''：父表数据删除时，对应子表数据设置为默认值
    # 创建数据表时，会自动创建projects_id的字段，用于存放父表外键只
    projects = models.ForeignKey(Projects, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'tb_interfaces'
        verbose_name = '接口表'
        verbose_name_plural = '接口表'
```

##### 8、抽象模型类

> 当多张表有相同字段，可以把相同字段抽离出来形成抽象模型类。需要使用到公共字段的模型类继承抽象模型类即可。

```python
# 项目下创建公共资源包utils/base_models.py
class BaseModel(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id主键', help_text='id主键')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
    class Meta：
    	# abstract指定当前模型类为抽象模型类
    	abstract = True	
```

