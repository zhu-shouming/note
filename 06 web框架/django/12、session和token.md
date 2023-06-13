### 用户模块

#### 1.修改django用户模型

- 创建并注册子应用

- 子应用模型继承AbstractUser，重新定义属性
- 全局配置文件指定AUTH_USER_MODEL = 'user.models.User'

#### 2.session认证

##### 1.修改DRF的认证和授权

```python
# 直接在项目全局指定文件中重写其认证和授权即可,DRF默认使用的认证方式是session认证
REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # DRF自带的权限
        #	AllowAny(默认权限)、IsAuthenticated、IsAdminUser、IsAuthenticatedOrReadonly
        #	
        # permissions类下定义了多种认证方式，IsAuthenticated表示登录授权
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

- 也可以在具体类中指定

  ```python
  # 权限类一般在类视图中指定，认证类一般在全局配置文件中指定
  class ProjectViewset(viewsets.ModelViewSet):
      authentication_classes = [authentication.SessionAuthentication, authentication.BasicAuthentication]
      permission_classes = [permissions.IsAuthenticated]
  ```

##### 2.创建可登录的api界面

- 全局路由里面指定django或restframework下的路由文件

```python
# 只要视图是继承APIView的接口，都可以登录后访问
urlpatterns = [
    path('api/', include('rest_framework.urls')),
]
```

- 创建超级管理员

```python
python manage.py createsuperuser
```

#### 3.token认证

##### 1.token的组成

header、playload、signature

- header
  - 声明类型
  - 声明加密算法，默认为H256
  - base64加密

- playload
  - 存放过期时间、签发用户等
  - 可以添加用户的非敏感信息
  - base64加密
- signature
  - 由三部分组成
  - 使用base64加密后的header+.+使用base64加密后的playload+使用H256算法加密，同时secret加盐处理


##### 2.django中使用token认证

可以使用django中自带模块pyjwt，也可以使用第三方模块djangorestframework-jwt模块

1. 安装djangorestframework-jwt

   ```python
   pip install djangorestframework-jwt
   ```

2. 全局配置文件修改认证机制

   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
           ],
   }  
   ```

3. 路由指定DRF下ObtainJSONWebToken视图

   ```python
   # 全局路由配置指向用户子应用
   path('user/', include('user.urls'))
   
   # 用户子应用执行DRF下产生token的类视图
   from rest_framework_jwt.views import obtain_jwt_token
   urlpatterns = [
       path('login/', obtain_jwt_token)
   ]
   ```

#### 3.修改jwt模块配置

1. 修改token前缀

   ```python
   # jwt模块生成token，在使用的时候默认有JWT前缀，可在django全局配置文件中修改前缀名
   JWT_AUTH = {
       'JWT_AUTH_HEADER_PREFIX': 'Bears',
   }
   
   ```

2. 修改jwt模块返回结果

   ```python
   # jwt模块生成token，默认只返回token。当需要修改返回的信息，需要重写jwt_response_payload_handler()方法
   # 第一步：重写jwt_response_payload_handler()方法
   def jwt_response_payload_handler(token, user=None, request=None):
       return {
           'token': token,
           'user_id': user.id,
           'username': user.username
       }
   # 第二步；全局配置指定重写的类
   JWT_AUTH = {
       'JWT_RESPONSE_PAYLOAD_HANDLER':
           'utils.handle_jwt_response.jwt_response_payload_handler',
   }
   # 备注：也可以直接把源码复制放在项目根目录下，直接改源码
   ```

### 用户注册接口实现

- 需求：

  - 前端提供用户名、密码、确认密码、邮箱
  - 用户名长度6-20字符且唯一，密码和确认密码一致，邮箱格式正确且唯一
  - 返回用户ID、用户名和生成token值

  ```python
  # 序列化器
  from rest_framework import serializers, validators
  from django.contrib.auth.models import User	# django用户表
  from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
  
  class UserSerializer(serializers.ModelSerializer):
      # django用户表添加额外字段
      password_confirm = serializers.CharField(label='确认密码', help_text='确认密码', max_length=20, min_length=6, write_only=True, error_messages={'max_length': '用户名不能大于20位', 'min_length': '用户名不能小于6位'})
      token = serializers.CharField(label='生成token', read_only=True)
  
      class Meta:
          model = User
          fields = ('id', 'username', 'password', 'password_confirm', 'email', 'token')
          extra_kwargs = {
              'username': {
                  'label': '用户名',
                  'help_text': '用户名',
                  'max_length': 20,
                  'min_length': 6,
                  'error_messages': {
                      'max_length': '用户名不能大于20位',
                      'min_length': '用户名不能小于6位'
                  }
              },
              'password': {
                  'label': '密码',
                  'help_text': '密码',
                  'max_length': 20,
                  'min_length': 6,
                  'write_only': True,
                  'error_messages': {
                      'max_length': '密码长度不能大于20位',
                      'min_length': '密码长度不能小于6位'
                  }
              },
              'email': {
                  'label': '邮箱',
                  'help_text': '邮箱',
                  'required': True,
                  'validators': [validators.UniqueValidator(queryset=User.objects.all(), message='此邮箱已注册')]
              }
          }
  
      def validate(self, attrs):
          password_confirm = attrs.pop('password_confirm')
          if attrs.get('password') != password_confirm:
              raise serializers.ValidationError('密码与确认密码不一致')
          return attrs
  
      def create(self, validated_data):
          user = User.objects.create_user(**validated_data)	# 调用create_user()方法给密码加密
          payload = jwt_payload_handler(user)	# 使用djangorestframework-jwt模块的方法生成token
          token = jwt_encode_handler(payload)
          user.token = token	# 给用户添加token属性，用于序列化输出
          return user
  ```

  ```python
  # 路由
  from django.urls import path
  from rest_framework_jwt.views import obtain_jwt_token
  from user import views
  
  urlpatterns = [
      path('login/', obtain_jwt_token),
      path('register/', views.UserView.as_view()),
  ]
  # 视图
  from user import serializers
  from django.contrib.auth.models import User
  from rest_framework.generics import CreateAPIView
  
  
  class UserView(CreateAPIView):
      queryset = User.objects.all()
      serializer_class = serializers.UserSerializer
  ```

  

