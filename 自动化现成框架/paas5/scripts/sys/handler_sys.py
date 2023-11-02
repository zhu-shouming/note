from time import sleep

import allure

from config.config import settings
from resource.base.client import PAASClient
from resource.utils.common import *

EXP_RESPONSE = {"code": "", "msg": ""}


# def get_project_by_name(user: PAASClient, project_name):
#     response = user.sys_client.get_projects_list()
#     check_status_code(response, 200)
#     return get_value_from_json(response, "$.data.res[?(@.name=='{}')]".format(project_name))


def new_project(user: PAASClient, project_name=None):
    if project_name == None:
        project_name = "auto" + get_random_string(5)
    response = user.sys_client.create_project(project_name)
    check_status_code(response, 200)
    cnt = 0
    while cnt < 5:
        expect = get_project_by_name(user, project_name)
        if expect:
            break
        sleep(2)
        cnt = cnt + 1
    assert expect, f"新建项目失败，列表中招不到新建的{project_name}项目"
    return expect


def new_pro_admin_and_user(user: PAASClient, project_id, project_name):
    pro_name = 'autoPro' + get_random_string(4).lower()
    user_name = 'autoUser' + get_random_string(4).lower()
    response = user.sys_client.get_role_list()
    check_status_code(response, 200)
    passwd = 'H46ee5wbc1FwjWxThNZ3lup6CyLEVk9pIpEQVfbog25ekiaE3OcbsKQ+G9PaWjI6jgy/p7k5OYqydcAmnKohfV7lR6P4Gyn7YhuDaOJo/0xy+lzzepgU9Q2ck79ic6jY5hoEE/yqmsDkUReIsGYImL+fc1giWosSeRpePkUH2ic='
    pro_admin_id = get_value_from_json(response, "$.data[?(@.name=='org_admin')].id")
    pro_user_id = get_value_from_json(response, "$.data[?(@.name=='user')].id")
    r1 = user.sys_client.creat_user(
        pro_name,
        "zhangsan",
        passwd,
        "zhnagsan@12.com",
        project_id,
        project_name,
        "org_admin",
        pro_admin_id,
    )
    r2 = user.sys_client.creat_user(
        user_name,
        "lisi",
        passwd,
        "lisi@12.com",
        project_id,
        project_name,
        "user",
        pro_user_id,
    )
    check_status_code(r1, 200)
    check_status_code(r2, 200)
    sleep(7)
    check = user.sys_client.get_project_users(project_id)
    user_list = get_value_from_json(check, '$.data.res..name', list_flag=True)
    assert pro_name in user_list
    assert user_name in user_list
    settings['PROJ_ADMIN'] = pro_name
    settings['PROJ_USER'] = user_name


def get_project_by_name(paas_client: PAASClient, project_name):
    """
    通过项目名称查找项目， 返回项目的详细信息

    :param paas_client: 登录信息
    :param project_name: 项目名称
    :return:
    """
    with allure.step("get_project_by_name()"):
        with allure.step("1.查询项目"):
            project_list_response = paas_client.sys_client.get_projects_list()
            check_status_code(project_list_response)
            project_list_info = json.loads(project_list_response.text)
            check_response(EXP_RESPONSE, project_list_info)
            project_list = project_list_info['data']['res']
            assert len(project_list) > 0, f"项目列表为空"
        with allure.step("2.查询指定组织信息"):
            exp_project_name = f"$.data.res[?(@.name=='{project_name}')]"
            project_info = get_value_from_json(
                project_list_response, exp_project_name, list_flag=False
            )
            return project_info


def get_user_by_name(paas_client: PAASClient, user):
    """
    查询用户

    :param paas_client: 登录信息
    :param user: 用户名
    :return:
    """
    with allure.step("get_user_by_name()"):
        user_info_response = paas_client.sys_client.get_users_list(name=user)
        check_status_code(user_info_response)
        return user_info_response.json()


def get_processes_by_kwargs(paas_client: PAASClient, **kwargs):
    """
    搜索流程

    :param paas_client: 登录信息
    :param kwargs: 搜索条件。如，status=PROCESSING；nameLike=aaaa；createUserNameLike=proj_admin；nextCandidateUser=userName
    :return:
    """
    with allure.step("get_processes_by_kwargs()"):
        if 'nextCandidateUser' in kwargs.keys():
            kwargs['nextCandidateUser'] = paas_client.login_info.user_id
        processes_info_response = paas_client.sys_client.get_processes(**kwargs)
        check_status_code(processes_info_response)
        return processes_info_response.json()


