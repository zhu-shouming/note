#### 一、Jenkins环境搭建

1. JDK下载，1.8版本以上
2. Jenkins下载安装

Jenkins无法运行

>a.查看Jenkins服务是否起来
>
>b.Jenkins默认端口号被占用，修改其端口号重启服务

#### 二、Jenkins构建项目

1. 创建项目

   选择**新建item**-->输入任务名称-->选择**Freestyle project**-->点击保存

2. 安装插件

   返回**工作台**-->选择**Manage Jenkins**-->选择**Manage Plugins**

3. 构建任务

   a.进入任务的工作区间-->选择**Build Now**-->点击**工作区**（工作区为存放项目代码），会在Jenkins目录下创建workspace目录，把项目的代码放置该目录下

   b.任务下选择**配置**-->选择**构建**-->选择执行的环境命令，输入执行命令（执行命令与终端执行命令一致，路径已Jenkins下workspace目录为初始路径）
   
   c.返回任务下，再次点击 **Build Now**

4. 源码在仓库构建方式

   a.**新建item**-->输入任务名称-->选择**Freestyle project**-->选择源码管理（前提装好git、svn相应的插件）-->填写远程仓库配置-->选择**构建**-->点击保存

5. Jenkins发送邮件

   a.安装插件

   > Email Extension Plugin
   >
   > Email Extension Template Plugin

   b.配置smtp服务器

   >- 邮箱开启smtp服务，获取smtp授权码
   >- 点击**Manage Jenkins**-->选择**Configure System**--> 系统管理员邮件地址填写邮箱地址--> **Extended E-mail Notification**设置smtp服务器地址，Default Content Type选择邮件类型， Default Recipients 填写默认收件人地址，配置smtp账号和认证密码后保存
   >- 进入任务点击配置，配置**构建后操作**

