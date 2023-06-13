### DRF路由

- 解决痛点：当路由处理许多的请求方法和动作的映射

```python
# urls.py
from django.urls import path, include
from projects import views
from rest_framework import routers

# 1.创建路由对象，DefaultRouter()会默认为项目添加一个根路由（获取当前数据的入口）
router = routers.SimpleRouter()
# 2.注册路由
# register()参数
#	第一个参数为路由前缀
#	第二个参数为视图集
#	第三个参数为路由别名
router.register(r'projects', views.ProjectsViewSet)

urlpatterns = [
    # path('', include(router.urls)),
]
# 3.合并路由条目，也可以在urlpatterns里面使用
urlpatterns += router.urls
```

备：

​	使用视图集中的路由机制，只会特定的action自动生成路由。如：create、get、retrieve、post...

​	自定义的action，不会自动生成路由条目，需要手动添加路由映射

```python
# view.py	自动生成自定义action路由
# 接口：http://127.0.0.1:8000/projects/names/
# 返回：所有项目的id和名称
from rest_framework.decorators import action

class ProjectsViewSet(viewsets.ModelViewSet):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ['=name']
    ordering_fields = ['id', 'name', 'create_time']
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination
	
    # 1.使用视图集中的路由机制自动生成路由，需要使用到action装饰器
    #	methods参数默认为get方法，可以在里诶表中指定多个请求
    #	detail参数指定是否接收模型主键值(路径参数pk)
    #	url_path参数指定生成的路由条路名称，默认为自定义action方法名称
    #	url_name指定生成的路由名称后缀。默认为自定义action方法名称
    @action(methods=['get'], detail=False)
    def names(self, request):
        queryset = self.get_queryset()
        names_lst = [{'id': obj.id, 'name': obj.name} for obj in queryset]
        return Response(names_lst, status=status.HTTP_200_OK)
```

### 使用不同的序列化器

- 重写get_serializer_class方法：使用self.action属性获取action，选择使用不同的序列化器

  ```python
  # serializers.py
  class ProjectsNamesSerializer(serializers.ModelSerializer):
      class Meta:
          model = ProjectModel
          fields = ['id', 'name']
  ```

  ```python
  # view.py
  from projects.models import ProjectModel
  from projects import serializers
  
  class ProjectsViewSet(viewsets.ModelViewSet):
      queryset = ProjectModel.objects.all()
      serializer_class = serializers.ProjectSerializer
      search_fields = ['=name']
      ordering_fields = ['id', 'name', 'create_time']
      filter_backends = [SearchFilter, OrderingFilter]
      pagination_class = PageNumberPagination
  
      @action(methods=['get'], detail=False)
      def names(self, request):
          return self.list(request)	# 调用父类的list
  
      def get_serializer_class(self):
          return serializers.ProjectsNamesSerializer if self.action == 'names' else super().get_serializer_class()
  ```

- 不需要类提供的过滤、分页功能，重写filter_queryset()、paginate_queryset()方法即可

  ```python
  # view.py
  def filter_queryset(self, queryset):
          return self.queryset if self.action == 'names' else super().filter_queryset(queryset)
  
      def paginate_queryset(self, queryset):
          return None if self.action == 'names' else super().filter_queryset(queryset)
  ```

