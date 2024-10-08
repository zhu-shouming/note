#### 一、WebDriver

1. 安装selenium类库

   - 方式一：pip install selenium （[pypi selenium](https://pypi.org/project/selenium/)）
   - 方式二：python setup.py install （[pypi selenium源码包](https://pypi.org/project/selenium/#files)）

2. 八大基本组成

   1. 驱动实例开启会话

      ```python
      driver = webdriver.Chrome()
      ```

   2. 在浏览器上执行操作

   3. 请求浏览器信息：包括窗口句柄、浏览器尺寸/位置、cookie、警报等

   4. 建立等待策略：强制等待、隐式等待、显示等待

   5. 查找元素

   6. 操作元素

   7. 获取元素信息

   8. 结束会话

   [chromedriver下载](http://chromedriver.storage.googleapis.com/index.html)

#### 二、浏览器配置options

1. 页面加载策略

   ```python
   opts = webdriver.ChromeOptions()
   opts.page_load_strategy = 'normal'	# normal:默认值, 等待所有资源下载;eager:DOM 访问已准备就绪, 但诸如图像的其他资源可能仍在加载;none:完全不会阻塞 WebDriver
   ```

2. 排除的参数

   ```python
   # 如果不希望添加某些参数，可以将其传入excludeSwitches
   opts.add_experimental_option("excludeSwitches", ['enable-automation'])	# 关闭Chrome浏览器受自动控制的提示
   ```

   ​

