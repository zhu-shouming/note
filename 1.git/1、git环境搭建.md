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
