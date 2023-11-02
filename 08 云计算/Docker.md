#### 容器生态系统

**容器核心技术**：容器在单个host上运行起来的那些技术

1. 容器规范：runtime spec和image format spec
2. 容器runtime：runtime需要和操作系统kernel紧密协作，为容器提供运行环境。lxc、runc(docker默认的runtime)和rkt是目前主流的三种容器runtime
3. 容器管理工具：lxd是lxc对应管理工具；runc管理工具是docker engine，docker engine包含后台deamon和cli两个部分；rkt的管理工具是rkt cli
4. 容器定义工具：允许用户定义容器的内容和属性
   - docker image是Docker容器的模板
   - dockerfile包含若干命令的文本文件，可通过这些命令创建docker iamge
   - ACI与docker image类似，由CoreOS开发的rkt容器的image格式。
5. Registries
   - Docker Registry构建私有的Registry
   - Docker Hub是docker为公众提供的托管Registry
   - Quay.io与Docker Hub类似。
6. 容器OS：专门运行容器的操作系统。如coreos、atomic、ubuntu core

**容器平台技术**：让容器作为集群在分布式环境中运行

1. 容器编排引擎：基于容器的应用一般会采用微服务架构，基于微服务的应用实际上是一个动态可伸缩的系统，而容器编排引擎是一种高效的方法来管理容器集群
   - docker swarm是docker开发的容器编排引擎
   - kubernetes是Google领导开大的开源容器编排引擎，同时支持Docker和CoreOS容器
   - mesos是一个通用的集群资源调度平台，mesos与marathon一起提供容器编排引擎
2. 容器管理平台：架构在容器编排引擎之上的一个更为通用的平台，抽象了编排引擎的底层实现细节，为用户提供更方便的功能。Rancher和ContainerShip是容器管理平台的典型代表
3. 基于容器的PaaS：为微服务应用开发人员和公司提供了开发、部署和管理应用的平台，使用户不必关心底层基础设施而专注于应用的开发。Deis、Flynn和Dokku都是开源容器PaaS的代表

**容器支持技术**

1. 容器网络：docker network是Docker原生的网络解决方案，还可以采用如flannel、weave和calico
2. 服务发现：保存容器集群中所有微服务最新的信息，并对外提供API，提供服务查询功能。etcd、consul和zookeeper是服务发现的典型解决方案
3. 监控：docker ps/top/stats是Docker原生的命令行监控工具。sysdig、cAdvisor/Heapster和Weave Scope是其他开源的容器监控方案
4. 数据管理：Rex-Ray管理工具
5. 日志管理：docker logs和logspout
6. 安全性：OpenSCAP是一种容器安全工具

#### Docker架构

Docker的核心组件包括：

- Docker客户端：Client

- Docker服务器：Docker Daemon

  ```bash
  # 1.docker daemon是服务器组件，以linux后台服务的方式进行
  systemctl status docker.service
  # 2.docker daemon运行在docker host，负责创建、运行、监控、构建、存储镜像，默认配置只能响应本地Host的客户端请求。如果要允许远程客户端请求，需要在配置文件中打开TCP监听
  编辑配置文件：/etc/systemd/system/multi-user.target.wants/docker.service，在环境变量ExecStart后面添加 -H tcp://0.0.0.0,允许来自任意ip的客户端连接
  # 3.修改完配置重启docker daemon生效
  systemctl daemon-reload
  systemctl restart docker
  # 4.客户端在命令行里加上-H参数，即可与远程服务器通信
  docker -H 远程客户端ip info
  ```

- Docker镜像：Image

  ```bash
  创建docker容器的模板，镜像有多种生成方法：
  1.从无到有开始创建镜像
  2.下载现成的镜像
  3.在现有镜像上创建新的镜像
  ```

- Docker镜像仓库：Registry

- Docker容器：Container

  ```bash
  镜像是软件生命周期的构建和打包阶段，而容器是启动、运行阶段
  ```

#### Docker镜像

