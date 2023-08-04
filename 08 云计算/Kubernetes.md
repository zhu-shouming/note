#### Kubernetes基础模块

1. 创建Kubernetes集群

   ```bash
   minikube start	# 创建一个单节点的kubernetes
   kubectl get nodes	# 获取节点
   kubectl cluster-info	# 查看集群信息
   ```

2. 部署应用

   ```bash
   # 使用kubectl run部署一个应用
   kubectl run 应用名 --image=镜像地址 --port=应用对外服务的端口号
   # Deployment是Kubernetes的术语，理解为应用；Pod是容器的集合，通常会将紧密相关的一组容器放到一个Pod中，同一个Pod中的所有容器共享IP地址和Port空间，也就是说它们在一个network namespace中。Pod是Kubernetes调度的最小单位，同一Pod中的容器始终被一起调度。
   kubectl get pods	# 获取当前的pod
   ```

3. 访问应用

   ```bash
   # 默认情况下，所有Pod只能在集群内部访问。为了能够从外部访问应用，需要将容器的端口映射到节点的端口，使用kubectl expose映射到节点的端口
   kubectl expose deployment/应用名 --type="NodePort" --port 节点端口
   kubectl get services	# 获取已部署的服务
   ```

4. 扩容与缩容

   ```bash
   # 使用kubectl scale使当前pod增加到3个，通过curl访问应用，每次请求发送到不同的Pod，3个副本轮询处理，这样就实现了负载均衡
   kubectl scale deployments/应用名 --replicas=3	# 将副本数增加到3个
   # 要scale down也很方便
   kubectl scale deployments/应用名 --replicas=2
   kubectl get deployments
   ```

5. 滚动更新

   ```bash
   # 从原有v1镜像升级到v2
   kubectl set image deployments/应用名 应用名=镜像:v2
   # 回退到v1版本
   kubectl rollout undo deployments/应用名
   ```

#### Kubernetes重要概念

**Cluster**是计算、存储和网络资源的集合，Kubernetes利用这些资源运行各种基于容器的应用。

**Master**是Cluster的大脑，它的主要职责是调度，即决定将应用放在哪里运行。为了实现高可用，可以运行多个Master。

**Node**的职责是运行容器应用。Node由Master管理，Node负责监控并汇报容器的状态，同时根据Master的要求管理容器的生命周期。

**Pod**是Kubernetes的最小工作单元。每个Pod包含一个或多个容器。Pod中的容器会作为一个整体被Master调度到一个Node上运行。

**Controller**：Kubernetes通常不会直接创建Pod，而是通过Controller来管理Pod的。Kubernetes提供了多种Controller，包括Deployment、ReplicaSet、DaemonSet、StatefuleSet、Job等

**Service**定义了外界访问一组特定Pod的方式。Service有自己的IP和端口，Service为Pod提供了负载均衡。

Namespace