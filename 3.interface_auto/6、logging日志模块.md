#### 一、logging模块日志级别介绍

- 日志一共分成5个等级，从低到高分别为：

  | **级别** | **说明**                                                     |
  | -------- | ------------------------------------------------------------ |
  | DEBUG    | 输出详细的运行情况，主要用于调试                             |
  | INFO     | 确认一切按预期运行，一般用于输出重要运行情况                 |
  | WARNING  | 一些意想不到的事情发生了（比如：“警告：内存空间不足”），但是这个软件还能按预期工作，在不久的将来会出现问题 |
  | ERROR    | 发生了错误，软件没能执行一些功能，还可以继续执行             |
  | CRITICAL | 一个严重的错误，表明程序本身可能无法继续运行                 |

#### 二、日志模块logging的使用

logging模块内置一个名叫root的日志收集器，收集的日志等级默认为WARNING以上。

**1、创建日志收集器对象**

```python
logger = logging.getLogger('mylog')	# 创建日志收集器
logger.setLevel('DEBUG')	# 设置日志收集器等级
```

**2、创建日志输出渠道**

有两种方式：一种输出到控制台，另一种记录到文件

- 输出到控制台

  ```python
  sh = logging.StreamHandler()	# 创建日志输出渠道
  sh.setLevel('DEBUG')	# 设置输出渠道等级
  logger.addHandler(sh)	# 输出渠道添加到日志收集器
  ```

- 输出到文件

  ```python
  fh = logging.FileHandler('log.txt', mode='w', encoding='utf8')
  fh.setLevel('DEBUG')
  logger.addHandler(fh)
  ```

**3、指定日志输出格式**

```python
fot = '%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s:%(message)s'	# 日志输出的格式
formatter = logging.Formatter(fot)	# 创建日志格式对象
fh.setFormatter(formatter)	# 输出格式绑定输出渠道
log.exception(e)	# 记录异常到日志
```

#### 三、日志模块的封装

```python
# 配置文件读取的日志配置
log_level = myconf.get('log', 'log_level')  # 日志收集器等级
sh_level = myconf.get('log', 's_level')  # 输出到控制台的等级
fh_level = myconf.get('log', 'f_level')  # 输出到文件的等级
name = myconf.get('log', 'filename')  # 日志名
file_path = os.path.join(LOG_DIR, name)  # 日志存放的路径

class Logger(object):

    def __new__(cls, *args, **kwargs):
        # 创建日志收集器对象
        my_log = logging.getLogger('my_log')
        my_log.setLevel(log_level)

        # 创建日志输出渠道
        # 输出到控制台
        sh = logging.StreamHandler()
        sh.setLevel(sh_level)
        # 输出到文件
        fh = logging.FileHandler(file_path, mode='w', encoding='utf8')
        fh.setLevel(fh_level)

        # 日志输出渠道绑定日志收集器
        my_log.addHandler(sh)
        my_log.addHandler(fh)
        # 设置日志输出格式
        log_format = '%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s:%(message)s'  # 日志样式
        formatter = logging.Formatter(log_format)
        sh.setFormatter(formatter)
        fh.setFormatter(formatter)
        return my_log

log = Logger()
```