- base镜像：1.不依赖其他镜像，从scratch构建；2.其他镜像可以之为基础进行扩展。base镜像通常是各种linux发行版的docker镜像，如Ubuntu Debian，Centos等。
- 镜像分层结构：构建的镜像是从base镜像一层一层叠加生成。每安装一个软件就在现有镜像的基础上增加一层。最大的好处是**共享资源**

##### 构建镜像

docker提供了两种构建镜像的方法：

1. docker commit命令

2. Dockerfile构建文件

docker commit命令构建新建井包含三个步骤：

1. 运行容器
2. 修改容器
3. 保存为新镜像：docker commit CONTAINER [REPOSITORY[:TAG]]

Dockerfile构建镜像

1. 准备Dockerfile文件

2. **docker build -t 镜像名:tag -f dockerfile文件路径**

   注：当dockerfile文件路径为`.`时，指明build context为当前目录。不要将多余文件放到build context，特别不要把 /、/usr作为build context，否则构建过程会相当缓慢甚至失败。

##### Dockerfile常见指令

- FROM xxx：指定base镜像

- MAINTAINER：设置镜像的作者，可以是任意字符串

- COPY：将文件从build context复制到镜像。COPY支持两种形式：

  1. COPY src dest
  2. COPY ["src","dest"]

- ADD：与COPY类似，不同的是，如果src是归档文件（tar,zip,tgz等），文件会自动到解压到dest 

- ENV：设置环境变量，环境变量可被后面的指令使用

  ```bash
  ENV VERSION 1.6
  RUN apt-get install -y mypackage=$VERSION
  ```

- EXPOSE：指定容器中的进程会监听某个端口，Docker可以将该端口暴露出来

- VOLUME：将文件或目录声明为volume

- WORKDIR：为后面的RUN、CMD、ENTRYPOINT、ADD或COPY指令设置镜像中的当前工作目录

- RUN：在容器中运行指定的命令

- CMD：容器启动时运行指定的命令。Dockerfile中可以有多个CMD指令，但只有最后一个生效。CMD可以被docker run之后的参数替换

- ENTRYPOINT：设置容器启动时运行的命令。Dockerfile中可以有多个ENTRYPOINT指令，但只有最后一个生效。CMD或docker run之后的参数会被当作参数传递给ENTRYPOINT。

  ```bash
  FROM scratch	# scratch为一个虚拟镜像，表示从0开始
  COPY hello /	# 将文件复制到镜像的根目录
  ADD centos-xx.tar.xz /	# 将远端资源下载或本地文件复制到容器中
  CMD ["/hello"]	# 启动容器时执行hello文件
  ```

RUN vs CMD vs ENTRYPOINT区别

- RUN：执行命令并创建新的镜像层，RUN经常用于安装软件包
- CMD：设置容器启动后默认执行的命令及其参数
  1. 如果docker run指定了其他命令，CMD指定的默认名了将被忽略。
  2. 如果dockerfile中有多个CMD指令，只有最后一个CMD有效。
  3. CMD ["param1","param2"]为ENTRYPOINT提供额外参数时，此时ENTRYPOINT必须使用Exec格式
- ENTRYPOINT配置容器启动时运行的命令
  1. ENTRYPOINT指令可让容器以应用程序或者服务的形式运行
  2. ENTRYPOINT指定要执行的命令和参数不会被忽略，一定会被执行，即使运行docker run时制定了其他命令
  3. ENTRYPOINT的shell格式会忽略任何CMD或docker run提供的参数

Shell和Exec格式：

都可以使用两种方式指定RUN、CMD和ENTRYPOINT要运行的命令

- shell格式：<instruction> <command>，当指令执行时，shell格式底层会调用 /bin/sh -c [command]

  ```bash
  RUN apt-get install python3
  CMD echo "Hello world"
  ENTRYPOINT echo "Hello world"
  ```

