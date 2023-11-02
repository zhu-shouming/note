from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode


class CCEAPI(RestAPIBase):
    """获取云容器引擎-集群列表"""
    def get_cce_list(self, page=1, size=10, name=''):
        uri = (
            f"/api/cloud/kaas/v1.0/cluster?pageIndex={page}&pageSize={size}&name={name}"
        )
        return self._get(uri)

    def get_clster_detail(self, cluster_id):
        """查看集群详情"""
        uri = f"/api/cloud/kaas/v1.0/cluster/{cluster_id}"
        return self._get(uri)

    def get_cluster_node_info(self, cluster_id):
        """查看集群节点列表"""
        uri = f"/api/cloud/kaas/v1.0/cluster/{cluster_id}/server"
        return self._get(uri)

    def get_ns_of_cluster(self, cluster_id, page=1, size=10, **kwargs):
        """查询集群命名空间 name= 指定名字"""
        uri = f"/api/cloud/kaas/v1.0/clusters/{cluster_id}/namespaces?page={page}&pageSize={size}"
        if kwargs:
            uri = uri + "&" + urlencode(kwargs)
        return self._get(uri)

    def get_cluster_detail(
        self, cluster_id, project_id, page_size=10, page_num=1, **kwargs
    ):
        """查询集群命名空间、所有者、规格等详细信息"""
        uri = f"/api/cloud/cce-project-manager/v1.0/namespace/list?pageSize={page_size}&pageNum={page_num}&clusterId={cluster_id}&projectId={project_id}"
        if kwargs:
            uri = uri + "&" + urlencode(kwargs)
        return self._get(uri)

    def add_namespace(self, name, clusterId, description):
        """新建命名空间"""
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces"
        data = {"name": name, "description": description}
        return self._post(uri, json=data)

    def del_namespace(self, namespace, clusterId):
        """删除命名空间"""
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces/{namespace}"
        return self._delete(uri)

    def create_deployment_workload(self, payload_type, clusterId, namespace, yaml_str):
        """创建工作负载

        Args:
            payload_type (_type_): 工作负载类型：deployments statefulset  daemonset  job cronjob   pod
            clusterId (_type_): 集群id
            namespace (_type_): 命名空间
            yaml_str (_type_): yaml文件内容  str类型
        """
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces/{namespace}/{payload_type}/yaml"
        data = {"yaml_str": yaml_str}
        print(data)
        return self._post(uri, data)

    def get_deployment_by_ns(
        self, payload_type, clusterId, namespace, page=1, size=10, name=''
    ):
        """指定集群 指定命名空间 查询工作负载

        Args:
            payload_type (_type_): 工作负载类型：deployments statefulsets  daemonsets  jobs cronjobs   pods
            clusterId (_type_): 集群id
            namespace (_type_): 命名空间
        """
        uri = f"/api/cloud/kaas/v1.0/{payload_type}"
        data = {
            "page": page,
            "pageSize": size,
            "namespaces": [namespace],
            "name": name,
            "statuses": [],
            "clusterId": clusterId,
            "order": "desc",
        }
        return self._post(uri, data)

    def del_deployment_workload(self, payload_type, clusterId, namespace, payload):
        """删除工作负载

        Args:
            payload_type (_type_): 工作负载类型：deployments statefulsets  daemonsets  jobs cronjobs   pods
            clusterId (_type_): 集群id
            namespace (_type_): 命名空间

        """
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces/{namespace}/{payload_type}/{payload}"
        return self._delete(uri)

    def stop_workload(self, payload_type, clusterId, namespace, payload):
        """停止工作负载  deployment  statefulsets  cronjob
        Args:
            payload_type (_type_): 类型
            clusterId (_type_): 集群id
            namespace (_type_): 命名空间
            payload (_type_): 工作负载实例的名字
        """
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces/{namespace}/{payload_type}/{payload}/stop"
        return self._put(uri)

    def start_workload(self, payload_type, clusterId, namespace, payload):
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces/{namespace}/{payload_type}/{payload}/start"
        return self._put(uri)

    def scale_workload(self, payload_type, clusterId, namespace, payload, data):
        """工作负载（deployment statefulset等）实例伸缩

        Args:
            payload_type (_type_): 工作负载类型：deploy statefulset  daemonset  job cronjob   pod
            clusterId (_type_): 集群id
            namespace (_type_): 命名空间
        """
        uri = f"/api/cloud/kaas/v1.0/clusters/{clusterId}/namespaces/{namespace}/{payload_type}/{payload}/scale"
        return self._put(uri, data)

    def get_storage_classes(
        self, cluster_id, page=1, page_size=2147483647, provisioner=""
    ):
        """
        获取存储类列表

        :param cluster_id: 集群ID
        :param page:
        :param page_size:
        :param provisioner:
        :return:
        """

        uri = "/api/cloud/kaas/v1.0/clusters/" + cluster_id + "/storageclasses"

        data = {"page": page, "pagesize": page_size, "provisioner": provisioner}

        return self._post(uri=uri, json=data)

    def get_cce_cluster_quota(self, cluster_id, namespace):
        """
        获取cce集群规格

        :param cluster_id: 集群ID
        :param namespace: 命名空间名称
        :return:
        """

        uri = (
            "/api/cloud/cce-project-manager/v1.0/namespace/quota?clusterId="
            + cluster_id
            + "&namespaceName="
            + namespace
        )

        return self._get(uri=uri)

    def get_pvc_for_cluster(self, cluster_id, page=1, size=10, **kwargs):
        """
        查看集群pvc列表

        :param cluster_id: 集群ID
        :param page: 页码
        :param size: 数据量
        :param kwargs:
        :return:
        """
        uri = (
            f"/api/cloud/cce/v1.0/clusters/{cluster_id}/pvs?page={page}&pageSize={size}"
        )

        if kwargs:
            uri += "&" + urlencode(kwargs)

        return self._get(uri)

    def delete_pvc_for_cluster(self, cluster_id, name):
        """
        删除pvc

        :param cluster_id: 集群ID
        :param name: pvc名称
        :return:
        """
        uri = f"/api/cloud/cce/v1.0/clusters/{cluster_id}/pvs/{name}"
        return self._delete(uri)
