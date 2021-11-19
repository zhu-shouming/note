#### 1.安装

```python
pip install httprunner==2.3.0
hrun -V	# 查看HTTPRunner版本
hrun -h	# 查看httpRunner帮助文档
hrun --startproject [projectname]	# 创建项目
```

#### 2.httprunner 2.x项目结构

- api目录：存放接口的最小执行单元（正向用例）

- reports目录：用于存放测试报告

- testcases目录：用于处理接口的复杂执行逻辑

- testsuites目录：

  - 添加多条测试用例，批量执行
  - 处理数据驱动测试

- .env文件：用于定义全局环境变量

- debugtalk.py文件：用于处理动态参数或处理参数化动态数据

  ```
  YAML配置文件的格式要求：
  1.yaml是一种强缩进的数据格式，同级键值对缩进必须一致
  2.yaml配置文件的后缀为.yaml或.yml
  3.yaml配置文件中使用#进行注释，不可以在yaml数据行内进行注释
  4.数据格式为key: value，且在同一区域的key不能重复
  5.yaml中的value含有字母，会识别为字符串类型，可以为其添加单引号或双引号指定为字符串类型
  6.yaml中的value为数字，自动识别为int类型
  7.yaml使用-表示数组结构
  ```

  

#### 2.命令行操作演练

- 基本操作
- 创建&引用环境变量
- 调用函数、base_url、添加valiate
- extract实现接口依赖
- 使用测试套件实现数据驱动、set_hooks、teardown_hooks