def approve_processes(paas_client: PAASClient, processes_ids, is_pass, message=""):
    """
    审批流程

    :param paas_client: 登录信息
    :param processes_ids：流程ID列表
    :param is_pass：同意（True）/ 驳回（False）
    :param message：处理意见
    :return:
    """
    with allure.step("approve_processes()"):
        ids = ""
        for i in range(len(processes_ids)):
            ids += processes_ids[i] + ","
        # ids[:-1] 去掉末尾的,
        approved_response = paas_client.sys_client.deal_with_process(ids[:-1], is_pass, message)
        check_status_code(approved_response)
        result = approved_response.json()
        if result['msg'] is None:
            return
        if "was updated by another transaction concurrently" in result['msg']:
            time.sleep(3)
            approved_response = paas_client.sys_client.deal_with_process(ids[:-1], is_pass, message)
            check_status_code(approved_response)
            assert approved_response.json()['msg'] == "", f"审批失败。原因：{approved_response.json()['msg']}"


def create_cluster_of_kafka(
    paas_client: PAASClient,
    cce_name,
    ns_name,
    cluster_name,
    kafka_info,
    zk_info,
    role_name="admin",
    **kwargs,
):
    """
    创建kafka集群

    :param paas_client: 登录信息
    :param cce_name：cce集群名称
    :param ns_name：命名空间
    :param cluster_name：集群名称
    :param kafka_info：kafka信息
    :param zk_info：zookeeper信息
    :param role_name：角色。admin/ org_admin/ user
    :param kwargs:
    :return:
    """
    with allure.step("create_cluster_of_kafka()"):
        with allure.step("1.获取项目ID"):
            project_id = settings['PROJECT_ID']
            if role_name == "admin":
                project_name = kwargs['project_name']
                project_info = get_project_by_name(paas_client, project_name)
                assert project_info, f"未找到项目：{project_name}"
                project_id = project_info['id']
        with allure.step("2.获取集群ID"):
            cce_info_response = paas_client.cce_client.get_cce_list(project_id)
            check_status_code(cce_info_response)
            cce_info = get_value_from_json(
                cce_info_response, f"$.data[?(@.name=='{cce_name}')]"
            )
            cce_id = cce_info['uuid']
        with allure.step("3.获取命名空间"):
            ns_info_response = paas_client.cce_client.get_cluster_detail(
                cce_id, project_id
            )
            check_status_code(ns_info_response)
            owner_info = get_value_from_json(
                ns_info_response, f"$.data.data[?(@.name=='{ns_name}')]"
            )
            assert owner_info, f"查找命名空间：{ns_name}失败"
            owner_id = owner_info['memberId']
            owner_name = owner_info['memberName']
        with allure.step("4.重名校验"):
            check_mqs_cluster_response = paas_client.sys_client.check_mqs_cluster_name(
                cce_id, ns_name, cluster_name
            )
            check_status_code(check_mqs_cluster_response)
            act_code = check_mqs_cluster_response.json()['code']
            assert (
                act_code != "cluster.create.name.exists"
            ), f"{check_mqs_cluster_response.json()['msg']}"
        with allure.step("5.创建集群"):
            created_response = paas_client.sys_client.create_kafka_cluster(
                cluster_name,
                project_id,
                cce_id,
                cce_name,
                owner_id,
                owner_name,
                ns_name,
                kafka_info,
                zk_info,
                **kwargs
            )
            check_status_code(created_response)
            check_response(EXP_RESPONSE, created_response.json())


