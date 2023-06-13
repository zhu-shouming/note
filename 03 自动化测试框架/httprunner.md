#### 测试用例构成

每个testcase都是HttpRunner的一个子类，必须有两个类属性：**config**和**teststeps**

- config：配置测试用例级别的设置，包含`.base_url`, `.verify`, `.variables`, `.export`
  - Config()：testcase名称，将展示在日志和报告中，必传参数。
  - .base_url()：项目的地址，可选参数。
  - .variables()：配置变量，testcase全局有效，可选参数。
  - .verify()：指定是否验证服务器的TLS证书，常设置为False，可选参数。
  - .export()：指定testcase的导出会话变量，当该测试用例的数据在另外测试用例需要用到时，那么提取的会话变量应该在配置导出部分进行配置。可选参数。
- teststeps：每个步骤对应于一个API请求或另一个testcase引用调用。列表数据。
  - RunRequest用于向API发出请求，并对响应进行提取或验证。RunRequest的参数名称用于指定teststep名称，该名称将显示在执行日志和测试报告中。
  - .with_variables：测试步骤中定义的变量
  - .method(url)：指定HTTP方法和请求的url
  - .with_params()：为请求url指定查询字符串
  - .with_headers()：为请求指定HTTP报头
  - .with_json()：以json格式指定HTTP请求体
  - .extract()：常用.with_jmespath()方式提取响应值并运用到后续测试步骤
  - .validate()：验证结果是否符合预期。.assert_XXX()使用jmespath提取JSON响应体，并使用预期值进行验证

