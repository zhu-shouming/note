#### docker安装nexus

1. 拉取镜像：docker pull sonatype/nexus3

2. 建立本地挂载文件夹(将nexus文件映射改目录)

   ```bash
   mkdir -p /data/nexus/data
   chown -R 200 /data/nexus/data	# 挂载文件夹授权
   ```

3. 创建容器并启动服务

   ```bash
   docker run -d -p 8001:8081 --privileged=true --name nexus -v /data/nexus/data:/nexus-data --restart=always docker.io/sonatype/nexus3
   ```

4. 查看admin密码

   ```bash
   cat /data/nexus/data/admin.password
   ```

   

