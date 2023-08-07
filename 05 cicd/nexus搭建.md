#### docker安装nexus

1. 获取镜像或加载已有的镜像tar文件

2. 启动nexus容器

   ```bash
    docker run -d --restart=always -p 8081:8081 -p 21181:21181 -p 21182:21182 -v /var/opt/nexus:/nexus-data -v /etc/localtime:/etc/localtime -m 24000M --name nexus --privileged=true os-harbor-svc.default.svc.cloudos:443/helm/h3ccloud/nexus:1.0
   ```

3. 替换nexus默认库

   - 获取nexus相关依赖库打包文件

   - 将打包文件解压并覆盖到/var/opt/nexus目录下

     ```bash
     tar -zxvf ./nexus-20201224.tgz
     rm -rf /var/opt/nexus/
     mv ./nexus /var/opt/
     ```

   - 重启容器： docker restart nexus容器



