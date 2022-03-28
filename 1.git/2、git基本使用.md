##### 初始化本地仓库

> 1、git init 仓库名：在当前目录生成一个.git目录，指定当前目录作为git仓库
>
> 2、git clone <git地址>：从远程仓库拷贝项目到本地

##### git基本操作

> $ git status:查看当前目录下文件的状态
>
> $ git add `<filename>`:将工作区修改的文件添加到暂存区
>
> $ git commit -m "提交说明":将暂存区的修改同步到本地仓库
>
> $ git log或git reflog:查看历史版本
>
> $ git restore --staged `<file>`:撤销暂存区到工作区
>
> $ git restore `<file>`:撤销工作区的修改
>
> $ git reset --hard 版本号:版本回退
>
> $ git tag -a v1.4 -m "my version 1.4":添加注释标签

##### 忽略文件

> 在仓库目录创建一个`.gitignore`文件，将需要忽略的文件添加到文件中将不被版本记录点对点

##### 远程仓库操作

> $ git remote -v:查看git存储的url
>
> $ git remote add `<alias> <url>`:添加远程仓库并起别名
>
> $ git remote rm name:删除一个仓库连接
>
> $ git pull origin main:远程仓库代码同步到本地
>
> $  git push origin main:本地代码合并到远程仓库

##### 分支

> $ git branch testing:创建testing分支并切换到该分支
>
> $ git checkout testing:切换到testing分支
>
> 分支合并：
>
> 	1、创建分支工作：git checkout -b zsm
> 	
> 	2、切换到主分支：git checkout main
> 	
> 	4、合并修补程序：git merge zsm
> 	
> 	5、删除分支：git branch -d zsm

##### 问题

**1.github打开缓慢问题**

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

##### 2.gitignore添加忽略文件不生效

> 改文件已经commit，在缓存中存在
>
> 解决办法：git rm -r -cache 文件名

忽略某个已提交的文件：
- git update-index --assume-unchanged 文件
取消忽略：
- git update-index --no-assume-unchanged 文件
