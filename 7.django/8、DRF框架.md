### Django REST framework框架

#### 一、REST API

- 是REpresentational State Transfer 的缩写

- 是一种开发理念，是设计风格而不是标准

- 每一个URL代表一种资源

- 客户端和服务端之间，传递资源的某种表现形式
  - 通过请求头中Content-Type来指明传给服务端的参数类型
  
    ```python
    "text/plain","application/json
    ```
  
  - 通过请求头中Accept来指明希望接收服务端的数据类型
  
    ```python
    Accept: application/json
    ```
  
- 客户端通过HTTP动词，指明对服务器端资源进行的操作

  | HTTP METHOD | CURD                  |
  | ----------- | --------------------- |
  | POST        | Create                |
  | GET         | Read                  |
  | PUT         | Update/Replace        |
  | PATCH       | Partial Update/Modify |
  | DELETE      | Delete                |

#### 二、REST常用的设计原则

- URL命名

  - 尽量使用名词复数形式
  - 往往和数据库的表名对应

- 过滤条件，使用分页、查询、排序一律使用查询字符串参数

  > ?limit=10					：指定返回记录的数量	
  >
  > ?offset=10				  ：指定返回记录的开始位置
  >
  > ?page=2&size=10      ：指定第几页和每页的数据条数
  >
  > ?sort=name				：指定返回结果按那个属性排序

- 版本

  - 在URL中呈现版本号

    > http://api.xiaoming/app/0.1/

  - 在请求头中呈现

    > Accept: application/vnd.example+json;version=1.1

- HTTP请求动词

  ```
  # 常见的HTTP动词
  GET（SELECT）	：从服务器上获取资源（一项或多项）
  POST（CREATE）：在服务器上新建一个资源
  PUT(UPDATE)   ：在服务器上更新资源
  DELETE(DELETE)：从服务器上删除资源
  
  # 不常见HTTP动词
  PATCH	：在服务器上更新部分资源
  HEAD	：获取资源的元数据
  OPTIONS	：获取关于资源的哪些属性是客户端可以改变的信息
  ```

- 状态码

  ```
  200	OK	- [GET]：服务器成功返回用户请求的数据
  201 CREATED	- [POST/PUT/PATCH]：用户新建或修改数据成功
  204	NO CONTENT	- [DELETE]：用户删除数据成功
  400	INVALID REQUEST	- [POST/PUT/PATCH]：用于请求参数有误
  401 Unauthorized - [*]：用户没有权限
  403 Forbidden - [*]：用户得到授权，但是访问是被禁止的
  404 NOT FOUND - [*]：用户请求路径不存在
  500 INTERNAL SERVER ERROR - [*]：服务器发生错误
  ```

- 错误处理
  
  - 当请求有误时，服务器需要将错误信息以json格式数据的形式返回

#### 三、Django REST framework

##### 1、简介

- 在Django框架基础之上进行的二次开发
- 用于构建Restful API

##### 2、特性

- 提供了强大的Serialize序列化器，可以高效地进行序列化与反序列化操作
- 提供了极为丰富的类视图，Mixin扩展类、ViewSet视图集
- 提供了直观的web API界面
- 多种身份认证和权限认证
- 强大的排序、过滤、分页、搜索、限流等功能
- 可扩展性、插件丰富

##### 3、安装&配置

- 安装

  ```python
  pip install djangorestframework
  pip install markdown
  ```

- 配置

  ```python
  # setting.py
  INSTALLED_APPS = [
      'rest_framework',]
  ```

##### 4、序列化器的作用

> 1.数据转化
>
> - 序列化：将对象转化成数据
> - 反序列化：将数据转化成对象
>
> 2.数据校验
>
> 3.操作数据

##### 5、序列化器的定义及使用

- 定义序列化器：在需要使用的子应用目录下创建序列化器，序列化器常命名为serializers.py

  ```python
  # projects/serializers.py
  from rest_framework import serializers	# 导入DRF的序列化器组件
  
  # 定义个序列化器：
  #	1.需要继承Serializer或其子类
  #	2.定义字段进行数据校验和序列化操作，字段名和其类型与模型类的字段保持一致
  创建一个类继承Serializer或其子类来定义一个序列化器
  class ProjectSerializer(serializers.Serializer):
      name = serializers.CharField()
      leader = serializers.CharField()
  ```

