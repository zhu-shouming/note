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
    query_set = Projects.objects.all()
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
  # 1.全局配置指定搜索引擎
  # 默认搜索使用的key值为：search，可在全局配置中修改key值
  REST_FRAMEWORK = {
      'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.SearchFilter'],
      'SEARCH_PARAM': 'name',
  }
  
  # view.py
  # 2.通过search_fields指定要搜索的字段
  # 3.使用父类的filter_queryset()方法获取查询集对象
  class ProjectsView(GenericAPIView):
      queryset = ProjectModel.objects.all()
      serializer_class = ProjectSerializer
      search_fields = ['name']
      
      def get(self, request: Request):
          queryset = self.filter_queryset(self.get_queryset())
          serializer = ProjectSerializer(instance=queryset, many=True)
  ```

  





53
