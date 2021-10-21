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
  INSTALLED_APPS = [
      'rest_framework',]
  ```

##### 4、序列化器

- 数据校验
- 数据转化
  - 序列化：将对象转化成数据
  - 反序列化：将数据转化成对象

##### 5、序列化、反序列化

- 定义序列化器

  ```python
  # 子应用中新建serializers.py定义序列化器
  from rest_framework import serializers
  '''
  1、序列化器需要是继承serializers.Serializer或期子类
  2、通过不同Field类定义不同的字段，且字段名需和对应使用的模型类一致'''
  class ProjectSerializer(serializers.Serializer):
      name = serializers.CharField(label='项目名称', help_text='项目名称', max_length=10, min_length=3, error_messages={'min_length': '项目名称长度不能少于3位', 'max_length': "项目名称长度不能大于10位"})
      leader = serializers.CharField(label='项目负责人', help_text='项目负责人')
      is_excute = serializers.BooleanField(label='是否启动项目', help_text='是否启动项目', read_only=True)
      # allow_null=True指定字段可以传入null，allow_blank指定字段可以传入空字符串
      desc = serializers.CharField(label='项目描述', help_text='项目描述', allow_null=True, allow_blank=True)
      # 格式化使用format参数
      create_time = serializers.DateTimeField(label='创建时间', help_text='创建时间', format='%Y-%m-%d %H:%M:%S')
      
  # 使用序列化器，view.py
  from . import serializers
  
  class ProjectViews(View):	# 类视图
      def get(self, request):	# 获取项目的所有数据的接口
          data = Project.objects.all()
          # 将获取的查询集或模型类对象传递给序列化器instance参数，数据为查询集时需指定参数many=True
          serialize = serializers.ProjectSerializer(instance=data, many=True)
          # serialize.data获取对象的数据，一般为字典或嵌套字典
          return JsonResponse(data=serialize.data, safe=False, json_dumps_params={"ensure_ascii": False})
      
      def post(self, request):	#创建一个项目的接口
          json_str = request.body.decode('utf-8')
          json_dict = json.loads(json_str)
          # 对数据校验时，在定义序列化器需要指定一些参数，如：max_length、min_length。将前端传来的数据传来序列化器data参数。
          serializer = serializers.ProjectSerializer(data=json_dict)
          # 通过序列化器的is_valid()方法校验参数，校验通过返回True。指定参数raise_exception=True校验不通过会抛出异常
          if not serializer.is_valid(raise_exception=True):
              # 校验不通过的错误信息存放在序列化器的errors属性中
              return JsonResponse(data=serializer.errors, json_dumps_params={"ensure_ascii": False})
          # 校验通过的数据：serializer.validated_data
          obj = Project(**serializer.validated_data)
        obj.save()
          serializer = serializers.ProjectSerializer(instance=obj)
        return JsonResponse(data=serializer.data, json_dumps_params={"ensure_ascii": False})
  ```
  
  - 选项参数
  
    | 参数名称            | 说明               |
    | ------------------- | ------------------ |
    | **max_length**      | 最大长度           |
    | **min_length**      | 最小长度           |
    | **allow_blank**     | 是否允许为空字符串 |
  | **trim_whitespace** | 是否截断空白字符   |
    | **max_value**       | 最大值             |
  | **min_value**       | 最小值             |
    
  - 通过参数
  
    | 参数名称           | 说明                                                         |
    | ------------------ | ------------------------------------------------------------ |
    | **read_only**      | 表明该字段仅用于序列化输出，默认为False。read_only=True表示该字段不用传参 |
    | **write_only**     | 表明该字段仅用于序列化输入，默认为False。write_only=True表示该字段序列化输出时不显示 |
    | **required**       | 表明该字段在反序列化时必须输入，默认为True                   |
    | **default**        | 反序列化时使用的默认值                                       |
    | **allow_null**     | 表明该字段是否允许传入None，默认为False                      |
    | **vaildators**     | 该字段使用的验证器                                           |
    | **error_messages** | 包含错误编号与错误信息的字典                                 |
    | **label**          | 用于HTML展示API页面时，显示的字段名称                        |
    | **help_text**      | 用于HTML展示API页面时，显示的字段帮助提示信息                |

49