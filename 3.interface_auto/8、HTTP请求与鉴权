##### 一、HTTP Headers

- Request Headers
  - Accept：表示浏览器希望收到服务器返回的数据类型
  - Accept-Encoding：希望得到文本的解压方式
  -  Accept-Language：文本语言
  -  Cache-Control ：缓存相关
  -  Connection ：连接方式
  -  Cookie ：保存用户的相关信息
  -  Host ：请求的域名
  -  User-Agent ：浏览器的相关信息
- Response Headers

##### 二、HTTP请求方法

| 方法    | 描述                                                         |
| ------- | ------------------------------------------------------------ |
| GET     | 请求页面的指定信息，并返回实体主题                           |
| HEAD    | 类似于get请求，只不过返回的响应中没有具体的内容，用于获取报头 |
| POST    | 向指定资源提交数据进行处理请求，数据被包含在请求体中。POST请求会导致新的资源建立和已有资源的修改 |
| PUT     | 从客户端向服务器传送的数据取代指定的文档的内容               |
| DELETE  | 请求服务器删除指定页面                                       |
| CONNECT | HTTP1.1协议中预留给能够将连接改为管道方式的代理服务器        |
| OPTIONS | 允许客户端查看服务器的性能                                   |
| TRACE   | 回显服务器收到的请求，主要用于测试或诊断                     |

**HTTP请求常用的Get和Post请求两种方法**

- GET是从服务器上获取数据，POST是向服务器传送的数据
- GET请求参数显示在浏览器网址上
- POST请求参数在请求体当中，消息长度没有限制而已以隐式的方式进行发送

##### 三、HTTP响应状态码

```python
# 1xx：信息
100 Continue
服务器仅接收到部分请求，但是服务器没有拒绝请求，客户端应该继续发送其余的请求
101 Switching Protocols
服务器转换协议：服务器将遵从客户的请求转换到另一种协议

# 2xx：成功
200 OK
请求成功
201 Created
请求被创建完成，同时新的资源被创建
202 Accepted
供处理的请求已被接收，但是处理未完成
203 Non-authoritative Informatica
文档已经正常的返回，但一些应答头不正确，因为使用的是文档拷贝
204 No Connect
没有新文档，浏览器应该继续显示原来的文档。如果用户定期的刷新页面，而Servlet可以确定用户文档足够新，这个状态码是很有用的
205 Reset Content
没有新文档，但浏览器应该重置它所有显示的内容。用来强制浏览器清除表单输入内容
206 Partial Content
客户发送了一个带有Range头的GET请求，服务器完成了它

# 3xx：重定向
300 Multiple Choices
多重选择。链接列表，用户可以选择某链接到达目的地，最多允许五个地址
301 Moved Permanently
所请求的页面已经转至新的url
302 Move Temporarily
所请求的页面已经临时转移至新的url
303 See Other
所请求的页面可以在别的url下被找到
304 Not Modified
305 Use Proxy
306 Unused
307 Temporary Redirect

# 4xx：客户端错误
400 Bad Request
服务器未能理解请求
401 Unauthorized
被请求的页面需要用户名和密码
401.1
登录失败
401.2
服务器配置导致登录失败
401.3
由于ACL对资源的限制而未获得授权
401.4
筛选器授权失败
401.5
ISPAI/CGI应用程序授权失败
401.7
访问被web服务器上的URL授权策略拒绝。这个错误代码为IIS6.0所专用
402 Payment Required
此代码尚无法使用
403 Forbidden
对被请求页面的访问禁止
403.1
执行访问被精致
403.2
读访问被禁止
403.3
写访问被禁止
403.4
要求SSL
403.5
要求SSL 128
403.6
IP地址被拒绝
403.7
要求客户端证书
403.8
站点访问被拒绝
403.9
用户数过多
403.10
配置无效
403.11
密码更改
403.12
拒绝访问映射表
403.14
拒绝目录列表
403.15
超出客户端访问许可
403.16
客户端证书不收信任或无效
403.17
客户端证书已过期或未生效
403.18
在当前的应用程序池中不能执行所请求的URL，IIS 6.0独有
403.19
不能为这个应用程序池的客户端执行CGI，IIS 6.0独有
403.20
Password登录失败，IIS 6.0独有
404 Not Found
服务器无法找到被请求的页面
404.0
没有找到文件或目录
404.1
无法在所请求的端口上访问web站点
404.2
web服务扩展锁定策略阻止本请求
404.3
MIME映射策略阻止本请求
405 Method Not Allowed
请求中指定的方法不被允许
406 Not Acceptable
服务器生成的响应无法被客户端所接受
407 Proxy Authentication Required
用户必须先使用代理服务器进行验证，请求才会被处理
408 Request Timeout
请求超出了服务器的等待时间
409 Conflict
由于冲突，请求无法被完成
410 Gone
被请求的页面不可用
411 Length Required
“Content-Length”未被定义，如无此内容，服务器不会接受请求
412 Precondition Failed
请求中的前提条件被服务器评估为失效
413 Request Entity Too Large
由于所请求的实体太大，服务器不会接受请求
414 Request-url Too Long
由于url太长，服务器不会接受请求。当post请求被转换为带有很长的查询信息的get请求时，就会发生这种情况狂
415 UNsupported Media Type
由于媒体类型不被支持，服务器不会接受请求
416 Requested Range Not staisfiable
服务器不能满足客户在请求中指定的Range头
417 Exceptation Failed
执行失败
423
锁定的错误

# 5xx服务器错误
500 Internal Server Error
请求未完成。服务器遇到不可未知的情况
500.12
应用程序正忙于在web服务器上重新启动
500.13
web服务器太忙
500.15
不允许直接请求Global.asa
500.16
UNC授权凭证不正确，为IIS 6.0独有
500.18
URL授权存储不能打开，为IIS 6.0独有
500.100
内部ASP错误
501 Not Implemented
请求未完成，服务器不支持所请求的功能
502 Bad Gateway
请求未完成，服务器从上游服务器收到一个无效的响应
502.1
CGI应用程序超时
502.2
CGI应用程序储蓄哦
503 Service Unavailable
请求未完成，服务器临时过载或宕机
504 Gateway Timeout
网关超时
505 HTTP Version Not Supported
服务器不支持请求中指明的HTTP协议
```

##### 四、鉴权、授权

1、cookie和session

2、token



