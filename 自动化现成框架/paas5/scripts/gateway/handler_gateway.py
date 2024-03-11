import allure

from resource.base.client import PAASClient
from resource.utils.common import *

# 响应成功时返回体中包含的字段
from scripts.app_mgmt.handler_app_mgmt import *
from scripts.cce.handler_cce import *
from scripts.sys.handler_sys import *

EXP_RESPONSE = {
    "code": "",
    "status": True
}


def get_gateway_api(url):
    """访问服务网关接口请求地址
    :params url:服务网关接口请求地址，如192.180.10.25:30088/apispza
    """
    sc = SSHConnection(settings['HOST'], "root", settings['PASSWORD'])
    sc.connect()
    message = sc.cmd("curl http://" + url)
    sc.close()
    return message


def get_gw_by_name(paas_client: PAASClient, name):
    """
    获取指定网关

    :param paas_client: 登录信息
    :param name: 网关名称
    :return:
    """

    with allure.step("get_gw_by_name()"):
        response = paas_client.gw_client.get_gw_list(name=name)
        check_status_code(response)
        check_response(EXP_RESPONSE, response.json())
        return response.json()


def get_worker_node(paas_client: PAASClient, index=0):
    """
    获取服务网关通过节点

    :param paas_client: 登录信息
    :param index: 工作节点标记
    :return:
    """

    with allure.step("get_worker_node()"):
        worker_nodes_resp = paas_client.gw_client.get_worker_node_list(settings['CLUSTER_ID'])
        check_status_code(worker_nodes_resp)
        worker_nodes = worker_nodes_resp.json()
        check_response(EXP_RESPONSE, worker_nodes)
        kong_ip = worker_nodes['data'][index]['businessIp']
        return kong_ip


def generate_kong_port(paas_client: PAASClient, business_ip, cluster_name):
    """
    生成网关服务端口

    :param paas_client: 登录信息
    :param business_ip: 网关IP
    :param cluster_name: 集群名称
    :return:
    """

    cluster_info = get_project_cluster_byname(paas_client, cluster_name)
    cluster_port = cluster_info['port']
    cluster_vip = cluster_info['businessVip']

    with allure.step("generate_kong_port()"):
        cnt = 1
        while cnt <= 5:
            kong_port = random.sample(range(1, 65535), 1)[0]
            check_kong_port_response = paas_client.gw_client.check_kong_port(business_ip, kong_port, cluster_port,
                                                                             cluster_vip)
            check_status_code(check_kong_port_response)
            check_kong_port = check_kong_port_response.json()
            check_response(EXP_RESPONSE, check_kong_port)
            if check_kong_port['data']:
                return kong_port
            cnt += 1
        assert cnt < 5, "5次随机生成端口均被占用"


