import allure
from time import sleep
from config.config import settings

from resource.utils.common import *
from resource.base.client import PAASClient


def new_spingcloud_engine(user_client: PAASClient, name=None):
    """
    默认参数新建一个springcloud类型的微服务引擎  包含注册中心、配置中心、API网关
    供其他模块使用
    """
    if name is None:
        name = "auto" + get_random_string("4")
    org_id = user_client.login_info.default_project_id
    cluster_name = settings["CLUSTER_NAME"]
    cluster_id = settings["CLUSTER_ID"]
    description = ""
    version = "Finchley.SR4"
    resp = user_client.msg_client.get_discovery_info(version)
    check_status_code(resp)
    discover_version = get_value_from_json(resp, "$..version")
    assert discover_version, "获取组件版本信息失败"
    resp2 = user_client.msg_client.get_config_info(version)
    check_status_code(resp2)
    config_version = get_value_from_json(resp2, "$..version")
    assert config_version, "获取组件版本信息失败"
    resp3 = user_client.msg_client.get_gateway_info(version)
    check_status_code(resp3)
    gateway_version = get_value_from_json(resp3, "$..version")
    assert gateway_version, "获取组件版本信息失败"
    components = [
        {
            "version": discover_version,
            "duplicate": 1,
            "reqCPU": "0.5",
            "reqMemory": "512Mi",
            "limitCPU": "1",
            "limitMemory": "1024Mi",
            "storageClass": "", # TODO:共享集群需新建使用，默认使用default集群这个参数会使用容器存储下的nfs
            "clusterPort": "",
            "nodePort": "",
            "component": "discover",
        },
        {
            "component": "config",
            "version": config_version,
            "duplicate": 1,
            "reqCPU": "0.5",
            "reqMemory": "512Mi",
            "limitCPU": "1",
            "limitMemory": "1024Mi",
            "clusterPort": "",
            "nodePort": "",
        },
        {
            "component": "gateway",
            "version": gateway_version,
            "duplicate": 1,
            "reqCPU": "0.5",
            "reqMemory": "512Mi",
            "limitCPU": "1",
            "limitMemory": "1024Mi",
            "clusterPort": "",
            "nodePort": "",
        },
    ]
    midware_type = 0
    midware = [
        {"middleWare": "mysql", "url": "", "port": "", "user": "", "passWord": ""},
        {"middleWare": "redis", "url": "", "port": "", "passWord": ""},
    ]
    if settings["CLUSTER_NAME"] != "default":
        host = settings["HOST"]
        midware_type = 1
        midware = [
            {
                "middleWare": "mysql",
                "url": host,
                "port": "3306",
                "user": "os_admin",
                "passWord": "SDNDX0Nsb3VkMFMjUGFhU0BDVFQyMDE5",
            },
            {
                "middleWare": "redis",
                "url": host,
                "port": "6379",
                "passWord": "SDNDX0Nsb3VkMFNfUGFhU19DVFQyMDIw",
            },
        ]
    response = user_client.msg_client.create_micro_engine_with_springcloud(
        name,
        org_id,
        cluster_name,
        cluster_id,
        description,
        version,
        "",
        components,
        midware,
        midware_type,
        "native",
    )
    check_status_code(response, 200)
    allure.attach(f"{response.text}")
    cnt = 0
    while cnt < 30:
        engine = get_micro_engine_by_name(user_client, name)
        if bool(engine):
            if engine["state"] == "RUNNING":
                break
            # TODO：添加微服务创建异常直接退出
        sleep(20)
        cnt = cnt + 1
    assert bool(engine), f"列表中找不到新建的微服务引擎: {name}"
    assert (
        engine["state"] == "RUNNING"
    ), f"新建的微服务引擎{name}状态异常，预期为RUNNING,实际为{engine['state']}"
    return engine


def get_micro_engine_by_name(user_client: PAASClient, engine_name):
    """
    根据名字查询微服务引擎详细信息
    """

    org_id = user_client.login_info.default_project_id
    r = user_client.msg_client.get_msg_list(org_id, engineName=engine_name)
    check_status_code(r)
    engine_info = get_value_from_json(
        r, f"$.data[?(@.name=='{engine_name}')]", list_flag=False
    )
    return engine_info


def delete_micro_engine(user_client: PAASClient, engine_name):
    """根据名字删除微服务引擎

    Args:
        user_client : 用户登录信息
        engine_name : 微服务引擎实例名字
    """
    engine_info = get_micro_engine_by_name(user_client, engine_name)
    if not engine_info:
        raise ValueError("要删除的微服务引擎{}不存在".format(engine_name))
    engine_type = get_value_from_json(engine_info, "$..engineType")
    if engine_type == "Spring Cloud":
        response = user_client.msg_client.delete_springcloud_engine(
            settings["CLUSTER_ID"], engine_info["id"]
        )
    else:
        response = user_client.msg_client.delete_dubbo_engine(engine_info["id"])
    check_status_code(response, 200)
    for i in range(3):  # 等待删除完成, 最多查询三次列表 每次 间隔4秒
        sleep(4)
        result = get_micro_engine_by_name(user_client, engine_name)
        if result:
            continue
        else:
            break
    assert not result, f"删除微服务引擎{engine_name}失败"


def query_until_timeout(
    query_request,
    expect_code: bool,
    value_jsonpath=None,
    expect_value=None,
    timeout=300,
):
    """等待微服务引擎等资源创建或者删除完成 成功创建或删除则返回True 超时失败则返回False
    Args:
        query_request :

    """
    cnt = 0
    while cnt < timeout:
        sleep(5)
        result = query_request()
        if expect_code and bool(result):
            if get_value_from_json(result, value_jsonpath) == expect_value:
                return True
        if not (bool(result) or expect_code):
            return True
        cnt = cnt + 5
    return False


def add_spring_mse(user: PAASClient, name=None):
    if not name:
        name = "auto" + get_random_string("4")
    org_id = user.login_info.default_project_id
    cluster_name = settings["CLUSTER_NAME"]
    cluster_id = settings["CLUSTER_ID"]
    description = ""
    version = "Finchley.SR4"
    resp = user.msg_client.get_discovery_info(version)
    check_status_code(resp)
    discover_version = get_value_from_json(resp, "$..version")
    assert discover_version, "获取组件版本信息失败"
    components = [
        {
            "version": discover_version,
            "duplicate": 1,
            "reqCPU": "0.5",
            "reqMemory": "512Mi",
            "limitCPU": "1",
            "limitMemory": "1024Mi",
            "storageClass": "",
            "clusterPort": "",
            "nodePort": "",
            "component": "discover",
        }
    ]
    midware_type = 0
    midware = [
    ]
    if settings["CLUSTER_NAME"] != "default":
        midware_type = 1
    response = user.msg_client.create_micro_engine_with_springcloud(
        name,
        org_id,
        cluster_name,
        cluster_id,
        description,
        version,
        "",
        components,
        midware,
        midware_type,
        "native",
    )
    check_status_code(response, 200)
    allure.attach(f"{response.text}")
    cnt = 0
    while cnt < 30:
        engine = get_micro_engine_by_name(user, name)
        if bool(engine):
            if engine["state"] == "RUNNING":
                break
        sleep(20)
        cnt = cnt + 1
    assert bool(engine), f"列表中找不到新建的微服务引擎: {name}"
    assert (
        engine["state"] == "RUNNING"
    ), f"新建的微服务引擎{name}状态异常，预期为RUNNING,实际为{engine['state']}"
    return engine