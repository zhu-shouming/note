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
> ​	1、创建分支工作：git checkout -b zsm
>
> ​	2、切换到主分支：git checkout main
>
> ​	4、合并修补程序：git merge zsm
>
> ​	5、删除分支：git branch -d zsm