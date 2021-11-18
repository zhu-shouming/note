### DRF视图

#### 一、APIView

- DRF中的APIView，是Django中View的子类
- 根据前端请求头中传递的Content-Type自动解析参数
- 根据前端请求头中传递Accept，后端返回需要的数据格式
- 提供认证、授权、限流等

```python
from rest_framework.views import APIView
from projects.models import Projects	# 模型类
from projects.serializers import ProjectSerializer	# 序列化器
from rest_framework.response import Response
from rest_framework import status

class ProjectsView(APIView):
    def get(self, request):
        # 继承APIView，request为Request对象
        # 前端传递的www-form-urlencoded、application/json、form/data等，使用request.data属性获取数据
        # 前端传递的查询字符串参数，使用request.query_params属性获取数据
        # 必须返回Response对象，response对象.data属性获取返回前端的数据
        qs = Projects.objects.all()
        serializer = ProjectSerializer(instance=qs, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
```

##### 1、修改DRF默认配置

```python
# settings.py 全局配置文件
# 修改django中的数据解析方式
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        # 'rest_framework.parsers.FormParser',
        # 'rest_framework.parsers.MultiPartParser'
    ],
}
```

##### 2、渲染器

```python
REST_FRAMEWORK = {
    # 指定后端使用的渲染器，会自动根据请求头中的Accept字段，返回前端需要的数据格式
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ],
}
```

##### 3、查询功能

```python
# api:/projects/?name=xiaoming
class ProjectsView(APIView):
    query_set = Projects.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request: Request):
        name = request.query_params.get('name')
        if name:
            query_set = self.query_set.filter(name__exact=request.query_params.get('name'))
        serializer = self.serializer_class(instance=query_set, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
```

#### 二、GenericAPIView

- 是APIView子类，支持APIView的所有功能
- 支持过过滤、排序、分页功能

```python
from rest_framework.generics import GenericAPIView
from projects.models import Projects	# 模型类
from projects.serializers import ProjectSerializer	# 序列化器

class ProjectsView(GenericAPIView):
    '''
    1.继承GenericAPIView，需要指定queryset(查询集)和serializer_class(序列化器类)
    2.请求方法中，使用self.get_queryset()获取查询集，self.get_serializer获取序列化器类
    3.lookup_field类属性用于指定传递主键参数时，接收的url路径参数名，默认为pk
    4.父类有提供self.get_object()获取模型对象
    '''
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request: Request):
        name = request.query_params.get('name')
        if name:
            queryset = self.get_queryset().filter(name__exact=name)
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
```

##### 1、过滤功能

> GenericAPIView支持过滤功能，底层BaseFilterBackend类为过滤基类，通过SearchFilter和OrderingFilter实现搜索和排序过滤

- 搜索过滤

  ```python
  # setting.py
  # 1.全局配置指定搜索引擎，只要视图继承GenericAPIView过滤全局有效；也可以在类视图指定过滤引擎，当前视图支持过滤引擎。
  # 默认搜索使用的key值为：search，可在全局配置中修改key值。
  REST_FRAMEWORK = {
      'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.SearchFilter'],
      'SEARCH_PARAM': 'name',
  }
  
  # view.py
  # 2.通过search_fields指定要搜索的字段
  # 3.必须使用父类的filter_queryset(查询集对象)继续进行过滤
  # 默认使用的是包含（icontains）匹配
  from rest_framework.generics import GenericAPIView
  from rest_framework.filters import SearchFilter
  
  class ProjectsView(GenericAPIView):
      queryset = ProjectModel.objects.all()
      serializer_class = ProjectSerializer
      search_fields = ['=name']	# =表示精确匹配，^表示以什么开头匹配
      filter_backends = [SearchFilter]	# 指定过滤引擎
      
      def get(self, request: Request):
          queryset = self.filter_queryset(self.get_queryset())
          serializer = self.get_serializer(instance=queryset, many=True)
          return Response(data=serializer.data, status=status.HTTP_200_OK)
  ```

- 排序过滤

  ```python
  # 1.指定过滤引擎OrderingFilter，同SearchFilter配置一样
  # 2.指定要排序的字段，如ordering_fields = ['id', 'name', 'create_time']
  # 3.必须使用父类的filter_queryset(查询集对象)继续进行过滤
  # 前端可以指定多个排序字段，每个排序字段用逗号隔开。如：?ordering=-id,name
  from rest_framework.generics import GenericAPIView
  from rest_framework.filters import OrderingFilter
  
  class ProjectsView(GenericAPIView):
      queryset = ProjectModel.objects.all()
      serializer_class = ProjectSerializer
      ordering_fields = ['id', 'name', 'create_time']
      filter_backends = [OrderingFilter]
      
      def get(self, request: Request):
          queryset = self.filter_queryset(self.get_queryset())
          serializer = self.get_serializer(instance=queryset, many=True)
          return Response(data=serializer.data, status=status.HTTP_200_OK)
  ```

##### 2、分页功能

```python
# 1.使用DEFAULT_PAGINATION_CLASS指定分页引擎，或视图中pagination_clas指定引擎
# 2.指定PAGE_SIZE分页的数据条数
# 3.必须调用paginate_queryset(查询集对象)方法
# 4.paginate_queryset(查询集对象)返回的对象传给序列化器
# 5.最终必须返回get_paginated_response(序列化后的数据)方法
# 也可以对PageNumberPagination进行重写，定义新功能
from rest_framework.generics import GenericAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

class ProjectsView(GenericAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ['=name']
    ordering_fields = ['id', 'name', 'create_time']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination

    def get(self, request: Request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
```

##### 3、Mixin扩展类