- 序列化

  ```python
  # projects/views.py
  from projects.models import Projects	# 模型类
  from projects.serializers import ProjectSerializer	# 导入创建的序列化器类
  
  class ProjectsView(View):
      def get(self, request):
          qs = Projects.objects.all()
          # 使用序列化器进行序列化操作
          #	1.定义一个序列化器，把模型类对象或查询集给到instance参数，且当数据为模型类对象时，参数many=False
          #	2.使用serializer.data获取序列化器中的数据（常为字典或嵌套字典的列表）
          serializer = ProjectSerializer(instance=qs, many=True)
          return JsonResponse(serializer.data, safe=False, json_dumps_params={"ensure_ascii": False})
  ```

##### 6、数据校验

- 选项参数

  | 参数名称            | 作用                      |
  | ------------------- | ------------------------- |
  | **max_length**      | CharField指定最大长度     |
  | **min_length**      | CharField指定最小长度     |
  | **allow_blank**     | CharField是否允许为空     |
  | **trim_whitespace** | CharField是否截断空白字符 |
  | **max_value**       | 最大值                    |
  | **min_value**       | 最小值                    |

- 通用参数

  | 参数名称            | 说明                                        |
  | ------------------- | ------------------------------------------- |
  | **read_only**       | 表明该字段仅用于序列化输出，默认为False     |
  | **write_only**      | 表明该字段仅用于反序列化输入，默认为False   |
  | **required**        | 表明该字段在反序列化时必须输入，默认True    |
  | **default**         | 反序列化时使用的默认值                      |
  | **allow_null**      | 表明该字段是否允许传入null，默认为False     |
  | **allow_blank**     | 表明该字段是否允许传入空字符串，默认为False |
  | **validators**      | 该字段使用的验证器                          |
  | **errors_messages** | 包含错误编码与错误信息的字典                |
  | **lable**           | 用于HTML展示API页面时，显示的字段名称       |
  | **help_text**       | 后台站点显示字段的名称                      |

- 序列化器校验参数

  ```python
  # serializers.py
  from rest_framework import serializers
  
  # 序列化器进行数据校验：
  #	1.序列化器类中添加参数进行校验
  class ProjectSerializer(serializers.Serializer):
      id = serializers.IntegerField()
      # 参数限定反序列化输入、序列化输出：
      #	1.min_length、max_length：限定字符的长度
      #	2.write_only=True：该字段必须输入，但无需序列化输出
      #	3.read_only=True:该字段无需输入，但必须序列化输出
      #	4.error_messages定制错误返回信息，规则的名称作为key，提示的错误信息为value
      #	5.allow_blank=True:允许前端传null值
      #	6.allow_null=True:允许前端传空字符串
      #	7.required=False：该字段反序列化输入时，可以不传递
      #	8.format='%Y-%m-%d %H:%M:%S'：格式化日期
      name = serializers.CharField(label='项目名称', help_text='项目名称', max_length=10, min_length=3, write_only=True, error_messages={'min_length':'项目名称不能少于3位', 'max_length':'项目名称不能大于10位'})
      leader = serializers.CharField(label='项目负责人', help_text='项目负责人')
      is_execute = serializers.BooleanField(label='是否启动', help_text='是否启动', read_only=True)
      desc = serializers.CharField(label='项目描述', help_text='项目描述', allow_blank=True, allow_null=True, required=False)
      create_time = serializers.DateTimeField(label='创建时间', help_text='创建时间', required=False， format='%Y-%m-%d %H:%M:%S')
  ```
	
  ```python
  # views.py
  class ProjectsView(View):
      def post(self, request):	# 创建一条数据
          json_str = request.body.decode('utf-8')
          python_data = json.loads(json_str)
  	# 序列化器对数据进行校验：
          # 	1.定义个序列化器，给data传参
          #	2.data必须为python中的基本类型（字典或嵌套字典的列表）
          #	3.必须调用is_valid()才会进行数据校验，指定raise_exception=True表示校验失败自动抛出异常
          #	4.serializer.errors获取校验失败后的信息，常为字典类型
          #	5.serializer.validated_data获取校验通过的数据
          serializer = ProjectSerializer(data=python_data)
          if not serializer.is_valid():
              err = serializer.errors
              return JsonResponse(err, json_dumps_params={"ensure_ascii": False})
          else:
              obj = Projects(**serializer.validated_data)
              obj.save()
              serializer = ProjectSerializer(instance=obj)
             return JsonResponse(serializer.data, safe=False, json_dumps_params={"ensure_ascii": False})
  ```