def create_cluster_of_zookeeper(
    paas_client: PAASClient,
    cce_name,
    ns_name,
    cluster_name,
    zk_info,
    role_name="admin",
    **kwargs,
):
    """
    创建zookeeper集群

    :param paas_client: 登录信息
    :param cce_name：cce集群名称
    :param ns_name：命名空间
    :param cluster_name：集群名称
    :param zk_info：zookeeper信息
    :param role_name：角色。admin/ org_admin/ user
    :param kwargs:
    :return:
    """
    with allure.step("create_cluster_of_zookeeper()"):
        with allure.step("1.获取项目ID"):
            project_id = settings['PROJECT_ID']
            if role_name == "admin":
                project_name = kwargs['project_name']
                project_info = get_project_by_name(paas_client, project_name)
                assert project_info, f"未找到项目：{project_name}"
                project_id = project_info['id']
        with allure.step("2.获取集群ID"):
            cce_info_response = paas_client.cce_client.get_cce_list(project_id)
            check_status_code(cce_info_response)
            cce_info = get_value_from_json(cce_info_response, f"$.data[?(@.name=='{cce_name}')]")
            cce_id = cce_info['uuid']
        with allure.step("3.获取命名空间"):
            ns_info_response = paas_client.cce_client.get_cluster_detail(
                cce_id, project_id
            )
            check_status_code(ns_info_response)
            owner_info = get_value_from_json(
                ns_info_response, f"$.data.data[?(@.name=='{ns_name}')]"
            )
            assert owner_info, f"查找命名空间：{ns_name}失败"
            owner_id = owner_info['memberId']
            owner_name = owner_info['memberName']
        with allure.step("4.重名校验"):
            check_mqs_cluster_response = paas_client.sys_client.check_mqs_cluster_name(
                cce_id, ns_name, cluster_name
            )
            check_status_code(check_mqs_cluster_response)
            act_code = check_mqs_cluster_response.json()['code']
            assert (
                act_code != "cluster.create.name.exists"
            ), f"{check_mqs_cluster_response.json()['msg']}"
        with allure.step("5.创建集群"):
            created_response = paas_client.sys_client.create_zookeeper_cluster(
                cluster_name,
                project_id,
                cce_id,
                cce_name,
                owner_id,
                owner_name,
                ns_name,
                zk_info,
            )
            check_status_code(created_response)
            check_response(EXP_RESPONSE, created_response.json())


def get_mqs_cluster_by_name(paas_client: PAASClient, cluster_type, cluster_name):
    """
    查询指定中间件集群

    :param paas_client: 登录信息
    :param cluster_type：中间件集群类型
    :param cluster_name：中间件集群名称
    :return:
    """
    with allure.step("get_mqs_cluster_by_name()"):
        cluster_info_response = paas_client.sys_client.get_mqs_cluster(type=cluster_type)
        check_status_code(cluster_info_response)
        cluster_info = get_value_from_json(cluster_info_response, f"$.data[?(@.name=='{cluster_name}')]")
        return cluster_info


def delete_mqs_cluster(paas_client: PAASClient, cluster_type, cluster_name):
    """
    删除中间件集群

    :param paas_client: 登录信息
    :param cluster_type：中间件集群类型
    :param cluster_name：中间件集群名称
    :return:
    """
    with allure.step("delete_mqs_cluster()"):
        with allure.step("1.查询指定集群"):
            cluster_info = get_mqs_cluster_by_name(paas_client, cluster_type, cluster_name)
            assert cluster_info, f"未找到集群：{cluster_name}"
            cluster_id = cluster_info['id']
        with allure.step("2.删除集群"):
            delete_cluster_response = paas_client.sys_client.delete_mqs_cluster(
                cluster_id
            )
            check_status_code(delete_cluster_response)
        with allure.step("3.校验集群已删除"):
            cluster_info = get_mqs_cluster_by_name(
                paas_client, cluster_type, cluster_name
            )
            assert not cluster_info, f"未删除集群：{cluster_name}"


def restart_mqs_cluster(paas_client: PAASClient, cluster_type, cluster_name):
    """
    重启中间件集群

    :param paas_client: 登录信息
    :param cluster_type：中间件集群类型
    :param cluster_name：中间件集群名称
    :return:
    """
    with allure.step("restart_mqs_cluster()"):
        with allure.step("1.查询指定集群"):
            cluster_info = get_mqs_cluster_by_name(
                paas_client, cluster_type, cluster_name
            )
            assert cluster_info, f"未找到集群：{cluster_name}"
            cluster_id = cluster_info['id']
        with allure.step("2.删除集群"):
            restart_cluster_response = paas_client.sys_client.restart_kafka_cluster(
                cluster_id
            )
            check_status_code(restart_cluster_response)
        with allure.step("3.校验集群状态"):
            temp = 360
            cnt = 1
            while cnt <= temp:
                result = get_mqs_cluster_by_name(
                    paas_client, cluster_type, cluster_name
                )
                if result:
                    act = jsonpath.jsonpath(result, "$.status")[0]
                    if act == "RUNNING":
                        break
                time.sleep(5)
                cnt = cnt + 1
            if cnt > temp:
                raise Exception(f"超时")


