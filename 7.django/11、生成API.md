#### 1.简介

- 生成API文档
- 自动生成测试代码

#### 2.安装

- coreapi(必选)
- Pygments(可选)
- Markdown(可选)

#### 3.使用coreapi

- DRF(>3.10)中，需要添加以下配置

  ```python
  # setting.py
  REST_FRAMEWORK = [
      'DEFAULT_SCHEMA_CLASS': 'rest_framework.schema.coreapi.AutoSchema',
  ]
  ```

  ```python
  #urls.py
  from rest_framework.documentation import include_docs_urls
  
  urlpatterns = [
      path('docs/', include_docs_urls(title='测试平台接口文档'))
  ]
  ```

- 添加注释

  - 单一方法的视图，直接给视图添加注释即可

  - 不同action方法的注释，可以通过 action:注释 添加

    ```python
    """
    list:
    获取项目列表数据
    """
    ```

#### 4.使用drf-yasg

- 安装

  **pip install drf-yasg**

- 添加到INSTALLED_APPS中

  ```python
  INSTALLED_APPS = [
      'drf-yasg',
  ]
  ```

- 在全局路由文件urls.py中添加配置

  ```python
  from drf_yasg.views import get_schema_view
  from drf_yasg import openapi
  
  schema_view = get_schema_view(
      openapi.Info(
      	title = '接口文档平台',
          deafault = 'V1',
          description = '',
          terms_of_service = 'http://api.site',
          contact = openapi.Contact(email=xxx''),
          license = openapi.License(name='BSD License'),
      ),
      public = True,
      # permission_classes = (permission.AllowAny,),
  )
  urlpatterns = [
      re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cahe_timeout=0)), name='schema-json'),
      path('swagger/', schema_view.without_ui('swagger', cahe_timeout=0), name='schema-swagger-ui'),
      path('redoc/', schema_view.without_ui('redoc', cahe_timeout=0), name='schema-redoc'),
  ]
  ```

  