- Exec格式：<instruction> ["executable", "param1", "param2",...]，当指令执行时，会直接调用 [command]，不会被shell解析

  ```bash
  ENV name world
  ENTRYPOINT ["/bin/sh","-c","echo Hello $world"]
  ```

注：CMD和ENTRYPOINT推荐使用Exec格式，因为指令可读性更强，更容易理解。RUN则两种格式都可以

##### 搭建私有registry

1. 启动registry容器

   ```bash
   docker run -d -p 5000:5000 --restart always --name registry registry:2
   # 验证安装：使用浏览器访问http://<your-server-ip>:5000/v2/_catalog
   ```

2. 上传镜像到registry

   ```bash
   # 通过docker tag重命名镜像，使之与registry匹配(<your-server-ip>:5000/<your-image>:<tag>上传到指定镜像仓库的固定格式)
   docker tag <your-image>:<tag> <your-server-ip>:5000/<your-image>:<tag>
   # 上传镜像
   docker pull <your-server-ip>:5000/<your-image>:<tag>
   ```

参开文档：https://docs.docker.com/registry/configuration/

##### 镜像操作常用命令

```bash
docker images	# 显示镜像列表
docker rmi 镜像ID	# 删除docker host中的镜像，如果一个镜像对应多个tag，只有当最后一个tag被删除时，镜像才真正删除
docker history 镜像ID	# 显示镜像构建历史
docker search 镜像名称:tag	# 搜索Docker Hub中的镜像
docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]	# 从容器创建新镜像
docker build -t 镜像名:tag -f dockerfile文件路径	# 从Dockerfile构建镜像
docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]	# 给镜像打tag
docker pull [选项] [Docker镜像地址[:端口号]/] 仓库名[:标签]	# 从registry下载镜像
docker push	[选项] [Docker镜像地址[:端口号]/] 仓库名[:标签]	# 将镜像上传到registry
docker image rm [选项] <镜像1> [<镜像2> ...]	# 删除Docker host中的镜像

docker save -o mycontainer.tar mycontainer:latest	# 导出为压缩文件
docker load -i mycontainer.tar	# 导入压缩文件
```

#### Docker容器

##### 运行容器

1. CMD执行令

2. ENTRYPOINT指令

3. 在docker run命令行中指定：docker run [options] image [command] [arg...] 

   ```bash
   # options详解
   -d	# 以后台方式启动容器
   --name xxx	# 显式地为容器命名
   -it	# 以交互模式打开终端，一般配合docker exec使用
   -p	# 指定宿主机端口映射到容器服务端口
   --restart=always	# 容器能够自动重启
   -restart=on-failure:3	#启动进程退出代码非0，则重启容器，最多重启3次
   --rm	# 如果容器为exit状态，会自动删除创建的容器
   --net	# 指定要加入的网络
   -v	# 将本地文件和容器文件进行映射
   
   # 限制容器对内存的使用，与操作系统类似，容器可使用的内存包括两部分：物理内存和sqap。
   -m或-memory：设置内存的使用限额。只指定-m而不指定--memory-swap，那么--memory-swap默认为-m的两倍
   --memory-swap：设置内存+swap的使用限额
   --vm 1	# 启动1个内存工作线程
   --vm-bytes 280M	# 每个线程分配280MB内存
   
   # 限制容器对CPU的使用
   -c或--cpu-shares：docker可以通过-c或--cpu-shares设置容器使用CPU的权重。如果不指定，默认为1024
   
   # 限制容器的Black IO(磁盘的读写)
   --blkio-weight：docker可通过设置权重、限制bps和iops的方式控制容器读写磁盘的带宽，默认为500
   ```

进入容器的两种方法：

1. docker attach
   - 直接进入容器启动命令终端，不会启动新的进程
   - 如果想直接在终端中查看启动命令的输出，用attach；其他情况使用exec
2. docker exec
   - exec在容器中打开新的终端，并且可以启动新的进程
     - docker exec -it <container> bash|sh 是执行exec最常用的方式

##### 容器底层技术

