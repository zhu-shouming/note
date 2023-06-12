#### 一、Git配置

git提供了git config工具，用来读取获取配置相应的工作环境变量。

- 1、配置用户信息

  > git config --global user.name "zhushouming"
  >
  > git config --global user.email `zsm2260@qq.com`

- 2、选择差异分析工具

  > git config --global merge.tool vimdiff

- 3、生成SSH Key

  > ssh-keygen -t rsa -C "`zsm2260@qq.com`"
  > 命令中的email就是github的账号，需要保持一致。

- 4、配置远程仓库秘钥

  > 1.查看秘钥：cat ~/.ssh/id_rsa.pub，赋值本地公共秘钥id_rsa.pub里面的key
  >
  > 2.远程仓库进入Account-->Setting，选择SSH and GPG keys，将本地的秘钥添加到远程仓库上并保存
  >
  > 3.验证是否成功：ssh -T `git@github.com`

- 5、添加远程路由，并下拉代码

  > ```
  > git remote add origin git@github.com:tianqixin/runoob-git-test.git
  > git clone git@github.com:tianqixin/runoob-git-test.git
  > ```

#### 二、git基本操作

##### 初始化本地仓库

```bash
git clone 仓库地址	# 从远程仓库拷贝项目到本地
git init 仓库名	# 本地初始化一个本地仓库
```

##### 提交修改

```bash
git status	# 查看当前目录下文件的状态
git add 文件	# 将工作区修改的文件添加到暂存区
git commit -m "提交说明"	# 将暂存区的修改同步到本地仓库
git tag -a v1.4 -m "my version 1.4"	#添加注释标签
```

##### 版本回退/撤销修改

```bash
git log	# 查看历史版
git reset --hard 版本号	# 版本回退
git restore --staged 	# 撤销暂存区到工作区
git restore 文件	# 撤销工作区的修改
```

##### 远程仓库操作

```bash
git remote -v	# 查看git存储的url
git remote add <alias> <url>	# 添加远程仓库并起别名
git remote rm name	# 删除一个仓库连接
git pull origin 分支	# 远程仓库代码同步到本地
git push origin 分支	# 本地代码合并到远程仓库
```

##### 常用合并操作

```bash
git checkout -b zsm	# 创建并切换分支工作
git checkout main	# 分支工作完并提交修改后切换到主分支
git merge zsm	# 合并分支修改到主分支
git branch -d zsm	# 删除分支
```

##### 切换远程分支

 ```bash
# 如果切换不成功，使用**git fetch**拉取远程信息到本地，再切换分支
git branch -b 本地分支名 origin/远程分支名	
 ```

##### git添加忽略文件

> 在仓库目录创建一个`.gitignore`文件，将需要忽略的文件添加到文件中

#### 三、常见问题

##### github打开缓慢问题

- 修改HOST文件

  1. 管理员身份打开记事本，记事本选择文件类型打开HOST文件

  > 文件路径： C:\WINDOWS\system32\drivers\etc 

  2. 查询3个网址对应的IP地址(可能会改变)

  >  github.com 、assets-cdn.github.com、github.global.ssl.fastly.net

  3. HOST文件添加一下代码

  ```
  140.82.112.4 github.com
  185.199.108.153 assets-cdn.github.com
  199.232.69.194 github.global.ssl.fastly.net
  ```

##### gitignore添加忽略文件不生效

原因：该文件已经commit，在缓存中存在

解决办法：删除该文件的缓存	git rm -r -cache 文件名

忽略某个已提交的文件：git update-index --assume-unchanged 文件

取消忽略：git update-index --no-assume-unchanged 文件

