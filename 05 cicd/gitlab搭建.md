#### docker安装gitlab

1. 获取镜像或加载已有的镜像tar文件

   ```bash
   docker pull gitlab镜像
   docker load -i gitlab.tar文件
   ```

2. 启动gitlab容器

   ```bash
   docker run -d –restart=always -p 21100:21100 -p 21101:443 -p 21102:22 -v /opt/gitlab/gitlab-data:/var/opt/gitlab -v /etc/localtime:/etc/localtime -v /opt/gitlab/logs:/var/log/gitlab -v /opt/gitlab/gitlab-config:/etc/gitlab -m 54000M --name gitlab --privileged=true h3ccloud/devopscloud/os-gitlab:clean
   ```

3. 修改gitlab配置文件

   - 将gitlab.rb放到/opt/gitlab/gitlab-config
   - 或修改/opt/gitlab/gitlab-config/gitlab.rb文件指定external_url(指定本机IP地址)和gitlab_rails['gitlab_shell_ssh_port']=21102

4. 重启gitlab容器(docker restart gitlab容器)