- cgroup全称Control Group。Linux操作系统通过cgroup可以设置进程使用CPU、内存和IO资源的限额。在 /sys/fs/cgroup/cpu/docker、/sys/fs/cgroup/memory/docker和 /sys/fs/cgroup/blkio/docker中分别保存的是cpu相关、内存以及Block IO的cgroup配置
- namespace实现了容器间资源的隔离，Linux使用了6种namespace，分别对应6种资源：Mount、UTS、IPC、PID、Network和User

##### 容器操作常用命令

```bash
docker ps	# 查看Docker host中当前运行的容器，-a选项会显示所有状态的容器
docker logs -f 容器ID	# 查看容器运行日志，-f表示实时查看
docker kill/stop/start/restart 容器ID	# 快速停止/停止/启动/重启容器
docker pause/unpause 容器ID	# 暂停/恢复运行容器
docker create/rm 容器ID	# 创建/删除容器
docker rm -v $(docker ps -aq -f status=exited)	# 批量删除所有已经退出的容器
docker history 容器ID # 查看容器运行的历史记录
docker inspect 容器ID	# 查看容器的配置和状态信息
docker cp xx.html ContainID://user/share/nginx/xx.html	# 拷贝本机xx.html到容器下
docker top ContainID # 查看容器的进程信息
docker stats ContainID # 查看容器的资源信息
```

#### Docker网络

docker安装时会自动在host上创建三个网络

- none网络：什么都没有的网络，挂载这个网络下的容器除了lo，没有其他任何网卡。容器创建时，可以通过--network=none指定使用none网络。一般用于安全性要求高并且不需要联网的应用

- host网络：连接到host网络的容器共享Docker Host的网络线，容器的网络配置与host完全一样。可以通过 --network=host指定使用host网络。

- bridge网络：Docker安装时会创建一个命名为docker0的Linux bridge。如果不指定--network，创建的容器默认都会挂到docker0上。

除了自动创建的网络，用户可以根据业务需要创建user-defined网络

- user-defined网络：有三种网络驱动，bridge、overlay和macvlan，overlay和macvlan用于创建跨主机的网络

##### 容器间通信

1. IP通信：两个容器要能通信，必须要有属于同一个网络的网卡。不同网络的容器间通信，通过docker network connect将现有容器加入到指定网络
2. Docker DNS Server：从Docker 1.10版本开始，docker daemon实现了一个内嵌的DNS server，使容器可以直接通过“容器名”通信。只要在启动时用--name为容器命名就可以了。**使用docker DNS有个限制：只能在user-defined网络中使用。**默认的bridge网络是无法使用DNS的。
3.  joined容器：先创建一个容器，名字为web1。然后创建另一个容器并通过 **--network=container:web1**指定joined容器为web1。这两个容器共享相同的网络栈

##### 常见命令

```bash
docker network ls	# 查看host有的网络类型
docker network inspect bridge	# bridge网络的配置信息
docker network create --driver bridge my_net	# 创建bridge类型网络my_net
# 创建网络指定IP网段。使用--subnet和--gateway 参数
docker network create --subnet 172.22.16.0/24 --gateway 172.22.16.1 my_net
# 运行容器指定网络及分配IP。使用--network和--ip参数
docker run -it --network=my_net --ip 172.22.16.8 my_net	
# 不同网络的容器间通信使用docker network connect命令实现
docker network connect my_net 容器ID	# 把容器加入网卡，和该网卡中的容器实现ip通信
docker run -it --network=container:web1 httpd	# 通过join容器web1，实现web1和httpd通信
```

#### Docker存储

Docker为容器提供了两种存放数据的资源：

1. 由storage driver管理的镜像层和容器层
2. Data Volume
   - 将host上已存在的目录或文件mount到容器，通过 -v将其mount到容器。-v的格式为 <host path>:<container path>。
   - 容器内数据共享：1.将容器挂载到一个目录；2.volume container提供volume的容器

##### 常用命令

