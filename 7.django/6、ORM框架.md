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
    
    # 在模型类中定义一个Meta内部类修改当前表的元信息
    class Meta:
        db_table = 'tb_project'	# 指定创建的数据表名称
        verbose_name = '项目表'	# 指定创建的数据表中文描述信息
        verbose_name_plural = '项目表'
```

##### 7、表与表关联：模型类使用**ForeignKey**关联

>表与表之间的关联关系：一对多（ForeignKey）、一对一（OneToOneField）、多对多（ManyToManyField）
>
>模型类中添加外键，一般在‘多’的那侧添加外键，一对一时候任何一方均可添加外键，外键字段名推荐使用关联模型类小写命名。

```python
# 接口表
class Interfaces(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id主键', help_text='id主键')
    name = models.CharField(max_length=15, verbose_name='接口名称', help_text='接口名称', unique=True)
    tester = models.CharField(max_length=10, verbose_name='测试人员', help_text='测试人员')
    '''
    ForeignKey两个位置参数：
    	1、关联的表(to)：a.可采用导入关联类，直接写关联的类；b.字符串指定‘子应用名_父类模型类’
    	2、指定关联表删除时的处理方式(on_delete)：级联删除策略
    		CASCADE：当父表数据删除时，对应从表数据会自动删除
    		SET_NULL：当父表数据删除之后，对应从表的外键字段会被自动设置为NULL
    		PROTECT：当父表数据删除时，如果存在对应的从表数据，会抛出异常
    		SET_DEAFAULT：当父表数据删除之后，对应的从表数据的外键会被自动设置为default参数指定的值
    '''
    # 创建数据表时，会自动生成projects_id作为字段名存放外键值
    projects = models.ForeignKey('pools.Projects', on_delete=models.CASCADE)
```

- 抽象模型类：多张表字段相同时，可抽取出来形成抽象模型类

  ```python
  # 项目下创建公共资源包utils/base_models.py
  class BaseModel(models.Model):
      id = models.AutoField(primary_key=True, verbose_name='id主键', help_text='id主键')
      create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
      update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间', help_text='更新时间')
      class Meta：
      	# abstract指定当前模型类为抽象模型类
          # 因为某些模型类，仅仅是将多个模型类中的公共的字段抽离出来，而不需要生成表,需要用到该模型类的字段继承模型类即可
      	abstract = True	
  ```

  

# 46