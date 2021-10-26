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
  