def new_project_and_user(
    paas_admin_login: PAASClient, role, name, nickname, passwd, email
):
    pro_name = "auto" + get_random_string(4)
    project = new_project(paas_admin_login, pro_name)
    response = paas_admin_login.sys_client.get_role_list()
    check_status_code(response, 200)
    role_id = get_value_from_json(response, f"$.data[?(@.name=='{role}')].id")
    assert role_id, f"获取角色ID失败，指定的角色名为：{role}"
    project_id = project['id']
    project_name = pro_name
    response = paas_admin_login.sys_client.creat_user(
        name,
        nickname,
        passwd,
        email,
        project_id,
        project_name,
        role,
        role_id,
    )
    check_status_code(response, 200)
    cnt = 0
    while cnt < 5:
        response = paas_admin_login.sys_client.get_project_users(
            project_id, page=1, pagesize=10
        )
        check_status_code(response)
        user_new = get_value_from_json(response, f"$.data.res[?(@.name=='{name}')]")
        if user_new:
            break
        cnt = cnt + 1
        sleep(5)
    assert user_new, f"用户列表中找不到新建的用户{name}"
    data = {"project": project_id, "user": user_new}
    return data


def setup_create_kafka_cluster(
    paas_client: PAASClient,
    cluster_name,
    ns_name,
    kafka_info,
    zk_info,
    role_name,
    **kwargs,
):

    """初始化：创建KAFKA集群

    :param paas_client: 登录信息
    :param cluster_name：集群名称
    :param ns_name：命名空间名称
    :param kafka_info：kafka的规格信息
    :param zk_info：zookeeper的规格信息
    :param role_name：角色。admin/ org_admin/ user
    :param kwargs：
    :return:

    """

    with allure.step("setup_create_kafka_cluster()"):
        with allure.step("1.创建kafka集群"):
            cce_name = settings['CLUSTER_NAME']
            cluster_type = "kafka"
            create_cluster_of_kafka(
                    paas_client,
                    cce_name,
                    ns_name,
                    cluster_name,
                    kafka_info,
                    zk_info,
                    role_name,
                    **kwargs
            )
        with allure.step("2.校验集群状态"):
            temp = 360
            cnt = 1
            while cnt <= temp:
                result = get_mqs_cluster_by_name(
                    paas_client, cluster_type, cluster_name
                )
                if result:
                    act = jsonpath.jsonpath(result, "$.status")[0]
                    if act == "RUNNING":
                        break
                time.sleep(5)
                cnt = cnt + 1
            if cnt > temp:
                raise Exception(f"超时")


def setup_create_zookeeper_cluster(
    paas_client: PAASClient, cluster_name, ns_name, zk_info, role_name, **kwargs
):

    """初始化：创建KAFKA集群

    :param paas_client: 登录信息
    :param cluster_name：集群名称
    :param ns_name：命名空间名称
    :param zk_info：zookeeper的规格信息
    :param role_name：角色。admin/ org_admin/ user
    :param kwargs：
    :return:

    """

    with allure.step("setup_create_zookeeper_cluster()"):
        with allure.step("1.创建kafka集群"):
            cce_name = settings['CLUSTER_NAME']
            cluster_type = "zookeeper"
            if role_name == "admin":
                create_cluster_of_zookeeper(
                    paas_client,
                    cce_name,
                    ns_name,
                    cluster_name,
                    zk_info,
                    role_name,
                    project_name=kwargs['project_name'],
                )
            else:
                create_cluster_of_zookeeper(
                    paas_client, cce_name, ns_name, cluster_name, zk_info, role_name
                )
        with allure.step("2.校验集群状态"):
            temp = 360
            cnt = 1
            while cnt <= temp:
                result = get_mqs_cluster_by_name(
                    paas_client, cluster_type, cluster_name
                )
                if result:
                    act = jsonpath.jsonpath(result, "$.status")[0]
                    if act == "RUNNING":
                        break
                time.sleep(5)
                cnt = cnt + 1
            if cnt > temp:
                raise Exception(f"超时")