def create_gateway(paas_client: PAASClient, gw_name, kong_ip, http_port, https_port, resource, cluster_name, data_volume,
                   cluster_type="PRIVATE_KAAS", open_service="0", service_version="1.0", resource_type="CONTAINER",
                   approval="disable", is_static=False, **kwargs):
    """
    创建服务网关

    :param paas_client: 登录信息
    :param gw_name: 网关实例名称
    :param kong_ip: 网关IP
    :param http_port: 服务HTTP端口
    :param https_port: 服务HTTPS端口
    :param resource: 容器规格
    :param cluster_name: 集群名称
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

    with allure.step("create_gateway()"):
        cluster_info = get_project_cluster_byname(paas_client, cluster_name)
        cluster_id = cluster_info['uuid']
        cluster_port = cluster_info['port']
        cluster_vip = cluster_info['vip']
        created_response = paas_client.gw_client.create_gateway(gw_name, kong_ip, http_port, https_port, resource,
                                                                cluster_id, cluster_port, cluster_vip, data_volume,
                                                                storage_class=kwargs['storage_class'])
        check_status_code(created_response)
        check_response(EXP_RESPONSE, created_response.json())


def delete_gateway(paas_client: PAASClient, gw_name):
    """
    删除服务网关

    :param paas_client: 登录信息
    :param gw_name: 网关实例名称
    :return:
    """
    with allure.step("delete_gateway()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关：{gw_name}"
        gw_id = gw_info['data'][0]['uuid']
        deleted_response = paas_client.gw_client.delete_gateway(gw_id)
        check_status_code(deleted_response)
        temp = 360
        cnt = 1
        while cnt <= temp:
            gw_info = get_gw_by_name(paas_client, gw_name)
            if len(gw_info['data']) == 0:
                break
            time.sleep(5)
            cnt = cnt + 1
        if cnt > temp:
            raise Exception(f"超时")


def restart_gateway(paas_client: PAASClient, gw_name):
    """
    重启服务网关

    :param paas_client: 登录信息
    :param gw_name: 网关实例名称
    :return:
    """
    with allure.step("restart_gateway()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关：{gw_name}"
        gw_id = gw_info['data'][0]['uuid']
        restarted_response = paas_client.gw_client.restart_gateway(gw_id)
        check_status_code(restarted_response)
        check_response(EXP_RESPONSE, restarted_response.json())
        exp_status = "RUNNING"
        exp_path = "$.data[0].status"
        check_status_timeout(exp_status, exp_path, get_gw_by_name, 1800, paas_client=paas_client, name=gw_name)


def resize_gateway(paas_client: PAASClient, gw_name, resource):
    """
    扩缩容服务网关容器规格

    :param paas_client: 登录信息
    :param gw_name: 网关实例名称
    :param resource: 容器规格
    :return:
    """
    with allure.step("resize_gateway()"):
        with allure.step("1. 扩缩容"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            assert len(gw_info['data']) > 0, f"未找到服务网关：{gw_name}"
            gw_id = gw_info['data'][0]['uuid']
            resized_response = paas_client.gw_client.resize_gateway(gw_id, resource)
            check_status_code(resized_response)
            check_response(EXP_RESPONSE, resized_response.json())
        with allure.step("2. 校验状态"):
            exp_status = "RUNNING"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_gw_by_name, 1800, paas_client=paas_client, name=gw_name)
            gw_info = get_gw_by_name(paas_client, gw_name)
        with allure.step("3. 校验扩缩容结果"):
            act_resource = gw_info['data'][0]['resource']
            exp_resource = "{\"limits\":{\"cpu\":\"" + resource['cpu_limit'] + "\",\"memory\":\"" + resource['mem_limit'] + "\"},\"requests\":{\"cpu\":\"" + resource['cpu_request'] + "\",\"memory\":\"" +resource['mem_request'] + "\"}}"
            assert act_resource == exp_resource, f"扩缩容失败。实际：{act_resource}，期望：{exp_resource}"


def replicas_gateway(paas_client: PAASClient, gw_name, business_ips, http_ports, https_ports):
    """
    扩缩容服务网关容器实例

    :param paas_client: 登录信息
    :param gw_name: 网关实例名称
    :param business_ips: 实例IP地址（至少1个，使用,分割）
    :param http_ports: HTTP端口（至少1个，使用,分割）
    :param https_ports: HTTPS端口（至少1个，使用,分割）
    :return:
    """
    with allure.step("replicas_gateway()"):
        with allure.step("1. 获取服务网关实例原有信息"):
            gw_info_res = get_gw_by_name(paas_client, gw_name)
            assert len(gw_info_res['data']) > 0, f"未找到服务网关：{gw_name}"
            gw_info = gw_info_res['data'][0]
            gw_id = gw_info['uuid']
        with allure.step("2. 扩缩容"):
            replicas_response = paas_client.gw_client.replicas_gateway(gw_id, business_ips, http_ports, https_ports)
            check_status_code(replicas_response)
            check_response(EXP_RESPONSE, replicas_response.json())
        with allure.step("3. 校验状态"):
            exp_status = "RUNNING"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_gw_by_name, 1800, paas_client=paas_client, name=gw_name)
            gw_info = get_gw_by_name(paas_client, gw_name)
        with allure.step("4. 校验扩缩容结果"):
            act_http_ports = gw_info['data'][0]['kongHttpProxyPort']
            act_https_ports = gw_info['data'][0]['kongHttpsProxyPort']
            act_kong_ips = gw_info['data'][0]['kongIp']
            assert act_kong_ips == business_ips, f"扩缩容失败。实际：{act_kong_ips}，期望：{business_ips}"
            assert act_http_ports == http_ports, f"扩缩容失败。实际：{act_http_ports}，期望：{http_ports}"
            assert act_https_ports == https_ports, f"扩缩容失败。实际：{act_https_ports}，期望：{https_ports}"


def update_gateway(paas_client: PAASClient, gw_name):
    """
    升级服务网关

    :param paas_client: 登录信息
    :param gw_name: 网关实例名称
    :return:
    """
    with allure.step("update_gateway()"):
        with allure.step("1. 搜索实例"):
            gw_info_res = get_gw_by_name(paas_client, gw_name)
            assert len(gw_info_res['data']) > 0, f"未找到服务网关：{gw_name}"
            gw_info = gw_info_res['data'][0]
            gw_id = gw_info['uuid']
        with allure.step("2. 升级"):  # 暂时不清楚这里为什么检查命名空间
            update_response = paas_client.gw_client.update_gateway(gw_id)
            check_status_code(update_response)
            check_response(EXP_RESPONSE, update_response.json())
        with allure.step("3. 检查结果"):
            temp = 360
            cnt = 1
            while cnt <= temp:
                gw_info = get_gw_by_name(paas_client, gw_name)
                if gw_info['data'][0]['status'] == "RUNNING":
                    break
                time.sleep(5)
                cnt = cnt + 1
            if cnt > temp:
                raise Exception(f"服务网关升级超过5min")


def setup_create_gateway(paas_client: PAASClient, gw_name, resource, kong_ip, storage_class, data_volume, **kwargs):
    """ 初始化：创建服务网关 """
    with allure.step("setup_create_gateway()"):
        cluster_name = kwargs['cluster_name'] if 'cluster_name' in kwargs.keys() else settings['CLUSTER_NAME']
        loop = 3
        while loop:
            http_port = generate_kong_port(paas_client, kong_ip, cluster_name=cluster_name)
            https_port = generate_kong_port(paas_client, kong_ip, cluster_name=cluster_name)
            if http_port == https_port:
                loop -= 1
            else:
                break
        assert loop > 0, "生成的HTTP和HTTPS端口3次均相同"
    with allure.step("1.创建服务网关"):
        create_gateway(paas_client, gw_name, kong_ip, http_port, https_port, resource, cluster_name, data_volume,
                       storage_class=storage_class)
    with allure.step("2.校验状态"):
        exp_status = "RUNNING"
        exp_path = "$.data[0].status"
        check_status_timeout(exp_status, exp_path, get_gw_by_name, 1800, paas_client=paas_client, name=gw_name)


def check_api_group_name(paas_client: PAASClient, gw_name, api_group_name):
    """ 校验接口管理组名称 """
    with allure.step("check_api_group_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        project_id = paas_client.login_info.default_project_id
        checked_response = paas_client.gw_client.check_api_group_name(api_group_name, project_id, gw_instance_name)
        check_status_code(checked_response)
        check_response(EXP_RESPONSE, checked_response.json())
        assert checked_response.json()['data'], f"已存在该接口组：{api_group_name}"


def get_api_group_by_name(paas_client: PAASClient, gw_name, api_group_name):
    """ 查询指定接口分组 """
    gw_info = get_gw_by_name(paas_client, gw_name)
    assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
    gw_instance_name = gw_info['data'][0]['svcApimgtName']
    api_groups_res = paas_client.gw_client.get_api_groups(gw_instance_name, 1,  500, api_group_name)
    check_status_code(api_groups_res)
    api_groups_info = api_groups_res.json()
    check_response(EXP_RESPONSE, api_groups_info)
    return api_groups_info


def create_api_group(paas_client: PAASClient, gw_name, api_group_name):
    """ 创建接口组 """
    with allure.step("create_api_group()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        created_response = paas_client.gw_client.create_api_group(api_group_name, gw_instance_name)
        check_status_code(created_response)
        check_response(EXP_RESPONSE, created_response.json())
        return created_response.json()


def delete_api_group(paas_client: PAASClient, gw_name, api_group_name):
    """ 删除指定接口分组 """
    with allure.step("delete_api_group()"):
        api_group = get_api_group_by_name(paas_client, gw_name, api_group_name)
        assert len(api_group['data']) > 0, f"未找到接口分组：{api_group_name}"
        api_group_id = api_group['data'][0]['id']
        gw_info = get_gw_by_name(paas_client, gw_name)
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        deleted_response = paas_client.gw_client.delete_api_group(gw_instance_name, api_group_id)
        check_status_code(deleted_response)
        check_response(EXP_RESPONSE, deleted_response.json())
        api_group = get_api_group_by_name(paas_client, gw_name, api_group_name)
        assert len(api_group['data']) == 0, f"未删除接口分组：{api_group_name}"


def create_apis(paas_client: PAASClient, gw_name, api_group_name, api_name, svc_params, kong_params, **kwargs):
    """ 创建接口 """
    with allure.step("create_apis()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        api_group_info = get_api_group_by_name(paas_client, gw_name, api_group_name)
        assert len(api_group_info['data']) > 0, f"未找到服务网关：{api_group_name}"
        api_group_id = api_group_info['data'][0]['id']
        created_response = paas_client.gw_client.create_apis(gw_instance_name, api_group_name, api_group_id, api_name,
                                                             svc_params, kong_params, **kwargs)
        check_status_code(created_response)
        check_response(EXP_RESPONSE, created_response.json())
        return created_response.json()


def get_apis_by_name(paas_client: PAASClient, gw_name, api_name=None):
    """ 搜索接口 """
    gw_info = get_gw_by_name(paas_client, gw_name)
    gw_instance_name = gw_info['data'][0]['svcApimgtName']
    api_info_response = paas_client.gw_client.get_apis_list(gw_instance_name, queryName=api_name)
    check_status_code(api_info_response)
    api_info = api_info_response.json()
    check_response(EXP_RESPONSE, api_info)
    return api_info


def get_apis_detail_by_name(paas_client: PAASClient, gw_name, api_name=None):
    """ 接口详情 """
    with allure.step("get_apis_detail_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        api_info_response = paas_client.gw_client.get_apis_list(gw_instance_name, queryName=api_name)
        check_status_code(api_info_response)
        api_info = api_info_response.json()
        check_response(EXP_RESPONSE, api_info)
        assert len(api_info['data']) > 0, f"未找到接口：{api_name}"
        api_id = api_info['data'][0]['id']
        api_detail_response = paas_client.gw_client.get_apis_detail(gw_instance_name, api_id)
        check_status_code(api_detail_response)
        api_detail = api_detail_response.json()
        check_response(EXP_RESPONSE, api_detail)
        return api_detail


def delete_api_by_name(paas_client: PAASClient, gw_name, api_name=None):
    """ 删除接口 """
    gw_info = get_gw_by_name(paas_client, gw_name)
    gw_instance_name = gw_info['data'][0]['svcApimgtName']
    api_info_response = paas_client.gw_client.get_apis_list(gw_instance_name, queryName=api_name)
    check_status_code(api_info_response)
    api_info = api_info_response.json()
    check_response(EXP_RESPONSE, api_info)
    assert len(api_info['data']) > 0, f"未找到接口：{api_name}"
    api_id = api_info['data'][0]['id']
    delete_api_response = paas_client.gw_client.delete_apis(gw_instance_name, api_id)
    check_status_code(delete_api_response)
    delete_api = delete_api_response.json()
    check_response(EXP_RESPONSE, delete_api)
    api_info_response = paas_client.gw_client.get_apis_list(gw_instance_name, queryName=api_name)
    api_info = api_info_response.json()
    assert len(api_info['data']) == 0, f"未删除接口：{api_name}"


def offline_apis_by_name(paas_client: PAASClient, gw_name, api_name):
    """ 下线接口 """
    api_detail = get_apis_detail_by_name(paas_client, gw_name, api_name)
    api_id = api_detail['data']['id']
    kong_url = api_detail['data']['kongUrl'][0]
    gw_info = get_gw_by_name(paas_client, gw_name)
    gw_instance_name = gw_info['data'][0]['svcApimgtName']
    offline_apis_response = paas_client.gw_client.offline_apis(gw_instance_name, api_id)
    check_status_code(offline_apis_response)
    offline_apis = offline_apis_response.json()
    check_response(EXP_RESPONSE, offline_apis)
    temp = 10
    cnt = 1
    while cnt <= temp:
        time.sleep(3)
        # response = requests.get("http://" + kong_url)
        message = get_gateway_api(kong_url)
        if message == '{"message":"The service already offline."}':
            break
        cnt += 1
    if cnt > temp:
        raise Exception(f"下线接口超时")


def online_apis_by_name(paas_client: PAASClient, gw_name, api_name, exp_msg):
    """ 上线接口 """
    api_detail = get_apis_detail_by_name(paas_client, gw_name, api_name)
    api_id = api_detail['data']['id']
    kong_url = api_detail['data']['kongUrl'][0]
    gw_info = get_gw_by_name(paas_client, gw_name)
    gw_instance_name = gw_info['data'][0]['svcApimgtName']
    online_apis_response = paas_client.gw_client.online_apis(gw_instance_name, api_id)
    check_status_code(online_apis_response)
    online_apis = online_apis_response.json()
    check_response(EXP_RESPONSE, online_apis)
    temp = 10
    cnt = 1
    while cnt <= temp:
        time.sleep(5)
        # response = requests.get("http://" + kong_url)
        message = get_gateway_api(kong_url)
        if message == exp_msg:
            break
        cnt += 1
    if cnt > temp:
        raise Exception(f"上线接口超时")


def create_proxy_cache(paas_client: PAASClient, gw_name, policy_name):
    """ 创建代理缓存策略 """
    with allure.step("create_proxy_cache()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        check_names_response = paas_client.gw_client.check_proxy_cache(gw_instance_name, policy_name)
        check_status_code(check_names_response)
        check_response(EXP_RESPONSE, check_names_response.json())
        assert check_names_response.json()['data'], f"已存在代理缓存策略：{policy_name}"
        created_response = paas_client.gw_client.create_proxy_cache_policy(gw_instance_name, policy_name)
        check_status_code(created_response)
        check_response(EXP_RESPONSE, created_response.json())


def delete_proxy_cache(paas_client: PAASClient, gw_name, policy_name):
    """ 删除代理缓存策略 """
    with allure.step("delete_proxy_cache()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        proxy_caches_info = get_proxy_cache_by_name(paas_client, gw_name, policy_name)
        assert len(proxy_caches_info['data']) > 0, f"未找到代理缓存策略：{policy_name}"
        proxy_caches_ids = []
        for proxy_cache_info in proxy_caches_info['data']:
            proxy_caches_ids.append(proxy_cache_info['id'])
        deleted_response = paas_client.gw_client.delete_proxy_cache_policy(gw_instance_name, proxy_caches_ids)
        check_status_code(deleted_response)
        check_response(EXP_RESPONSE, deleted_response.json())
        proxy_caches_info = get_proxy_cache_by_name(paas_client, gw_name, policy_name)
        assert len(proxy_caches_info['data']) == 0, f"未删除代理缓存策略：{policy_name}"


def get_proxy_cache_by_name(paas_client: PAASClient, gw_name, policy_name):
    """ 根据名称查询代理缓存策略 """
    with allure.step("get_proxy_cache_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        proxy_cache_response = paas_client.gw_client.get_proxy_caches_list(gw_instance_name, page=1, size=500,
                                                                           name=policy_name)
        check_status_code(proxy_cache_response)
        proxy_caches_info = proxy_cache_response.json()
        check_response(EXP_RESPONSE, proxy_caches_info)
        return proxy_caches_info


def create_apis_version(paas_client: PAASClient, gw_name, api_name, version, service_list, **kwargs):
    """ 创建接口版本 """
    with allure.step("create_apis_version()"):
        with allure.step("1.重名校验"):
            api_detail = get_apis_detail_by_name(paas_client, gw_name, api_name)
            api_id = api_detail['data']['id']
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            check_version_res = paas_client.gw_client.check_apis_version(gw_instance_name, api_id, version)
            check_status_code(check_version_res)
            check_version = check_version_res.json()
            check_response(EXP_RESPONSE, check_version)
            assert check_version['data'], f"接口{api_name}已有版本{version}"
        with allure.step("2.创建版本"):
            create_api_res = paas_client.gw_client.create_apis_version(gw_instance_name, api_id, version, service_list,
                                                                       **kwargs)
            check_status_code(create_api_res)
            check_response(EXP_RESPONSE, create_api_res.json())


def get_apis_version_by_name(paas_client: PAASClient, gw_name, api_name, version):
    """ 根据名称查询接口版本 """
    with allure.step("get_apis_version_by_name()"):
        api_detail = get_apis_detail_by_name(paas_client, gw_name, api_name)
        api_id = api_detail['data']['id']
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        apis_version_response = paas_client.gw_client.get_apis_version(gw_instance_name, api_id, page=1, size=500)
        check_status_code(apis_version_response)
        check_response(EXP_RESPONSE, apis_version_response.json())
        exp_version = f"$.data[?(@.apiVersion=='{version}')]"
        apis_version = get_value_from_json(apis_version_response, exp_version, list_flag=False)
        assert apis_version, f"未找到{api_name}的版本{version}"
        return apis_version


def get_unbound_apis_with_proxy_cache_by_name(paas_client: PAASClient, gw_name, api_name, api_group_name=None):
    """ 查询未绑定接口 """
    with allure.step("get_unbound_apis_with_proxy_cache_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        if api_group_name:
            api_group_info = get_api_group_by_name(paas_client, gw_name, api_group_name)
            assert len(api_group_info['data']) > 0, f"未找到网关{gw_name}下的接口组：{api_group_name}"
            api_group_id = api_group_info['data'][0]['id']
            unbound_apis_response = paas_client.gw_client.get_unbound_proxy_cache_apis(gw_instance_name, page=1, size=500,
                                                                                       queryName=api_name, groupId=api_group_id)
        else:
            unbound_apis_response = paas_client.gw_client.get_unbound_proxy_cache_apis(gw_instance_name, page=1, size=500,
                                                                                       queryName=api_name)
        check_status_code(unbound_apis_response)
        unbound_apis = unbound_apis_response.json()
        check_response(EXP_RESPONSE, unbound_apis)
        return unbound_apis


def bind_apis_with_proxy_cache(paas_client: PAASClient, gw_name, proxy_cache_name, api_name, api_group_name=None):
    """ 代理缓存策略绑定接口 """
    with allure.step("bind_apis_with_proxy_cache()"):
        with allure.step("1.查询代理缓存策略"):
            proxy_cache_info = get_proxy_cache_by_name(paas_client, gw_name, proxy_cache_name)
            assert len(proxy_cache_info['data']) > 0, f"未找到网关{gw_name}下的代理缓存策略：{proxy_cache_name}"
            proxy_cache_id = proxy_cache_info['data'][0]['id']
        with allure.step("2.查询未绑定接口"):
            unbound_apis = get_unbound_apis_with_proxy_cache_by_name(paas_client, gw_name, api_name, api_group_name)
            assert len(unbound_apis['data']) > 0, f"未找到网关：{gw_name}下的接口组：{api_group_name}"
            exp_unbound_api = f"$.data[?(@.name=='{api_name}')]"
            apis_info = jsonpath.jsonpath(unbound_apis, exp_unbound_api)
            assert apis_info, f"未找到网关：{gw_name}下的接口组：{api_group_name}存在未绑定的接口：{api_name}"
        with allure.step("3.绑定接口"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            api_ids = []
            for api in apis_info:
                api_ids.append(api['id'])
            binding_response = paas_client.gw_client.bind_apis_with_proxy_cache(gw_instance_name, proxy_cache_id, api_ids)
            check_status_code(binding_response)
            check_response(EXP_RESPONSE, binding_response.json())
        with allure.step("4.绑定接口出现在代理缓存详情列表中"):
            temp = 10
            cnt = 1
            while cnt < temp:
                time.sleep(3)
                proxy_cache_detail_res = paas_client.gw_client.get_proxy_caches_detail(gw_instance_name, proxy_cache_id,
                                                                                       queryName=api_name)
                check_status_code(proxy_cache_detail_res)
                if len(proxy_cache_detail_res.json()['data']) > 0:
                    break
                cnt += 1
            if cnt > temp:
                raise Exception(f"未成功绑定接口：{api_name}")
            proxy_cache_detail = proxy_cache_detail_res.json()
            check_response(EXP_RESPONSE, proxy_cache_detail)


def unbind_apis_with_proxy_cache(paas_client: PAASClient, gw_name, proxy_cache_name, api_name, api_group_name=None):
    """ 代理缓存策略解绑接口 """
    with allure.step("unbind_apis_with_proxy_cache()"):
        with allure.step("1.查询代理缓存策略详情"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            proxy_cache_info = get_proxy_cache_by_name(paas_client, gw_name, proxy_cache_name)
            assert len(proxy_cache_info['data']) > 0, f"未找到网关{gw_name}下的代理缓存策略：{proxy_cache_name}"
            proxy_cache_id = proxy_cache_info['data'][0]['id']
            proxy_cache_detail_res = paas_client.gw_client.get_proxy_caches_detail(gw_instance_name, proxy_cache_id,
                                                                                   queryName=api_name)
            check_status_code(proxy_cache_detail_res)
            proxy_cache_detail = proxy_cache_detail_res.json()
            check_response(EXP_RESPONSE, proxy_cache_detail)
            assert len(proxy_cache_detail['data']) > 0, f"无绑定接口：{api_name}"
        with allure.step("2.解绑接口"):
            api_ids = []
            for api in proxy_cache_detail['data']:
                api_ids.append(api['id'])
            unbind_response = paas_client.gw_client.unbind_apis_with_proxy_cache(gw_instance_name, proxy_cache_id, api_ids)
            check_status_code(unbind_response)
            check_response(EXP_RESPONSE, unbind_response.json())
        with allure.step("3.绑定接口不再出现在代理缓存详情列表中"):
            proxy_cache_detail_res = paas_client.gw_client.get_proxy_caches_detail(gw_instance_name, proxy_cache_id,
                                                                                   queryName=api_name)
            check_status_code(proxy_cache_detail_res)
            proxy_cache_detail = proxy_cache_detail_res.json()
            check_response(EXP_RESPONSE, proxy_cache_detail)
            assert len(proxy_cache_detail['data']) == 0, f"未成功解绑接口：{api_name}"


def create_flow_control(paas_client: PAASClient, gw_name, policy_name, limit_by, per_sec, per_min, per_hour, per_day,
                        **kwargs):
    """ 创建流控策略 """
    with allure.step("create_flow_control()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        project_id = paas_client.login_info.default_project_id
        check_names_response = paas_client.gw_client.check_flow_control(gw_instance_name, policy_name, project_id)
        check_status_code(check_names_response)
        check_response(EXP_RESPONSE, check_names_response.json())
        assert check_names_response.json()['data'], f"已存在流控策略：{policy_name}"
        created_response = paas_client.gw_client.create_flow_control(gw_instance_name, policy_name, limit_by, per_sec,
                                                                     per_min, per_hour, per_day, **kwargs)
        check_status_code(created_response)
        check_response(EXP_RESPONSE, created_response.json())


def delete_flow_control(paas_client: PAASClient, gw_name, policy_name):
    """ 删除流控策略 """
    with allure.step("delete_flow_control()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        flow_controls_info = get_flow_control_by_name(paas_client, gw_name, policy_name)
        assert len(flow_controls_info['data']) > 0, f"未找到流控策略：{policy_name}"
        flow_control_ids = []
        for flow_control_info in flow_controls_info['data']:
            flow_control_ids.append(flow_control_info['id'])
        if len(flow_control_ids) == 1:
            deleted_response = paas_client.gw_client.delete_flow_control(gw_instance_name, flow_control_ids[0])
        else:
            deleted_response = paas_client.gw_client.batch_delete_flow_controls(gw_instance_name, flow_control_ids)
        check_status_code(deleted_response)
        check_response(EXP_RESPONSE, deleted_response.json())
        flow_controls_info = get_flow_control_by_name(paas_client, gw_name, policy_name)
        assert len(flow_controls_info['data']) == 0, f"未删除流控策略：{policy_name}"


def get_flow_control_by_name(paas_client: PAASClient, gw_name, policy_name):
    """ 根据名称查询流控策略 """
    with allure.step("get_flow_control_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        flow_control_response = paas_client.gw_client.get_flow_controls_list(gw_instance_name, page=1, size=500,
                                                                             name=policy_name)
        check_status_code(flow_control_response)
        flow_control_info = flow_control_response.json()
        check_response(EXP_RESPONSE, flow_control_info)
        return flow_control_info


def get_unbound_apis_with_flow_control_by_name(paas_client: PAASClient, gw_name, api_name, api_group_name=None):
    """ 查询流控策略未绑定接口 """
    with allure.step("get_unbound_apis_with_flow_control_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        if api_group_name:
            api_group_info = get_api_group_by_name(paas_client, gw_name, api_group_name)
            assert len(api_group_info['data']) > 0, f"未找到网关{gw_name}下的接口组：{api_group_name}"
            api_group_id = api_group_info['data'][0]['id']
            unbound_apis_response = paas_client.gw_client.get_unbound_flow_control_apis(gw_instance_name, page=1,
                                                                                        size=500, queryName=api_name,
                                                                                        groupId=api_group_id)
        else:
            unbound_apis_response = paas_client.gw_client.get_unbound_flow_control_apis(gw_instance_name, page=1,
                                                                                        size=500, queryName=api_name)
        check_status_code(unbound_apis_response)
        unbound_apis = unbound_apis_response.json()
        check_response(EXP_RESPONSE, unbound_apis)
        return unbound_apis


def bind_apis_with_flow_control(paas_client: PAASClient, gw_name, flow_control_name, api_name, api_group_name=None):
    """ 流控策略绑定接口 """
    with allure.step("bind_apis_with_flow_control()"):
        with allure.step("1.查询流控策略"):
            flow_control_info = get_flow_control_by_name(paas_client, gw_name, flow_control_name)
            assert len(flow_control_info['data']) > 0, f"未找到网关{gw_name}下的代理缓存策略：{flow_control_name}"
            flow_control_id = flow_control_info['data'][0]['id']
        with allure.step("2.查询未绑定接口"):
            unbound_apis = get_unbound_apis_with_flow_control_by_name(paas_client, gw_name, api_name, api_group_name)
            assert len(unbound_apis['data']) > 0, f"未找到网关：{gw_name}下的接口组：{api_group_name}"
            exp_unbound_api = f"$.data[?(@.name=='{api_name}')]"
            apis_info = jsonpath.jsonpath(unbound_apis, exp_unbound_api)
            assert apis_info, f"未找到网关：{gw_name}下的接口组：{api_group_name}存在未绑定的接口：{api_name}"
        with allure.step("3.绑定接口"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            api_ids = []
            for api in apis_info:
                api_ids.append(api['id'])
            binding_response = paas_client.gw_client.bind_apis_with_flow_control(gw_instance_name, flow_control_id,
                                                                                 api_ids)
            check_status_code(binding_response)
            check_response(EXP_RESPONSE, binding_response.json())
        with allure.step("4.绑定接口出现在代理缓存详情列表中"):
            temp = 10
            cnt = 1
            while cnt < temp:
                time.sleep(3)
                flow_control_detail_res = paas_client.gw_client.get_flow_control_detail(gw_instance_name,
                                                                                        flow_control_id,
                                                                                        queryName=api_name)
                check_status_code(flow_control_detail_res)
                if len(flow_control_detail_res.json()['data']) > 0:
                    break
                cnt += 1
            if cnt > temp:
                raise Exception(f"未成功绑定接口：{api_name}")

            flow_control_detail = flow_control_detail_res.json()
            check_response(EXP_RESPONSE, flow_control_detail)


def unbind_apis_with_flow_control(paas_client: PAASClient, gw_name, flow_control_name, api_name, api_group_name=None):
    """ 流控策略解绑接口 """
    with allure.step("unbind_apis_with_flow_control()"):
        with allure.step("1.查询流控策略详情"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            flow_control_info = get_flow_control_by_name(paas_client, gw_name, flow_control_name)
            assert len(flow_control_info['data']) > 0, f"未找到网关{gw_name}下的流控策略：{flow_control_name}"
            flow_control_id = flow_control_info['data'][0]['id']
            flow_control_detail_res = paas_client.gw_client.get_flow_control_detail(gw_instance_name, flow_control_id,
                                                                                    queryName=api_name)
            check_status_code(flow_control_detail_res)
            flow_control_detail = flow_control_detail_res.json()
            check_response(EXP_RESPONSE, flow_control_detail)
            assert len(flow_control_detail['data']) > 0, f"无绑定接口：{api_name}"
        with allure.step("2.解绑接口"):
            api_ids = []
            for api in flow_control_detail['data']:
                api_ids.append(api['id'])
            if len(api_ids) == 1:
                unbind_response = paas_client.gw_client.unbind_api_with_flow_control(gw_instance_name, flow_control_id,
                                                                                     api_ids[0])
            else:
                unbind_response = paas_client.gw_client.batch_unbind_api_with_flow_control(gw_instance_name,
                                                                                           flow_control_id, api_ids)
            check_status_code(unbind_response)
            check_response(EXP_RESPONSE, unbind_response.json())
        with allure.step("3.绑定接口不再出现在代理缓存详情列表中"):
            flow_control_detail_res = paas_client.gw_client.get_flow_control_detail(gw_instance_name, flow_control_id,
                                                                                    queryName=api_name)
            check_status_code(flow_control_detail_res)
            flow_control_detail = flow_control_detail_res.json()
            check_response(EXP_RESPONSE, flow_control_detail)
            assert len(flow_control_detail['data']) == 0, f"未成功解绑接口：{api_name}"


def create_access_control(paas_client: PAASClient, gw_name, policy_name, limit_type, action="ALLOW", ip_address="",
                          **kwargs):
    """ 创建安全控制策略 """
    with allure.step("create_access_control()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        project_id = paas_client.login_info.default_project_id
        check_names_response = paas_client.gw_client.check_access_control(gw_instance_name, policy_name, project_id)
        check_status_code(check_names_response)
        check_response(EXP_RESPONSE, check_names_response.json())
        assert check_names_response.json()['data'], f"已存在安全控制策略：{policy_name}"
        created_response = paas_client.gw_client.create_access_control(gw_instance_name, policy_name, limit_type,
                                                                       action, ip_address, **kwargs)
        check_status_code(created_response)
        check_response(EXP_RESPONSE, created_response.json())


def delete_access_control(paas_client: PAASClient, gw_name, policy_name):
    """ 删除安全控制策略 """
    with allure.step("delete_access_control()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        access_controls_info = get_access_control_by_name(paas_client, gw_name, policy_name)
        assert len(access_controls_info['data']) > 0, f"未找到安全控制策略：{policy_name}"
        access_control_ids = []
        for access_controls_info in access_controls_info['data']:
            access_control_ids.append(access_controls_info['id'])
        if len(access_control_ids) == 1:
            deleted_response = paas_client.gw_client.delete_access_control(gw_instance_name, access_control_ids[0])
        else:
            deleted_response = paas_client.gw_client.delete_access_control(gw_instance_name, access_control_ids)
        check_status_code(deleted_response)
        check_response(EXP_RESPONSE, deleted_response.json())
        access_controls_info = get_access_control_by_name(paas_client, gw_name, policy_name)
        assert len(access_controls_info['data']) == 0, f"未删除流控策略：{policy_name}"


def get_access_control_by_name(paas_client: PAASClient, gw_name, policy_name):
    """ 根据名称查询安全控制策略 """
    with allure.step("get_access_control_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        access_control_response = paas_client.gw_client.get_access_controls_list(gw_instance_name, page=1, size=500,
                                                                                 name=policy_name)
        check_status_code(access_control_response)
        access_control_info = access_control_response.json()
        check_response(EXP_RESPONSE, access_control_info)
        return access_control_info


def get_unbound_apis_with_access_control_by_name(paas_client: PAASClient, gw_name, api_name, api_group_name=None):
    """ 查询安全控制策略未绑定接口 """
    with allure.step("get_unbound_apis_with_access_control_by_name()"):
        gw_info = get_gw_by_name(paas_client, gw_name)
        assert len(gw_info['data']) > 0, f"未找到服务网关实例：{gw_name}"
        gw_instance_name = gw_info['data'][0]['svcApimgtName']
        if api_group_name:
            api_group_info = get_api_group_by_name(paas_client, gw_name, api_group_name)
            assert len(api_group_info['data']) > 0, f"未找到网关{gw_name}下的接口组：{api_group_name}"
            api_group_id = api_group_info['data'][0]['id']
            unbound_apis_response = paas_client.gw_client.get_unbound_access_control_apis(gw_instance_name, page=1,
                                                                                          size=500, queryName=api_name,
                                                                                          groupId=api_group_id)
        else:
            unbound_apis_response = paas_client.gw_client.get_unbound_access_control_apis(gw_instance_name, page=1,
                                                                                          size=500, queryName=api_name)
        check_status_code(unbound_apis_response)
        unbound_apis = unbound_apis_response.json()
        check_response(EXP_RESPONSE, unbound_apis)
        return unbound_apis


def bind_apis_with_access_control(paas_client: PAASClient, gw_name, access_control_name, api_name, api_group_name=None):
    """ 安全控制策略绑定接口 """
    with allure.step("bind_apis_with_access_control()"):
        with allure.step("1.查询安全控制策略"):
            access_control_info = get_access_control_by_name(paas_client, gw_name, access_control_name)
            assert len(access_control_info['data']) > 0, f"未找到网关{gw_name}下的安全控制策略：{access_control_name}"
            access_control_id = access_control_info['data'][0]['id']
        with allure.step("2.查询未绑定接口"):
            unbound_apis = get_unbound_apis_with_access_control_by_name(paas_client, gw_name, api_name, api_group_name)
            assert len(unbound_apis['data']) > 0, f"未找到网关：{gw_name}下的接口组：{api_group_name}"
            exp_unbound_api = f"$.data[?(@.name=='{api_name}')]"
            apis_info = jsonpath.jsonpath(unbound_apis, exp_unbound_api)
            assert apis_info, f"未找到网关：{gw_name}下的接口组：{api_group_name}存在未绑定的接口：{api_name}"
        with allure.step("3.绑定接口"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            api_ids = []
            for api in apis_info:
                api_ids.append(api['id'])
            binding_response = paas_client.gw_client.bind_apis_with_access_control(gw_instance_name, access_control_id,
                                                                                   api_ids)
            check_status_code(binding_response)
            check_response(EXP_RESPONSE, binding_response.json())
        with allure.step("4.绑定接口出现在安全控制详情列表中"):
            temp = 10
            cnt = 1
            while cnt < temp:
                time.sleep(3)
                access_control_detail_res = paas_client.gw_client.get_apis_in_access_control_detail(gw_instance_name,
                                                                                                    access_control_id,
                                                                                                    queryName=api_name)
                check_status_code(access_control_detail_res)
                if len(access_control_detail_res.json()['data']) > 0:
                    break
                cnt += 1
            if cnt > temp:
                raise Exception(f"未成功绑定接口：{api_name}")
            access_control_detail = access_control_detail_res.json()
            check_response(EXP_RESPONSE, access_control_detail)


def unbind_apis_with_access_control(paas_client: PAASClient, gw_name, access_control_name, api_name, api_group_name=None):
    """ 安全控制解绑接口 """
    with allure.step("unbind_apis_with_access_control()"):
        with allure.step("1.查询安全控制详情"):
            gw_info = get_gw_by_name(paas_client, gw_name)
            gw_instance_name = gw_info['data'][0]['svcApimgtName']
            access_control_info = get_access_control_by_name(paas_client, gw_name, access_control_name)
            assert len(access_control_info['data']) > 0, f"未找到网关{gw_name}下的安全控制策略：{access_control_name}"
            access_control_id = access_control_info['data'][0]['id']
            access_control_detail_res = paas_client.gw_client.get_apis_in_access_control_detail(gw_instance_name,
                                                                                                access_control_id,
                                                                                                queryName=api_name)
            check_status_code(access_control_detail_res)
            access_control_detail = access_control_detail_res.json()
            check_response(EXP_RESPONSE, access_control_detail)
            assert len(access_control_detail['data']) > 0, f"无绑定接口：{api_name}"
        with allure.step("2.解绑接口"):
            api_ids = []
            for api in access_control_detail['data']:
                api_ids.append(api['id'])
            if len(api_ids) == 1:
                unbind_response = paas_client.gw_client.unbind_api_with_access_control(gw_instance_name,
                                                                                       access_control_id, api_ids[0])

            else:
                unbind_response = paas_client.gw_client.unbind_api_with_access_control(gw_instance_name,
                                                                                       access_control_id, api_ids)
            check_status_code(unbind_response)
            check_response(EXP_RESPONSE, unbind_response.json())
        with allure.step("3.绑定接口不再出现在安全控制详情列表中"):
            access_control_detail_res = paas_client.gw_client.get_apis_in_access_control_detail(gw_instance_name,
                                                                                                access_control_id,
                                                                                                queryName=api_name)
            check_status_code(access_control_detail_res)
            flow_control_detail = access_control_detail_res.json()
            check_response(EXP_RESPONSE, flow_control_detail)
            assert len(flow_control_detail['data']) == 0, f"未成功解绑接口：{api_name}"


def setup_create_apis(paas_client: PAASClient, cluster_name, package_name, package_version, app_container_spec,
                      svc_access_control, app_svc_info, gw_name, gw_container_spec, kong_ip, storage_class, data_volume,
                      api_group_name, api_name, svc_params, kong_params, **kwargs):
    """ 初始化： 创建接口 """

    with allure.step("1.创建应用组部署应用，校验应用状态，应用对外正常提供服务"):
        node_port = generate_svc_port(paas_client)
        node_port_info = {
            "nodePort": node_port
        }
        svc_access_control.update(node_port_info)
        role_name = paas_client.login_info.user_role
        if role_name == "admin":
            app_info = setup_create_jar_app(paas_client, cluster_name, package_name, package_version,
                                            app_container_spec, svc_access_control, app_svc_info, engine_type="others",
                                            role_name=role_name, project_name=kwargs['project_name'])
        else:
            app_info = setup_create_jar_app(paas_client, cluster_name, package_name, package_version,
                                            app_container_spec, svc_access_control, app_svc_info, engine_type="others",
                                            role_name=role_name)
        external_endpoint = app_info['data'][0]['external_endpoint'][0]
        services = [{
            "host": external_endpoint,
            "weight": 100
        }]
    with allure.step("2.服务网关实例"):
        setup_create_gateway(paas_client, gw_name, gw_container_spec, kong_ip, storage_class, data_volume)
    with allure.step("3.创建接口分组"):
        create_api_group(paas_client, gw_name, api_group_name)
    with allure.step("4.发布接口"):
        svc_params['services'] = services
        create_apis(paas_client, gw_name, api_group_name, api_name, svc_params, kong_params)
        sleep(10)
        api_detail = get_apis_detail_by_name(paas_client, gw_name, api_name)
        kong_url = api_detail['data']['kongUrl'][0]
        response = requests.get("http://" + kong_url)
        assert response.status_code == 200, f"访问http://{kong_url}失败"
        assert response.text == app_svc_info[
            'app_message'], f"访问http://{kong_url}失败。期望：{app_svc_info['app_message']}，实际：{response.text}"
        return app_info


def teardown_delete_apis(paas_client: PAASClient, gw_name, api_name, api_group_name, app_group_name):
    """ 删除接口 """
    with allure.step("1.删除接口"):
        delete_api_by_name(paas_client, gw_name, api_name)
    with allure.step("2.删除接口分组"):
        delete_api_group(paas_client, gw_name, api_group_name)
    with allure.step("3.删除网关"):
        delete_gateway(paas_client, gw_name)
    with allure.step("4.删除应用组"):
        delete_app_group_by_name(paas_client, app_group_name)