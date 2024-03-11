from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode
from config.config import settings


class MsgAPI(RestAPIBase):
    def get_msg_list(self, org_id, page=1, size=100, **kwargs):
        """
        获取微服务引擎列表

        :param org_id: 组织ID
        :param page: 页码
        :param size: 每一页数据量
        :return:
        """
        uri = f"/api/msg/springcloud/v1.0/clusters/all/environments?&orgId={org_id}&page={page}&size={size}"

        if kwargs:
            uri += "&" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_msg_sku_list(self, **kwargs):
        """获取引擎规格信息列表"""
        uri = "/api/msg/springcloud/v1.0/engine_frameworks"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_discovery_info(self, version):
        """
        获取注册中心信息

        :param version: 微服务引擎版本
        :param kwargs:
        :return:
        """
        uri = (
            f"/api/msg/springcloud/v1.0/components/version/discover-{version}/{version}"
        )
        response = self._get(uri=uri)
        return response

    def get_config_info(self, version, **kwargs):
        """
        获取配置中心信息

        :param version: 引擎版本
        :param kwargs:
        :return:
        """
        uri = (
            "/api/msg/springcloud/v1.0/components/version/config-"
            + version
            + "/"
            + version
        )
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_gateway_info(self, version, **kwargs):
        """
        获取网关信息

        :param version: 引擎版本
        :param kwargs:
        :return:
        """
        uri = (
            "/api/msg/springcloud/v1.0/components/version/gateway-"
            + version
            + "/"
            + version
        )
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def check_name(self, name, **kwargs):
        """
        重名校验

        :param name: 名称
        :param kwargs:
        :return:
        """
        uri = "/api/msg/svcgov/v1.0/engines/checkName/" + name
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_traces_services_list(self, **kwargs):
        """
        获取微服务引擎--链路追踪服务列表
        :return:
        """
        uri = "/api/cloud/app_mgmt/msg/v1.0/clusters/all/traces/services/all"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def create_micro_engine_with_springcloud(
        self,
        name,
        org_id,
        cluster,
        cluster_id,
        description,
        version,
        engineIp,
        components,
        midware,
        midware_type,
        component_type,
        **kwargs,
    ):
        """
        创建springcloud微服务引擎

        :param cluster_id: 集群ID
        :param orgId: 组织ID
        :param name: 引擎名称
        :param description: 微服务引擎描述
        :param version: 微服务引擎版本
        :param zone: 资源配置可用域名称
        :param zoneId: 资源配置可用域ID
        :param components: 列表.引擎组件中注册中心/配置中心/API网关的配置
        :param engineIp:
        :param midware_type:  default集群为0 cce集群为1
        :return:
        """
        uri = f"/api/msg/springcloud/v1.0/clusters/{cluster_id}/environments"
        post_data = {
            "orgId": org_id,
            "name": name,
            "description": description,
            "version": version,
            "engineIp": engineIp,
            "zone": cluster,
            "zoneId": cluster_id,
            "clusterType": 2,   # TODO：共享集群clusterType为1，需适配
            "engineType": "1",
            "middlewareCustomType": midware_type,
            "components": components,
            "middleWares": midware,
            "needApproval": False,
            "componentType": component_type,
        }

        response = self._post(uri=uri, json=post_data)
        return response

    def create_micro_engine_with_dubbo(
        self,
        org_id,
        name,
        cluster,
        cluster_id,
        description,
        engineIP,
        version,
        components,
        midware_type,
        midware,
        componentType,
    ):
        """新建dubbo类型的微服务引擎"""
        uri = "/api/msg/svcgov/v1.0/engines"
        data = {
            "orgId": org_id,
            "name": name,
            "description": description,
            "version": version,
            "engineIp": engineIP,
            "zone": cluster,
            "zoneId": cluster_id,
            "clusterType": 2,
            "engineType": 3,
            "middlewareCustomType": midware_type,
            "components": components,
            "middleWares": midware,
            "needApproval": False,
            "componentType": componentType,
            "clusterId": cluster_id,
        }
        return self._post(uri=uri, json=data)

    def query_micro_engine(self, **kwargs):
        """
        查询微服务引擎
        :param kwargs:
        :return:
        """
        uri = "/api/msg/springcloud/v1.0/clusters/all/environments"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def delete_springcloud_engine(self, cluster_id, id, **kwargs):
        uri = f"/api/msg/springcloud/v1.0/clusters/{cluster_id}/environment/{id}"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._delete(uri=uri)
        return response

    def delete_dubbo_engine(self, engine_id):
        uri = f"/api/msg/svcgov/v1.0/engines/{engine_id}"
        return self._delete(uri)

    def modify_msg_info(self, cluster_id, msg_id, name, engineIp, description):
        uri = f"/api/msg/springcloud/v1.0/clusters/{cluster_id}/environments"
        data = {
            "id": msg_id,
            "name": name,
            "engineIp": engineIp,
            "description": description,
        }
        return self._put(uri, data)

    def get_mse_component(self, mse_id):
        uri = f"/api/msg/springcloud/v1.0/components/{mse_id}"
        return self._get(uri)

    def get_mse_component_status(self, cluster_id, mse_id):
        uri = f"/api/msg/springcloud/v1.0/clusters/{cluster_id}/environments/{mse_id}/components"
        return self._get(uri)

    def update_mse_component_flavor(self, mse_id, data):
        uri = f"/api/msg/springcloud/v1.0/environments/{mse_id}/components"

        return self._put(uri, data)

    def add_mse_compoent(self, mse_id, data):
        uri = f"/api/msg/springcloud/v1.0/environments/{mse_id}/components"
        return self._post(uri, data)

    def create_config(self, mse_id, key, value):
        uri = f"/api/msg/springcloud/v1.0/mconfig/engine/{mse_id}"
        data = {
            "name": key,
            "envId": mse_id,
            "type": "native",
            "value": value,
            "application": "",
            "profile": "",
            "label": "",
        }
        return self._post(uri, data)

    def get_mse_configmap(self, mse_id):
        uri = f"/api/msg/springcloud/v1.0/mconfig/engine/{mse_id}"
        return self._get(uri)

    def update_configmap(self, mse_id, cm_id, cm_name, cm_value):
        uri = f"/api/msg/springcloud/v1.0/mconfig/engine/{mse_id}/{cm_id}"
        data = {
            "name": cm_name,
            "envId": mse_id,
            "type": "native",
            "value": cm_value,
            "application": "",
            "profile": "",
            "label": "",
            "id": int(cm_id),
        }
        return self._put(uri, data)

    def delete_configmap(self, mse_id, cm_id):
        uri = f"/api/msg/springcloud/v1.0/mconfig/engine/{mse_id}/{cm_id}"
        return self._delete(uri)

    def remove_mse_component(self, mse_id, component):
        uri = f"/api/msg/springcloud/v1.0/environments/{mse_id}/components/springcloud-gateway"
        return self._delete(uri)