```python
from projects.models import ProjectModel	# 模型类
from projects.serializers import ProjectSerializer	# 序列化器
from rest_framework.generics import GenericAPIView	# 视图
from rest_framework.filters import SearchFilter, OrderingFilter	# 过滤引擎
from rest_framework.pagination import PageNumberPagination	# 分页引擎
from rest_framework import mixins	# 扩展类

class ProjectsView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ['=name']
    ordering_fields = ['id', 'name', 'create_time']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination

    def get(self, request: Request):
        return self.list(request)

    def post(self, request):
        return self.create(request)

class ProjectsViewDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.update(request)

    def delete(self, request, pk):
        return self.destroy(request)
```

##### 4、GenericAPIView属性和方法

- 属性
  - queryset：定义类视图的类属性，指定当前类视图用到的查询集对象
  - serializer_class：指定当前类视图要使用的序列化器对象
- 方法
  - get_queryset()：获取的就是queryset查询集对象
  - get_object()：获取一个模型类对象，默认使用pk为路径名称
  - get_serializer()：获取的就是serializer_class序列化器类
  - get_serializer_class()：获取序列化器名称
  - filter_queryset()：实现过滤功能调用
  - paginate_queryset()：实现分页功能调用
  - get_paginated_response()：获取分页返回结果

##### 5、Concrete Generic Views

- RetrieveAPIView
  - 提供get方法
  - 继承：RetrieveModelMixin、GenericAPIView
- UpdateAPIView
  - 提供put和patch()方法
  - 继承：UpdateModelMixin、GenericAPIView
- DestroyAPIView
  - 提供delete
  - 继承：DestroyModelMixin、GenericAPIView
- ListAPIView
  - 提供get方法
  - 继承：ListModelMixin、GenericAPIView
- CreateAPIView
  - 提供post方法
  - 继承：CreateModeMixin、GenericAPIView
- ListCreateAPIView
  - 提供post、get方法
  - 继承：ListModelMixin、CreateModelMixin、GenericAPIView
- RetrieveUpdateAPIView
  - 提供get、put、patch方法
  - 继承：RetrieveModelMixin、UpdateModelMixin、GenericAPIView

```python
# model.py
from django.db import models

class ProjectModel(models.Model):
    name = models.CharField(verbose_name='项目名称', help_text='项目名称', max_length=20, unique=True)
    des = models.TextField(verbose_name='项目描述', help_text='项目描述', null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', help_text='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', help_text='更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tb_project'
        verbose_name = '项目表'
        verbose_name_plural = '项目表'

# serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from projects.models import ProjectModel

class ProjectSerializer(serializers.ModelSerializer):
    interface = serializers.StringRelatedField(read_only=True, many=True)	# 自定义关联从表信息

    class Meta:
        model = ProjectModel
        fields = '__all__'
        extra_kwargs = {
            'name': {
                'label': '项目名称',
                'help_text': '项目名称',
                'max_length': 10,
                'min_length': 3,
                'error_messages': {'max_length': '字符长度必须小于10位', 'min_length': '字符长度必须大于3位'},
                'validators': [UniqueValidator(ProjectModel.objects.all(), message='项目名称已重复')]
            },
            'des': {
                'allow_blank': True,
                'allow_null': True
            }
        }
```

```python
# view.py
from projects.models import ProjectModel
from rest_framework import generics
from projects.serializers import ProjectSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

class ProjectsView(generics.ListCreateAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ['=name']
    ordering_fields = ['id', 'name', 'create_time']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination

class ProjectsViewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
```

#### 三、viewsets

- 使请求方法和动作进行映射

| 请求方法 | 动作           | 描述                 |
| -------- | -------------- | -------------------- |
| GET      | retrieve       | 获取详情数据（单条） |
| GET      | list           | 获取列表数据（多条） |
| POST     | create         | 创建数据             |
| PUT      | update         | 更新数据             |
| PATCH    | partial_update | 部分更新             |
| DELETE   | destroy        | 删除数据             |

##### ViewSet类

- 继承ViewSetMixin和views.APIView
  - ViewSetMixin支持action动作
- 未提供get_object()、get_serializer()、queryset、serializer_class等

##### GenericViewSet类

- 继承ViewSetMixin和GenericAPIView
  - get_object()、get_serializer()、queryset、serializer_class等
- 在定义路由时，需要将请求方法与action动作进行绑定

##### ModelViewSet类

- 继承CreateModelMixin、RetrieveModelMixin、UpdateModelMixin、DestroyModelMixin、ListModelMixin、GenericViewSet

##### ReadOnlyModelViewSet类

- 继承RetrieveModelMixin、ListModelMixin、GenericViewSet

```python
# urls.py
from django.urls import path
from projects import views

# 继承了ViewSet类视图，在路由中支持请求方法和action一一对应的功能
# 在as_view()方法中传入字典
urlpatterns = [
    path('', views.ProjectsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('<int:pk>/', views.ProjectsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]
```

```python
# view.py
from rest_framework import viewsets
from rest_framework import mixins

# 继承mixins扩展类使用action方法
class ProjectsViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ['=name']
    ordering_fields = ['id', 'name', 'create_time']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination
```

- viewsets封装了GenericViewSet、ReadOnlyModelViewSet、ModelViewSet

  ```python
  # 上面类继承的代码可以优化
  class ProjectsViewSet(viewsets.ModelViewSet):
      pass
  ```

#### 四、类视图实现原则

- 类视图尽量简化
- 根据需求选择相应的父类视图
- 如果DRF中的类视图有提供相应的逻辑，那么直接使用父类的方法
- 如果DRF中的类视图能满足绝大多数需求，那么直接重写父类的实现
- 如果DRF中的类视图