```bash
# 容器与host之间复制数据，也可以直接通过linux的cp命令
docker cp 文件 容器ID:指定目录
docker volume ls	# 查看容器使用的docker managed volume
docker volume rm ID	# 删除volume
```

#### 容器进阶知识

1. multi-host
2. 容器网络
3. 监控
4. 数据管理
5. 管理日志

#### Docker Machine解决方案

容器在多个host启动、运行、停止和销毁，相关容器会通过网络相互通信。Docker Machine可以批量安装和配置docker host

官方安装文档在https://docs.docker.com/machine/install-machine/

#### 容器网络

跨主机网络方案包括：（1）docker原生的overlay和macvlan;（2）第三方方案：常用的包括flannel、weave和calico

##### overlay

Docker提供了overlay driver，使用户可以创建基于VxLAN的overlay网络。VxLAN可将二层数据封装到UDP进行传输，VxLAN提供与VLAN相同的以太网二层服务，但是拥有更强的扩展性和灵活性。

##### macvlan

macvlan本身是linxu kernel模块，其功能是允许同一个物理网卡配置多个MAC地址，即多个interface，每个interface可以配置自己的IP。macvlan本质上是一种网卡虚拟化技术

#### 日志管理

在开源的日志管理方案中，最出名的莫过于ELK了。ELK是三个软件的合称：Elasticsearch、Logstash、Kibana

#### docker compose

作用：同时启动多个容器

##### 1.安装

##### 2.使用docker compose

- 项目根目录下创建docker-compose.yaml

  ```shell
  # 指定版本信息
  VERSION: '3'
  
  # 定义服务
  services:
  	# 创建的具体服务
  	db:
  		# 指定镜像名（镜像名:tag），如果本地没有，会从docker hub中下载
  		image:mariadb
		# 运行容器时，指定需要执行的命令或参数
  		command:--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
  		# 指定数据持久化映射
  		volumes:
  			# 数据卷名称或宿主机文件
  			mysql_db:/var/bin/mysql
  		# 指定容器失败时（EXITED），重启策略
  		restart:always
  		# 指定容器中的全局变量
          environment:
          	MYSQL_ROOT_PASSWORD:"123456"
          	MYSQL_DATABASE:my_django
          # 指定容器加入的网络
          networks:
          	django_app_net
      
      django_app:
      	# 指定django_app依赖的服务
      	depends_on:
      		db
      	# 指定通过Dockerfile路径（./django_app_docker）去构建（django_app:v1）镜像
      	build:./django_app_docker
      	image:django_app:v1
      	restart:always
          volumes:
          	logs:/usr/src/app/logs/
          	django_code:/usr/src/app/
          networks:
          	django_app_net
          	
  # 指定网络
  networks:
  	# 指定网络名称，默认会创建briage桥接网络
  	django_app_net
  	
  # 指定数据卷
  volumes:
  	mysql_db:
      django_code:    	
  	logs:		
  ```
  
  ##### 3.常用命令
  
  ```bash
  # 查看docker-compose.yaml文件配置是否有误
  $ docker-compose config
  # 如果执行命令目录下compose文件未命名docker-compose，需要使用-f指定文件
  $ docker-compose -f docker-pose.yaml config
  # 通过docker-compose文件启动容器，会在卷、网络、容器前面加前缀（当前所在目录名），可以使用-p指定前缀。一旦指定了，在删除容器的时候也需要使用-p指定相应前缀删除
  docker-compose -p my_project up	# 运行容器
  docker-compose -p my_project down # 删除容器、网络...
  ```

#### Docker Swarm

##### 1.Swarm manager

- 切换、加入、移除、维护节点

##### 2.Swarm work

- 运行任务的节点
- 托管容器任务

##### 3.创建集群

- 初始化

##### 4.常用命令

```bash
# docker swarm去操作集群
$ docker swarm --help 
# docker node去操作节点
$ docker node --help
# docker service去操作服务
$ docker service --help
$ docker service ls
```
