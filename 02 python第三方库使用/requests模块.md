#### 1、requests发起get请求

```python
import requests
url = 'http://www.baidu.com'
response = requests.get(url=url)
print(response.text)	# 获取响应内容
print(response.content.decode('utf-8'))	# 获取响应内容
```

- get请求添加请求头信息

  ```python
  # 指定请求头信息，模拟浏览器发出请求
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
  }
  response = requests.get(url=url, headers=headers)
  ```

- get请求添加请求参数信息

  ```python
  data = {"wd": "selenium"}
  response = requests.get(url=url, headers=headers, params=data)
  ```

#### 2、requests发起post请求

```python
data = {
    'name':'xiaoming',
    'age':'18'
}
response = requests.post(url=url, data=data)
response.json()	# 获取响应结果（返回结果为json格式数据才能使用）
```

- 请求参数为json数据

  ```python
  response = requests.post(url=url, json=data)	# 使用json关键字传参
  ```

#### 3、访问需要鉴权的接口

```python
'''方式一：通过创建一个session对象发起请求'''
from request import session
# session对象发送请求的作用：可以记录上一次请求的cookies信息
s = session()
s.post(url=url, data=data)
s.post(url=url1, data=data1)	# 需要鉴权的接口
session.close()	# 关闭session

'''方式二：获取响应的cookie信息发起请求'''
response = requests.post(url=url, data=data)
request.post(url=url1, data=data, cookie=response.cookies)	# response.cookies获取上次请求的cookie信息
```

#### 4、接口请求封装

- HttpSession：可以记住cookie信息的请求类

  ```python
  class HttpSession:
      def __init__(self):
          self.session = requests.session()
      def send(self, method, url, data=None, headers=None, json=None):
          method = method.lower()
          if method == 'get':
              return self.session.get(url=url, params=data, headers=headers, json=json)
          elif method == 'post':
              return self.session.post(url=url, data=data, headers=headers, json=json)
      def close(self):
          self.session.close()
  ```

- HttpRequest：不需要记住cookie的请求类

  ```python
  class HttpRequest:
      def send(self, method, url, data=None, headers=None, json=None):
          method = method.lower()
          if method == 'get':
              return requests.get(url=url, params=data, headers=headers, json=json)
          elif method == 'post':
              return requests.post(url=url, data=data, headers=headers, json=json)
  ```