##### 7、关联字段的序列化

- 父表获取从表字段

```python
# serializers.py 父类序列化器
# 需求：序列化输出输出从表的信息
from rest_framework import serializers
from interfaces.models import Interfaces

class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='项目id', help_text='项目id')
    name = serializers.CharField(label='项目名称', help_text='项目名称', max_length=10, min_length=3)
    leader = serializers.CharField(label='项目负责人', help_text='项目负责人', max_length=20)
    ie_execute = serializers.BooleanField(label='是否启动', help_text='是否启动', read_only=True)
    des = serializers.CharField(label='项目描述', help_text='项目描述', allow_null=True, allow_blank=True)
    create_time = serializers.DateTimeField(label='创建时间', help_text='创建时间', required=True)
    # 父表序列化器获取从表的数据，默认使用变量名：从表模型类小写_set(interfaces_set)。也可以自定义变量名，在从表的外键字段(ForeignKey)指定related_name参数
    # 可以指定关联字段的序列化
    # 	- PrimaryKeyRelatedField指定的是从表的id值
    #		- 如果序列化输出的数据多个，参数必须指定many=True
    #		- 如果参数指定read_only=True，那么只输出从表的id
    #		- 如果参数未指定read_only=True或required=False，那么必须指定queryset参数（指定查询集对象）
    # 		例如：interfaces = serializers.PrimaryKeyRelatedField(label='所属接口id', help_text='所属接口id', many=True, queryset=Interfaces.objects.all())
    #	- StringRelatedField序列化输出时，调用关联模型类__str__方法。默认指定read_only=True
    # 		例如：interfaces = serializers.StringRelatedField(label='所属接口名称', help_text='所属接口名称', many=True)
    #	- SlugRelatedField指定序列化时关联模型类的字段
    #		- 如果要指定反序列化输入，slug_field必须指定唯一约束字段
    interfaces = serializers.SlugRelatedField(label='所属接口名称', help_text='所属接口名称', many=True, read_only=True, slug_field='tester')
```

```python
# models.py	子类模型类
class Interfaces(BaseModel):
    name = models.CharField(unique=True, max_length=15, verbose_name='接口名称', help_text='接口名称')
    tester = models.CharField(max_length=10, verbose_name='测试人员', help_text='测试人员')
    projects = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='interfaces')
```

- 从表获取父表数据

```python
# 从表序列化器
class OneProjectsSerializer(serializers.Serializer):
    """"定义一个序列化器类，指定要返回的父表字段"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    leader = serializers.CharField()
    is_execute = serializers.BooleanField()
    desc = serializers.CharField()
    create_time = serializers.DateTimeField()
    update_time = serializers.DateTimeField()
    
class InterfaceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='id主键', help_text='id主键', required=False)
    name = serializers.CharField(label='接口名称', help_text='接口名称', max_length=15,
                                 error_messages={'max_length': 'name不能超过15字'})
    tester = serializers.CharField(label='测试人员', help_text='测试人员', max_length=10,
                                   error_messages={'max_length': 'tester不能超过15字'})
    create_time = serializers.DateTimeField(label='创建时间', help_text='创建时间', required=False, read_only=True)
    update_time = serializers.DateTimeField(label='更新时间', help_text='更新时间', required=False, read_only=True)
    projects = OneProjectsSerializer(label='获取父表projects所有信息', help_text='获取父表projects所有信息', read_only=True)
```

##### 8、自定义校验规则

- 字段的校验顺序

  校验字段类型->通过的约束参数(max_length、min_length)->依次校验字段参数validators中的规则->序列化器类中调用单字段的校验方法(validate_字段名)->序列化器类中联合字段校验方法(validate)

