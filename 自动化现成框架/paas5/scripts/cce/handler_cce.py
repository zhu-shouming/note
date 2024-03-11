from resource.base.client import PAASClient
from resource.utils.common import *
from scripts.sys.handler_sys import new_project
from config.config import settings
from time import sleep


def new_namespace(user: PAASClient, name=None):
    if name == None:
        name = "auto" + get_random_string(4).lower()
    clusterId = settings['CLUSTER_ID']
    r = user.cce_client.add_namespace(name, clusterId, "")
    check_status_code(r, 200)
    time.sleep(3)
    r_check = user.cce_client.get_ns_of_cluster(clusterId, name=name)
    check_status_code(r_check, 200)
    assert get_value_from_json(r_check, "$..total") == 1
    return get_value_from_json(r_check, "$.data[0]")


def new_workload(user, payload_type, deploy_name, yaml_str, ns):
    r = user.cce_client.create_deployment_workload(
        payload_type, settings['CLUSTER_ID'], ns, yaml_str
    )
    check_status_code(r, 200)
    cnt = 0
    while cnt < 5:
        sleep(10)
        r_check = user.cce_client.get_deployment_by_ns(
            payload_type, settings['CLUSTER_ID'], ns
        )
        deploy = get_value_from_json(r_check, f"$.data[?(@.name=='{deploy_name}')]")
        if deploy["status"] == "running":
            break
        else:
            cnt = cnt + 1
    assert cnt < 5, f"新建{payload_type}工作负载失败"


def wait_action_finish_until_timeout(
    query_act_funtion, elem_jsonpath, expect_value, timeout: int, interval: int, *args
):
    """等待操作完成， 直到超时
        操作成功返回true 失败则返回false
    Args:
        query_act_funtion (_type_): 查询状态的请求
        elem_jsonpath (_type_): 待校验状态的jsonpath
        expect_value (_type_): 期望值
        timeout (_type_, optional): 超时时间
        interval (_type_, optional): 查询间隔
    """
    cnt = 0
    while cnt < timeout:
        sleep(interval)
        r = query_act_funtion(*args)
        check_status_code(r, 200)
        if get_value_from_json(r, elem_jsonpath) == expect_value:
            return True
        else:
            cnt = cnt + interval
    return False


def delete_pvc(user: PAASClient, cluster_name, pvc_name="", page=1, size=500):
    """删除pvc"""
    with allure.step("delete_pvc()"):
        with allure.step("1.查询集群ID"):
            cce_list_res = user.cce_client.get_cce_list()
            check_status_code(cce_list_res, 200)
            expect_cluster = get_value_from_json(
                cce_list_res, f"$.data[?(@.name=='{cluster_name}')]"
            )
            assert expect_cluster, f"找不到指定的集群：{cluster_name}"
            cluster_id = expect_cluster["uuid"]
        with allure.step("2.查询pvc"):
            pvc_list_res = user.cce_client.get_pvc_for_cluster(
                cluster_id, page=page, size=size
            )
            check_status_code(pvc_list_res)
        with allure.step("3.删除pvc"):
            if pvc_name == "":
                pvcs_info = pvc_list_res.json()['data']
                for pvc_info in pvcs_info['data']:
                    delete_res = user.cce_client.delete_pvc_for_cluster(
                        cluster_id, pvc_info['persistentVolume']['metadata']['name']
                    )
                    check_status_code(delete_res)
            else:
                delete_res = user.cce_client.delete_pvc_for_cluster(
                    cluster_id, pvc_name
                )
                check_status_code(delete_res)


def get_project_cluster_byname(user: PAASClient, cluster_name):
    res = user.cce_client.get_cce_list(name=cluster_name)
    check_status_code(res, 200)
    cluster = get_value_from_json(res, f"$.data[?(@.name=='{cluster_name}')]")
    assert cluster, f"查找cce集群：{cluster_name}失败"
    return cluster
