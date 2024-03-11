import allure

from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode


class GatewayAPI(RestAPIBase):

    def get_gw_list(self, page=1, size=10, name=None):
        """
        获取网关列表

        :param page: 页码
        :param size: 单页数据量
        :param name: 网关名称
        :return:
        """
        uri = f"/api/cloud/svcgw/v1.0/applications?page={str(page)}&size={str(size)}&name={name}"
        response = self._get(uri=uri)
        return response

    def get_available_pvs(self, cluster_id, cluster_vip, zone_id):
        """
        获取存储配置

        :param cluster_vip: 集群类型
        :param cluster_id: 集群ID
        :param zone_id: 可用域ID
        :return:
        """
        uri = "/api/cloud/svcgw/v1.0/available_pvs"

        data = {
            "clusterVip": cluster_vip,
            "clusterId": cluster_id,
            "zoneId": zone_id
        }

        response = self._post(uri=uri, json=data)
        return response

    def get_worker_node_list(self, cluster_id):
        """
        获取网关工作节点列表

        :param cluster_id: 集群ID
        :return:
        """
        uri = f"/api/cloud/svcgw/v1.0/kaas_clusters/{cluster_id}"
        response = self._get(uri=uri)
        return response

    def check_kong_port(self, business_ip, port, cluster_port, cluster_vip):
        """
        检查网关端口是否重复

        :param business_ip: 网关IP
        :param port: 网关端口
        :param cluster_port: 集群端口
        :param cluster_vip: 集群VIP
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/kaas_clusters/port/check"

        data = {
            "businessIp": business_ip,
            "clusterPort": cluster_port,
            "clusterVip": cluster_vip,
            "ip": business_ip.split("/")[0],
            "port": port
        }
        response = self._post(uri=uri, json=data)
        return response

    def check_instance_ip(self, kong_ip, http_port, https_port, instance_ip):
        """
        检查网关实例VIP是否重复

        :param kong_ip: 网关IP
        :param http_port: 网关HTTP端口
        :param https_port: 网关HTTPS端口
        :param instance_ip: 实例VIP
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/kaas_clusters/instance_ip/check"

        data = {
            "kongIp": kong_ip,
            "kongHttpProxyPort": http_port,
            "kongHttpsProxyPort": https_port,
            "instanceVipOpen": 1,
            "instanceVip": instance_ip
        }
        response = self._post(uri=uri, json=data)
        return response

    def check_gw_namespace(self, cluster_id, kong_ip, namespace, project_id, cpu, memory):
        """
        检查命名空间是否重复

        :param cluster_id: 集群ID
        :param kong_ip: 网关实例IP
        :param namespace: 命名空间
        :param project_id: 项目ID
        :param cpu: 请求规格
        :param memory: 请求规格
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/pcr/check/namespace"

        data = {
            "clusterId": cluster_id,
            "cpu": cpu,
            "kongIp": kong_ip,
            "memory": memory,
            "namespaceName": namespace,
            "projectId": project_id
        }
        response = self._post(uri=uri, json=data)
        return response

    def create_gateway(self, gw_name, kong_ip, http_port, https_port, resource, cluster_id, cluster_port, cluster_vip,
                       data_volume, cluster_type="PRIVATE_KAAS", open_service="0", service_version="1.0",
                       resource_type="CONTAINER", approval="disable", is_static=False, **kwargs):
        """
        创建服务网关

        :param gw_name: 网关实例名称
        :param kong_ip: 网关IP
        :param http_port: 服务HTTP端口
        :param https_port: 服务HTTPS端口
        :param resource: 容器规格
        :param cluster_id: 集群ID
        :param cluster_port: 集群端口
        :param cluster_vip: 集群VIP
        :param cluster_type: 集群类型
        :param data_volume: 数据盘大小。如，5Gi
        :param open_service: 私有实例（0）/ 共享实例（1）
        :param service_version: 版本
        :param resource_type: 资源类型
        :param approval: 服务发布审批
        :param is_static: 静态/动态供给
        :param kwargs:
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/applications"

        data = {
            "name": gw_name,
            "description": kwargs['description'] if "description" in kwargs.keys() else "",
            "serviceType": "svcgw",
            "serviceVersion": service_version,
            "openService": open_service,
            "approval": approval,
            "kongAddr": [{
                "kongIp": kong_ip,
                "kongHttpProxyPort": http_port,
                "kongHttpsProxyPort": https_port,
            }],
            "resource": {
                "limits": {
                    "cpu": resource['cpu_limit'],
                    "memory": resource['mem_limit']
                },
                "requests": {
                    "cpu": resource['cpu_request'],
                    "memory": resource['mem_request']
                }
            },
            "dataVolume": data_volume,
            "isStatic": is_static,
            "resourceType": resource_type,
            "clusterId": cluster_id,
            "clusterVip": cluster_vip,
            "num": 1,
            "clusterType": cluster_type,
            "kongIp": kong_ip,
            "kongHttpProxyPort": str(http_port),
            "kongHttpsProxyPort": str(https_port),
            "clusterPort": cluster_port
        }

        if is_static:
            data['volumeName'] = kwargs['volume_name']
        else:
            data['storageClass'] = kwargs['storage_class']

        response = self._post(uri=uri, json=data)
        return response

    def delete_gateway(self, gw_id):
        """
        删除网关

        :param gw_id: 网关ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/applications/{gw_id}/delete"

        response = self._delete(uri=uri)
        return response

    def restart_gateway(self, gw_id):
        """
        重启网关

        :param gw_id: 网关ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/applications/{gw_id}/restart"

        response = self._post(uri=uri)
        return response

    def replicas_gateway(self, gw_id, kong_ip, http_port, https_port):
        """
        扩缩容网关容器实例数

        :param gw_id: 网关ID
        :param kong_ip: 实例IP
        :param http_port: HTTP端口
        :param https_port: HTTPS端口
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/applications/{gw_id}/replicas"

        data = {
            "kongIp": kong_ip,
            "kongHttpProxyPort": http_port,
            "kongHttpsProxyPort": https_port
        }

        response = self._post(uri=uri, json=data)
        return response

    def resize_gateway(self, gw_id, resource):
        """
        扩缩容网关容器规格

        :param gw_id: 网关ID
        :param resource: 容器规格
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/applications/{gw_id}/resize"

        data = {
            "limits": {
                "cpu": resource['cpu_limit'],
                "memory": resource['mem_limit']
            },
            "requests": {
                "cpu": resource['cpu_request'],
                "memory": resource['mem_request']
            }
        }

        response = self._post(uri=uri, json=data)
        return response

    def update_gateway(self, gw_id):
        """
        升级服务网关

        :param gw_id: 服务网关ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/applications/{gw_id}/update"

        response = self._post(uri=uri)
        return response

    def get_api_groups(self, gw_ip, page=1, size=10, name=None):
        """
        获取接口组列表

        :param gw_ip: 服务网关实例名称
        :param page: 页码
        :param size: 单页数据量
        :param name: 接口组名称
        :return:
        """
        uri = f"/api/cloud/svcgw/v1.0/apimgt/apigroups?page={str(page)}&size={str(size)}&name={name}"

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def check_api_group_name(self, name, project_id, gw_ip):
        """
        检查网关端口是否重复

        :param name: 接口组名称
        :param project_id: 项目ID
        :param gw_ip: 服务网关实例名称
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/apigroups/name/check"

        header = {
            "gatewayip": gw_ip
        }

        data = {
            "name": name,
            "projectId": project_id
        }
        response = self._post(uri=uri, json=data, headers=header)
        return response

    def create_api_group(self, name, gw_ip, id="", description="", **kwargs):
        """
        创建接口组

        :param name: 接口组名称
        :param gw_ip: 服务网关实例名称
        :param id:
        :param description:
        :param kwargs:如，enable_add_log: 是否记录接口日志（True/ False）
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/apigroups"

        data = {
            "description": description,
            "id": id,
            "name": name
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, json=data, headers=header)
        return response

    def delete_api_group(self, gw_ip, api_group_id):
        """
        删除接口分组

        :param api_group_id: 接口分组ID
        :param gw_ip: 服务网关实例名称
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apigroups/{api_group_id}/delete"

        header = {
            "gatewayip": gw_ip
        }

        response = self._delete(uri=uri, headers=header)
        return response

    def check_api_name(self, name, group_id, gw_ip):
        """
        检查API是否重名

        :param name: 接口名称
        :param group_id: 接口分组名称
        :param gw_ip: 接口分组的实例IP
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/apis/name/check"

        data = {
            "name": name,
            "groupId": group_id
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, json=data, headers=header)
        return response

    def check_uri_param(self, method, path, gw_ip):
        """
        检查API是否重名

        :param method: 请求方法
        :param path: 请求path
        :param gw_ip: 接口分组的实例IP
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/check/urlParams"

        data = {
            "method": method,
            "path": path
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, json=data, headers=header)
        return response

    def get_flow_control(self, gw_ip, page=1, size=10):
        """
        获取流控策略

        :param gw_ip: 接口分组的实例IP
        :param page:
        :param size:
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/flow-control?page={page}&size={size}"

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def get_access_policy(self, gw_ip, page=1, size=10):
        """
        获取访问策略

        :param gw_ip: 接口分组的实例IP
        :param page:
        :param size:
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access?page={page}&size={size}"

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header)
        return response

    def create_apis(self, gw_ip, api_group_name, api_group_id, api_name, svc_params, kong_params, **kwargs):
        """
        创建接口

        :param api_name: 接口组名称
        :param api_group_name: 接口组名称
        :param api_group_id: 接口组名称
        :param gw_ip: 服务网关实例名称
        :param svc_params: 后端服务的信息
        :param kong_params: 接口信息
        :param kwargs:如，enable_add_log: 是否记录接口日志（True/ False）
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/apis"

        data = {
            "groupId": api_group_id,
            "groupName": api_group_name,
            "name": api_name,
            "authPolicy": kwargs['auth_policy'] if 'auth_policy' in kwargs.keys() else None,
            "accessPolicy": kwargs['access_policy'] if 'access_policy' in kwargs.keys() else None,
            "flowControlPolicy": kwargs['flow_control_policy'] if 'flow_control_policy' in kwargs.keys() else None,
            "description": kwargs['description'] if 'description' in kwargs.keys() else "",
            "kongProtocol": kong_params['kong_protocol'],
            "path": kong_params['kong_path'],
            "kongMethod": kong_params['kong_method'],
            "apiType": "REST",
            "regex": 0,
            "paramModel": "mapping",
            "svcProtocol": svc_params['svc_protocol'],
            "wsdlUrl": "",
            "namespace": "",
            "endpoint": "",
            "binding": "",
            "soapAction": "",
            "operation": "",
            "svcMethod": svc_params['svc_method'],
            "svcPath": svc_params['svc_path'],
            "serviceList": svc_params['services'],
            "algorithm": "round-robin",
            "hashOn": kwargs['hash_on'] if 'hash_on' in kwargs.keys() else "none",
            "hashOnHeader": kwargs['hash_on_header'] if 'hash_on_header' in kwargs.keys() else "",
            "hashOnCookie": kwargs['hash_on_cookie'] if 'hash_on_cookie' in kwargs.keys() else None,
            "hashOnCookiePath": kwargs['hash_on_cookie_path'] if 'hash_on_cookie_path' in kwargs.keys() else None,
            "retries": svc_params['retries'] if 'retries' in svc_params.keys() else 5,
            "connectTimeout": svc_params['connect_timeout'] if 'connect_timeout' in svc_params.keys() else 60000,
            "apiVersion": svc_params['api_version'] if 'api_version' in svc_params.keys() else "v1",
            "versionDescription": kwargs['version_description'] if 'version_description' in kwargs.keys() else "",
            "enableStripPathPrefix": kwargs[
                'enable_strip_path_prefix'] if 'enable_strip_path_prefix' in kwargs.keys() else False,
            "upstreamHealthChecks": {
                "enable": kwargs['upstream_health_checks'][
                    'enable'] if 'upstream_health_checks' in kwargs.keys() else False,
                "interval": kwargs['upstream_health_checks'][
                    'interval'] if 'upstream_health_checks' in kwargs.keys() else 45,
                "timeout": kwargs['upstream_health_checks'][
                    'timeout'] if 'upstream_health_checks' in kwargs.keys() else 3,
                "failureThreshold": kwargs['upstream_health_checks'][
                    'failure_threshold'] if 'upstream_health_checks' in kwargs.keys() else 3,
                "successThreshold": kwargs['upstream_health_checks'][
                    'success_threshold'] if 'upstream_health_checks' in kwargs.keys() else 3,
            },
            "enablePreserveHost": kwargs['enable_preserve_host'] if 'enable_preserve_host' in kwargs.keys() else False,
            "enableCORS": kwargs['enable_cors'] if 'enable_cors' in kwargs.keys() else False
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, json=data, headers=header)
        return response

    def get_apis_list(self, gw_ip, page=1, size=10, **kwargs):
        """
        接口列表，含搜索

        :param gw_ip: 接口分组的实例IP
        :param page:
        :param size:
        :param kwargs: 如，
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?page={page}&size={size}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def get_apis_detail(self, gw_ip, api_id):
        """
        接口详情

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis/{api_id}"

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def delete_apis(self, gw_ip, api_id):
        """
        删除接口

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis/{api_id}/delete"

        header = {
            "gatewayip": gw_ip
        }

        response = self._delete(uri=uri, headers=header)
        return response

    def offline_apis(self, gw_ip, api_id):
        """
        下线接口

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis/{api_id}/offline"

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header)
        return response

    def online_apis(self, gw_ip, api_id):
        """
        上线接口

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis/{api_id}/online"

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header)
        return response

    def get_apis_version(self, gw_ip, api_id, page=1, size=10, **kwargs):
        """
        获取接口版本信息

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :param page: 接口ID
        :param size: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis/{api_id}/versions?page={page}&size={size}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def check_apis_version(self, gw_ip, api_id, version):
        """
        校验接口版本名称

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :param version: 接口版本名称
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/apis/versions/check"

        data = {
            "apiId": api_id,
            "apiVersion": version
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def create_apis_version(self, gw_ip, api_id, version, service_list, **kwargs):
        """
        创建接口版本

        :param gw_ip: 接口分组的实例IP
        :param api_id: 接口ID
        :param version: 接口版本名称
        :param service_list: 后端服务地址集合
        :param kwargs: 例如："items_header": [["k1:v1"]]
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/apis/versions"

        data = {
            "apiId": api_id,
            "apiVersion": version,
            "versionDescription": "",
            "serviceList": service_list,
            "algorithm": "round-robin",
            "hashOn": "none",
            "enableCustom": True,
            "upstreamHealthChecks": {
                "enable": False,
                "interval": 45,
                "timeout": 3,
                "failureThreshold": 3,
                "successThreshold": 3
            },
        }

        if 'items_header' in kwargs.keys():
            data["itemsHeader"] = kwargs['items_header']

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def check_proxy_cache(self, gw_ip, name):
        """
        校验代理缓存策略名称

        :param gw_ip: 接口分组的实例IP
        :param name: 代理缓存策略名称
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/proxy-cache/check"

        data = {
            "name": name
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_proxy_caches_list(self, gw_ip, page=1, size=10, **kwargs):
        """
        获取代理缓存策略

        :param gw_ip: 接口分组的实例IP
        :param page: 页码
        :param size: 数量
        :param kwargs: 例如，name=
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/proxy-cache?size={size}&page={page}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def get_proxy_caches_detail(self, gw_ip, proxy_cache_id, page=1, size=10, **kwargs):
        """
        获取代理缓存策略详情

        :param gw_ip: 接口分组的实例IP
        :param proxy_cache_id: 代理缓存策略ID
        :param page: 接口ID
        :param size: 接口ID
        :param kwargs:
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?page={page}&size={size}&proxyCachePolicy={proxy_cache_id}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def create_proxy_cache_policy(self, gw_ip, name, cache_ttl=300, response_code=[200, 301, 404], **kwargs):
        """
        创建代理缓存策略

        :param gw_ip: 接口分组的实例IP
        :param name: 代理缓存策略名称
        :param cache_ttl: 缓存TTL(s)
        :param response_code: 返回码
        :param kwargs: 例如，name=
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/proxy-cache"

        if kwargs:
            uri += '?' + urlencode(kwargs)

        data = {
            "name": name,
            "description": kwargs['description'] if 'description' in kwargs.keys() else "",
            "cacheTTL": cache_ttl,
            "responseCode": response_code,
            "contentType": [],
            "varyHeaders": [],
            "varyQueryParams": []
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def delete_proxy_cache_policy(self, gw_ip, proxy_cache_ids):
        """
        删除代理缓存策略

        :param gw_ip: 接口分组的实例IP
        :param proxy_cache_ids: 代理缓存策略ID列表
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/proxy-cache/batch/delete"

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=proxy_cache_ids)
        return response

    def get_unbound_proxy_cache_apis(self, gw_ip, except_proxy_cache="undefined", page=1, size=10, **kwargs):
        """
        获取代理缓存策略未绑定的接口

        :param gw_ip: 接口分组的实例IP
        :param except_proxy_cache: 缓存策略
        :param page: 页码
        :param size: 数量
        :param kwargs: 例如，queryName=, groupId=
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?exceptProxyCache={except_proxy_cache}&page={page}&size={size}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def bind_apis_with_proxy_cache(self, gw_ip, proxy_cache_id, api_ids):
        """
        代理缓存策略绑定接口

        :param gw_ip: 接口分组的实例IP
        :param proxy_cache_id: 代理缓存策略ID
        :param api_ids: 接口ID列表
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/proxy-cache/{proxy_cache_id}/binding/api/list"

        data = api_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def unbind_apis_with_proxy_cache(self, gw_ip, proxy_cache_id, api_ids):
        """
        代理缓存策略解绑接口

        :param gw_ip: 接口分组的实例IP
        :param proxy_cache_id: 代理缓存策略ID
        :param api_ids: 接口ID列表
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/proxy-cache/{proxy_cache_id}/unbind/api/list"

        data = api_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def check_flow_control(self, gw_ip, name, project_id):
        """
        校验流控策略名称

        :param gw_ip: 接口分组的实例IP
        :param name: 流控策略名称
        :param project_id: 项目ID
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/flow-control/name/check"

        data = {
            "name": name,
            "projectId": project_id
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_flow_controls_list(self, gw_ip, page=1, size=10, name=None):
        """
        获取流控策略列表

        :param gw_ip: 接口分组的实例IP
        :param page: 页码
        :param size: 数量
        :param name: 流控策略名称
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/flow-control?&page={page}&size={size}&name={name}"

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def create_flow_control(self, gw_ip, name, limit_by, per_sec, per_min, per_hour, per_day, config_type="BaseConfig",
                            **kwargs):
        """
        创建流控策略

        :param gw_ip: 接口分组的实例IP
        :param name: 流控策略名称
        :param limit_by: 限流模式。例如，按接口（service）/ 按项目（project）/按凭证（consumer）/按IP（ip）
        :param per_day: 每天请求数
        :param per_hour: 每小时请求数
        :param per_min: 每分钟请求数
        :param per_sec: 每秒请求数
        :param config_type: 配置类型（基础配置/ 自定义配置）
        :param kwargs:
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/flow-control"

        if kwargs:
            uri += '?' + urlencode(kwargs)

        data = {
            "config": None,
            "description": kwargs['description'] if 'description' in kwargs.keys() else "",
            "limitBy": limit_by,
            "name": name,
            "perDay": per_day,
            "perHour": per_hour,
            "perMinute": per_min,
            "perSecond": per_sec,
            "type": config_type
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_flow_control_detail(self, gw_ip, flow_control_id, page=1, size=10, **kwargs):
        """
        获取流控策略详情

        :param gw_ip: 接口分组的实例IP
        :param flow_control_id: 流控策略ID
        :param page: 接口ID
        :param size: 接口ID
        :param kwargs:
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?page={page}&size={size}&flowControlPolicy={flow_control_id}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def delete_flow_control(self, gw_ip, flow_control_id):
        """
        删除单个流控策略

        :param gw_ip: 接口分组的实例IP
        :param flow_control_id: 流控策略ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/flow-control/{flow_control_id}/delete"

        header = {
            "gatewayip": gw_ip
        }

        response = self._delete(uri=uri, headers=header)
        return response

    def batch_delete_flow_controls(self, gw_ip, flow_control_ids):
        """
        批量删除流控策略

        :param gw_ip: 接口分组的实例IP
        :param flow_control_ids: 流控策略ID
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/flow-control/batch/delete"

        data = flow_control_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_unbound_flow_control_apis(self, gw_ip, except_policy="flowControlPolicy", page=1, size=10, **kwargs):
        """
        获取流控策略未绑定的接口

        :param gw_ip: 接口分组的实例IP
        :param except_policy: 流控策略
        :param page: 页码
        :param size: 数量
        :param kwargs: 例如，queryName=, groupId=
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?page={page}&size={size}&exceptPolicy={except_policy}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def bind_apis_with_flow_control(self, gw_ip, flow_control_id, api_ids):
        """
        流控策略绑定接口

        :param gw_ip: 接口分组的实例IP
        :param flow_control_id: 流控策略ID
        :param api_ids: 接口ID列表
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/flow-control/{flow_control_id}/binding/list"

        data = api_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def unbind_api_with_flow_control(self, gw_ip, flow_control_id, api_id):
        """
        流控策略解绑单个接口

        :param gw_ip: 接口分组的实例IP
        :param flow_control_id: 流控策略ID
        :param api_id: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/flow-control/{flow_control_id}/unbind/{api_id}/api"

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header)
        return response

    def batch_unbind_api_with_flow_control(self, gw_ip, flow_control_id, api_ids):
        """
        流控策略批量解绑接口

        :param gw_ip: 接口分组的实例IP
        :param flow_control_id: 流控策略ID
        :param api_ids: 接口ID列表
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/flow-control/{flow_control_id}/unbind/list"

        data = api_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def check_access_control(self, gw_ip, name, project_id):
        """
        校验安全控制策略名称

        :param gw_ip: 接口分组的实例IP
        :param name: 安全控制策略名称
        :param project_id: 项目ID
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/access/name/check"

        data = {
            "name": name,
            "projectId": project_id
        }

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_access_controls_list(self, gw_ip, page=1, size=10, name=None):
        """
        获取安全控制策略列表

        :param gw_ip: 接口分组的实例IP
        :param page: 页码
        :param size: 数量
        :param name: 安全控制策略名称
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access?&page={page}&size={size}&name={name}"

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def create_access_control(self, gw_ip, name, limit_type, action="ALLOW", ip_address="", **kwargs):
        """
        创建安全控制策略

        :param gw_ip: 接口分组的实例IP
        :param name: 安全控制策略名称
        :param limit_type: 限制类型。如， IP/ rule
        :param action: 动作。如，ALLOW/ FORBID
        :param ip_address: IP地址
        :param kwargs:
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/access"

        data = {
            "name": name,
            "type": limit_type,
            "action": action,
            "ipAddress": ip_address,
        }

        if 'config' in kwargs.keys():
            data['config'] = kwargs['config']

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_access_control_detail(self, gw_ip, access_control_id):
        """
        获取安全控制策略详情

        :param gw_ip: 接口分组的实例IP
        :param access_control_id: 安全控制策略ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access/{access_control_id}/info"

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def get_apis_in_access_control_detail(self, gw_ip, access_control_id, page=1, size=10, **kwargs):
        """
        获取安全控制策略详情中绑定接口列表

        :param gw_ip: 接口分组的实例IP
        :param access_control_id: 安全控制策略ID
        :param page: 接口ID
        :param size: 接口ID
        :param kwargs:
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?page={page}&size={size}&accessPolicy={access_control_id}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def delete_access_control(self, gw_ip, access_control_id):
        """
        删除单个安全控制策略

        :param gw_ip: 接口分组的实例IP
        :param access_control_id: 安全控制策略ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access/{access_control_id}/delete"

        header = {
            "gatewayip": gw_ip
        }

        response = self._delete(uri=uri, headers=header)
        return response

    def batch_delete_access_controls(self, gw_ip, access_control_ids):
        """
        批量删除安全控制策略

        :param gw_ip: 接口分组的实例IP
        :param access_control_ids: 安全控制策略ID
        :return:
        """

        uri = "/api/cloud/svcgw/v1.0/apimgt/policy/access/batch/delete"

        data = access_control_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def get_unbound_access_control_apis(self, gw_ip, except_policy="accessPolicy", page=1, size=10, **kwargs):
        """
        获取安全控制策略未绑定的接口

        :param gw_ip: 接口分组的实例IP
        :param except_policy: 安全控制策略
        :param page: 页码
        :param size: 数量
        :param kwargs: 例如，queryName=, groupId=
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/apis?page={page}&size={size}&exceptPolicy={except_policy}"

        if kwargs:
            uri += '&' + urlencode(kwargs)

        header = {
            "gatewayip": gw_ip
        }

        response = self._get(uri=uri, headers=header)
        return response

    def bind_apis_with_access_control(self, gw_ip, access_control_id, api_ids):
        """
        安全控制策略绑定接口

        :param gw_ip: 接口分组的实例IP
        :param access_control_id: 安全控制策略ID
        :param api_ids: 接口ID列表
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access/{access_control_id}/binding/list"

        data = api_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response

    def unbind_api_with_access_control(self, gw_ip, access_control_id, api_id):
        """
        安全控制策略解绑单个接口

        :param gw_ip: 接口分组的实例IP
        :param access_control_id: 安全控制策略ID
        :param api_id: 接口ID
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access/{access_control_id}/unbind/{api_id}/api"

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header)
        return response

    def batch_unbind_api_with_access_control(self, gw_ip, access_control_id, api_ids):
        """
        安全控制策略批量解绑接口

        :param gw_ip: 接口分组的实例IP
        :param access_control_id: 安全控制策略ID
        :param api_ids: 接口ID列表
        :return:
        """

        uri = f"/api/cloud/svcgw/v1.0/apimgt/policy/access/{access_control_id}/unbind/list"

        data = api_ids

        header = {
            "gatewayip": gw_ip
        }

        response = self._post(uri=uri, headers=header, json=data)
        return response