```python
# serializers.py	需求：创建数据进行校验
from rest_framework import serializers
from rest_framework.validators import UniqueValidator	# DRF中的校验器
from .models import Projects

def is_contain_keyword(value):	# 自定义校验函数
    # value：前端传递的数据
    # 如果校验失败，必须返回ValidationError异常对象
    # ValidationError中可以指定报错的信息
    if '项目' not in value:
        raise serializers.ValidationError('项目名称中必须包含项目')
        
class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='项目id', help_text='项目id', read_only=True)
    # 序列化器字段使用validators参数指定自定义校验器，validators必须指定序列类型
    # 	- UniqueValidator校验器进行唯一约束的校验，必须指定queryset参数，message参数指定报错的信息
    # 自定义校验器对字段数据进行校验，在validators序列中添加自定义校验器关键字即可
    name = serializers.CharField(label='项目名称', help_text='项目名称', max_length=10, min_length=3,validators=[UniqueValidator(queryset=Projects.objects.all(), message='项目名称不能重复'), is_contain_keyword])
    leader = serializers.CharField(label='项目负责人', help_text='项目负责人', max_length=20)
    ie_execute = serializers.BooleanField(label='是否启动', help_text='是否启动', read_only=True)
    des = serializers.CharField(label='项目描述', help_text='项目描述', allow_null=True, allow_blank=True, read_only=True)
    create_time = serializers.DateTimeField(label='创建时间', help_text='创建时间',read_only=True)
    
    # 可以在序列化器类中定义对字段进行校验的方法
    #	- 校验方法的名称：validate_字段名
    #	- 接受的参数为前端传递的值
    def validate_name(self, value):
        value: str
        if not value.endswith('项目'):
            raise serializers.ValidationError('项目名称必须以项目结尾')
        return value
    
    # validate方法对多个字段进行校验，attr为前端校验后的数据
    # validate校验通过必须有返回值
    def validate(self, attr):
        name = attr.get('name')
        leader = attr.get('leader')
        if name == leader:
            raise serializers.ValidationError('项目名和负责人名称不能一样')
        return attr
    
    # 序列化器进行校验时，首先会调用to_internal_value进行校验
    def to_internal_value(self, data):
    	some_data = super().to_internal_value(data)
        return some_data
    
    def to_representation(self, instance):
        pass
```

##### 9、DRF数据保存、更新

```python
# serializers.py 序列化器
from rest_framework import serializers
from projects.models import Projects	# 模型类

class ProjectSerializer(serializers.Serializer):
    """省去模型类定义字段"""
    token = serializers.CharField(read_only=True)	# 添加序列化输出的数据
    
    def create(self, validated_data):
        # validated_data：校验通过后的数据
        # 必须将创建的模型类对象返回
        # 也可以添加自定义返回数据（token），前提序列化器中必须有定义
        obj = Projects.objects.create(**validated_data)
        obj.token = 'xxx-xxx-xxx-xxx-xxx'
        return obj
    
    def update(self, instance, validated_data):
        # validated_data：校验通过后的数据
        # instance：待更新的模型类对象
        # 必须将创建的模型类对象返回
        instance.name = instance.get('name') or instance.name
        instance.leader = instance.get('leader') or instance.leader
        instance.is_execute = instance.get('is_execute') or instance.is_execute
        instance.desc = instance.get('desc') or instance.desc
        instance.save()
        return instance
```

```python
# View.py
# 解决痛点：反序列化需要把数据传给序列化器data参数，序列化时传给instance参数
# 序列化器对象调用save()方法，会进行数据创建和更新操作
#	- 当创建数据时，只给序列化器data传参，使用序列化器的save()方法会自动调用序列化器的create()方法
#	- 当更新数据时，给序列化器instance和data同时传参，使用序列化器的save()方法会自动调用序列化器的update()方法
#	- 序列化器save()方法可以传关键字参数，可在create或update方法validated_data中获取

class ProjectsView(View):
    def post(self, request):
        err_msg = {
            'status': False,
            'msg': '参数有误',
            'num': 0
        }
        try:
            json_data = request.body.decode('utf-8')
            python_data = json.loads(json_data)
        except Exception:
            return JsonResponse(err_msg, json_dumps_params={'ensure_ascii': False}, status=400)
        serializer = ProjectSerializer(data=python_data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, json_dumps_params={"ensure_ascii": False})
        serializer.save()
        return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False})
    
class ProjectViewDetail(View):
    def put(self, request, pk):
        error_msg = {
            'status': False,
            'msg': '参数有误',
            'num': 0
        }
        try:
            json_data = request.body.decode('utf-8')
            python_data = json.loads(json_data)
            obj = Projects.objects.get(id__exact=pk)
        except Exception:
            return JsonResponse(error_msg, json_dumps_params={'ensure_ascii': False}, status=400)
        serializer = ProjectSerializer(instance=obj, data=python_data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, json_dumps_params={"ensure_ascii": False})
        serializer.save()
        return JsonResponse(serializer.data, json_dumps_params={"ensure_ascii": False}, status=200)
```

