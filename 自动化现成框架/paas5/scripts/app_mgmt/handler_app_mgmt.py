import allure
from retrying import retry

from config.config import settings
from resource.base.client import PAASClient
from resource.utils.common import *
from resource.utils.shell import SSHConnection
from scripts.cce.handler_cce import *
from scripts.ccr.handler_ccr import *
from scripts.msg.handler_msg import *
from scripts.deploy.handler_deploy import *
from scripts.sys.handler_sys import *

# 响应成功时返回体中包含的字段
EXP_RESPONSE = {"code": "", "status": True}


def create_app_group(paas_client: PAASClient, app_group_name, namespace="", engine_type="Spring Cloud", svc_engine_id="",
                     **kwargs):
    """
    创建应用组

    :param paas_client: 登录信息
    :param app_group_name: 应用组名称
    :param namespace: 自定义命名空间
    :param engine_type: 微服务引擎类型：Spring Cloud; Istio; others
    :param svc_engine_id: SpringCloud微服务引擎ID
    :param kwargs: 项目名称
    :return:
    """

    create_app_group_resp = paas_client.app_mgmt_client.create_app_group(app_group_name, namespace, engine_type,
                                                                         svc_engine_id)
    check_status_code(create_app_group_resp)
    check_response(EXP_RESPONSE, create_app_group_resp.json())


def get_app_group_by_name(paas_client: PAASClient, app_group_name="", page=1, page_size=1000):
    """
    根据名称查询应用组

    :param paas_client: 登录信息
    :param app_group_name: 应用组名称
    :param page: 页码
    :param page_size: 数据量
    :return:
    """

    app_group_resp = paas_client.app_mgmt_client.get_app_groups_list(app_group_name, page=page, page_size=page_size)
    check_status_code(app_group_resp)
    app_group_info = app_group_resp.json()
    check_response(EXP_RESPONSE, app_group_info)
    return app_group_info


def delete_app_group_by_name(paas_client: PAASClient, app_group_name):
    """
    删除指定应用组

    :param paas_client: 登录信息
    :param app_group_name: 应用组名称
    :return:
    """
    with allure.step("delete_app_group_by_name()"):
        with allure.step("1.获取匹配应用组信息"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
        with allure.step("2.删除应用组"):
            app_group_id = app_group_info['data'][0]['uuid']
            delete_app_group_resp = paas_client.app_mgmt_client.delete_app_group(app_group_id)
            check_status_code(delete_app_group_resp)
            check_response(EXP_RESPONSE, delete_app_group_resp.json())
        with allure.step("3.删除确认"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            assert len(app_group_info['data']) == 0, f"删除应用组失败：{app_group_name}"


def get_app_by_name(paas_client: PAASClient, app_name, app_group_name=""):
    """
    获取指定应用信息。指定应用组名称则入口为应用组页面，未指定则入口为应用列表页面

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_group_name: 应用组名称
    :return:

    """

    with allure.step("get_app_by_name()"):
        if app_group_name == "":
            with allure.step("从应用列表页面查询"):
                app_info_resp = paas_client.app_mgmt_client.get_apps_list(name=app_name)
                check_status_code(app_info_resp)
                app_info = app_info_resp.json()
                check_response(EXP_RESPONSE, app_info)
        else:
            with allure.step("从应用组页面查询"):
                with allure.step("1.查询指定应用组"):
                    app_group_info_resp = paas_client.app_mgmt_client.get_app_groups_list(name=app_group_name)
                    check_status_code(app_group_info_resp)
                    app_group_info = app_group_info_resp.json()
                    check_response(EXP_RESPONSE, app_group_info)
                    assert len(app_group_info['data']) > 0, f"未找到应用组：{app_group_name}"
                with allure.step("2.查询指定应用"):
                    app_group_id = app_group_info['data'][0]['uuid']
                    app_info_resp = paas_client.app_mgmt_client.get_apps_list(appGroupId=app_group_id, name=app_name)
                    check_status_code(app_info_resp)
                    app_info = app_info_resp.json()
                    check_response(EXP_RESPONSE, app_info)
        return app_info


def get_app_detail_by_name(paas_client: PAASClient, app_name, app_group_name=""):
    """
    获取应用信息详情。指定应用组名称则入口为应用组页面，未指定则入口为应用列表页面

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_group_name: 应用组名称
    :return:

    """

    with allure.step("get_app_detail_by_name()"):
        app_info = get_app_by_name(paas_client, app_name, app_group_name)
        assert len(app_info['data']) > 0, f"未找到应用：{app_name}"
        app_id = app_info['data'][0]['uuid']
        app_detail_response = paas_client.app_mgmt_client.get_app_detail(app_id)
        check_status_code(app_detail_response)
        app_detail = app_detail_response.json()
        check_response(EXP_RESPONSE, app_detail)
        return app_detail


def delete_app_by_name(paas_client: PAASClient, app_name, delete_pvc="true"):
    """
    删除应用。

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param delete_pvc: 是否删除PVC。勾选为True，不勾选为False
    :return:
    """
    with allure.step("delete_app_by_name()"):
        with allure.step("1.获取并返回指定应用的信息"):
            app_info = get_app_by_name(paas_client, app_name)
            assert len(app_info["data"]) > 0, f"未找到应用： {app_name}"
        with allure.step("2.删除应用请求"):
            app_id = app_info["data"][0]["uuid"]
            delete_app_resp = paas_client.app_mgmt_client.delete_app(app_id, delete_pvc)
            check_status_code(delete_app_resp)
            check_response(EXP_RESPONSE, delete_app_resp.json())
        with allure.step("3.删除确认"):
            app_info = get_app_by_name(paas_client, app_name)
            assert len(app_info["data"]) == 0, f"未删除应用： {app_name}"


def delete_apps_patch_by_names(paas_client: PAASClient, app_names, delete_pvc="true"):
    """
    批量删除应用组

    :param paas_client: 登录信息
    :param app_names: 一组应用组名称
    :param delete_pvc: 是否删除关联pvc
    :return:

    """
    with allure.step("delete_apps_patch_by_names()"):
        with allure.step("1.获取匹配的所有应用信息"):
            ids = []
            for i in range(len(app_names)):
                app_info = get_app_by_name(paas_client, app_names[i])
                assert len(app_info['data']) > 0, f"未找到应用：{app_names[i]}"
                app_id = app_info['data'][0]['uuid']
                ids.append(app_id)
        with allure.step("2.批量删除应用"):
            delete_patch_resp = paas_client.app_mgmt_client.delete_app_patch(ids, delete_pvc)
            check_status_code(delete_patch_resp)
        with allure.step("3.删除确认"):
            for app_name in app_names:
                app_info = get_app_by_name(paas_client, app_name)
                assert len(app_info['data']) == 0, f"未删除应用：{app_name}"


def create_jar_app(
    paas_client: PAASClient,
    app_name,
    app_version,
    app_group_name,
    deploy_type,
    resource_type,
    app_type_info,
    cluster_info,
    app_package_info,
    container_spec,
    jdk_version,
    **kwargs,
):
    """
    创建jar应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_version: 应用版本号
    :param app_group_name: 应用组名称
    :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
    :param resource_type: 资源类型。当前缺省为容器集群
    :param app_type_info: 应用类型
    :param cluster_info: 资源配置
    :param app_package_info: 应用安装包
    :param container_spec: 容器规格
    :param jdk_version: JDK版本
    :param kwargs:
    :return:
    """
    with allure.step("create_jar_app()"):
        with allure.step("1.查询集群ID"):
            cluster_type = cluster_info["cluster_type"]
            if resource_type == "container":
                cluster_id = settings['CLUSTER_ID']
            if resource_type == "mcp":
                cluster_id = settings['MCP_CLUSTER_ID']
        with allure.step("2.应用选择的命名空间"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_id = app_group_info['data'][0]['uuid']
            app_group_ns = app_group_info['data'][0]['namespace']
        with allure.step("3.选择应用包"):
            repository = app_package_info['repository']
            package_name = app_package_info['package_name']
            package_version = app_package_info['package_version']
            package_type = 'jar'
            package_info = get_deploy_package_by_name_and_version(
                paas_client, package_type, repository, package_name, package_version
            )
            assert package_info, f"未找到指定应用{package_name}"
            version_id = package_info[0]['id']
        with allure.step("5.创建应用请求"):
            created_app_response = paas_client.app_mgmt_client.create_app_of_jar(
                app_group_id,
                app_name,
                app_version,
                app_group_ns,
                resource_type,
                app_type_info,
                cluster_type,
                deploy_type,
                cluster_id,
                version_id,
                jdk_version,
                container_spec,
                **kwargs,
            )
            check_status_code(created_app_response)
            created_app_info = json.loads(created_app_response.text)
            check_response(EXP_RESPONSE, created_app_info)


def create_war_app(
    paas_client: PAASClient,
    app_name,
    app_version,
    app_group_name,
    deploy_type,
    resource_type,
    app_type_info,
    cluster_info,
    app_package_info,
    container_spec,
    tomcat_version,
    jdk_version,
    **kwargs,
):
    """
    创建war应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_version: 应用版本号
    :param app_group_name: 应用组名称
    :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
    :param resource_type: 资源类型。当前缺省为容器集群
    :param app_type_info: 应用类型
    :param cluster_info: 资源配置
    :param app_package_info: 应用安装包
    :param container_spec: 容器规格
    :param tomcat_version: TOMCAT版本
    :param jdk_version: JDK版本
    :param kwargs:
    :return:
    """

    with allure.step("create_war_app()"):
        with allure.step("1.查询集群ID"):
            cluster_type = cluster_info["cluster_type"]
            if resource_type == "container":
                cluster_id = settings['CLUSTER_ID']
            if resource_type == "mcp":
                cluster_id = settings['MCP_CLUSTER_ID']
        with allure.step("2.应用选择的命名空间"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_id = app_group_info['data'][0]['uuid']
            app_group_ns = app_group_info['data'][0]['namespace']
        with allure.step("3.选择应用包"):
            repository = app_package_info['repository']
            package_name = app_package_info['package_name']
            package_version = app_package_info['package_version']
            package_type = 'war'
            package_info = get_deploy_package_by_name_and_version(
                paas_client, package_type, repository, package_name, package_version
            )
            assert package_info, f"未找到应用{package_name}"
            version_id = package_info[0]['id']
        with allure.step("5.创建应用请求"):
            created_response = paas_client.app_mgmt_client.create_app_of_war(
                app_group_id,
                app_name,
                app_version,
                app_group_ns,
                resource_type,
                app_type_info,
                cluster_type,
                deploy_type,
                cluster_id,
                version_id,
                tomcat_version,
                jdk_version,
                container_spec,
                **kwargs,
            )
            check_status_code(created_response)
            check_response(EXP_RESPONSE, created_response.json())


def create_front_app(
    paas_client: PAASClient,
    app_name,
    app_version,
    app_group_name,
    deploy_type,
    resource_type,
    app_type_info,
    cluster_info,
    app_package_info,
    container_spec,
    tomcat_version,
    jdk_version,
    nginx_version,
    **kwargs,
):

    """
    创建前端应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_version: 应用版本号
    :param app_group_name: 应用组名称
    :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
    :param resource_type: 资源类型。当前缺省为容器集群
    :param app_type_info: 应用类型
    :param cluster_info: 资源配置
    :param app_package_info: 应用安装包
    :param container_spec: 容器规格
    :param tomcat_version: TOMCAT版本
    :param jdk_version: JDK版本
    :param nginx_version: NGINX版本
    :param kwargs:
    :return:
    """
    with allure.step("create_front_app()"):
        with allure.step("1.查询集群ID"):
            cluster_type = cluster_info["cluster_type"]
            if resource_type == "container":
                cluster_id = settings['CLUSTER_ID']
            if resource_type == "mcp":
                cluster_id = settings['MCP_CLUSTER_ID']
        with allure.step("2.应用选择的命名空间"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_id = app_group_info['data'][0]['uuid']
            app_group_ns = app_group_info['data'][0]['namespace']
        with allure.step("3.选择应用包"):
            repository = app_package_info['repository']
            package_name = app_package_info['package_name']
            package_version = app_package_info['package_version']
            package_type = 'web'
            package_info = get_deploy_package_by_name_and_version(
                paas_client, package_type, repository, package_name, package_version
            )
            assert package_info, f"未找到指定应用{package_name}"
            version_id = package_info[0]['id']
        with allure.step("5.创建应用请求"):
            created_app_response = paas_client.app_mgmt_client.create_app_of_front(
                app_group_id,
                app_name,
                app_version,
                app_group_ns,
                resource_type,
                app_type_info,
                cluster_type,
                deploy_type,
                cluster_id,
                version_id,
                tomcat_version,
                jdk_version,
                nginx_version,
                container_spec,
                **kwargs,
            )
            check_status_code(created_app_response)
            created_app_info = json.loads(created_app_response.text)
            check_response(EXP_RESPONSE, created_app_info)


def create_helm_app(
    paas_client: PAASClient,
    app_name,
    app_version,
    app_group_name,
    resource_type,
    cluster_info,
    app_package_info,
    container_spec,
    **kwargs,
):
    """
    创建HELM应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_version: 应用版本号
    :param app_group_name: 应用组名称
    :param resource_type: 资源类型。当前缺省为容器集群
    :param cluster_info: 资源配置
    :param app_package_info: 应用安装包
    :param container_spec: 容器规格
    :param kwargs:
    :return:
    """
    with allure.step("create_helm_app()"):
        with allure.step("1.查询集群ID"):
            cluster_type = cluster_info["cluster_type"]
            cluster_id = settings['CLUSTER_ID']
        with allure.step("2.应用选择的命名空间"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_id = app_group_info['data'][0]['uuid']
        with allure.step("3.选择应用包"):
            repository = app_package_info['repository']
            package_name = app_package_info['package_name']
            package_version = app_package_info['package_version']
            package_type = 'helm'
            package_info = get_deploy_package_by_name_and_version(
                paas_client, package_type, repository, package_name, package_version
            )
            assert package_info, f"未找到指定应用{package_name}"
            version_id = package_info[0]['id']
        with allure.step("5.创建应用请求"):
            created_app_response = paas_client.app_mgmt_client.create_app_of_helm(
                app_group_id,
                app_name,
                app_version,
                resource_type,
                cluster_type,
                cluster_id,
                version_id,
                container_spec,
                **kwargs,
            )
            check_status_code(created_app_response)
            created_app_info = json.loads(created_app_response.text)
            check_response(EXP_RESPONSE, created_app_info)


def create_image_app(
    paas_client: PAASClient,
    app_name,
    app_version,
    app_group_name,
    deploy_type,
    resource_type,
    app_type_info,
    cluster_info,
    app_package_info,
    container_spec,
    **kwargs,
):
    """
    创建容器镜像应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_version: 应用版本号
    :param app_group_name: 应用组名称
    :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
    :param resource_type: 资源类型。当前缺省为容器集群
    :param app_type_info: 应用类型
    :param cluster_info: 资源配置
    :param app_package_info: 应用安装包
    :param container_spec: 容器规格
    :param kwargs:
    :return:
    """
    with allure.step("create_image_app()"):
        with allure.step("1.查询集群ID"):
            cluster_type = cluster_info["cluster_type"]
            if resource_type == "container":
                cluster_id = settings['CLUSTER_ID']
            if resource_type == "mcp":
                cluster_id = settings['MCP_CLUSTER_ID']
        with allure.step("2.应用选择的命名空间"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_id = app_group_info['data'][0]['uuid']
            app_group_ns = app_group_info['data'][0]['namespace']
        with allure.step("3.选择应用包"):
            package_name = app_package_info['package_name']
            package_info = get_img_info_by_name(paas_client, package_name)
            assert package_info, f"未找到指定应用{package_name}"
            version_id = package_info['images'][0]['versions']
            img_url = package_info['images'][0]['imgUrl']
        with allure.step("5.创建应用请求"):
            created_app_response = paas_client.app_mgmt_client.create_app_of_image(
                app_group_id,
                app_name,
                app_version,
                app_group_ns,
                resource_type,
                app_type_info,
                cluster_type,
                deploy_type,
                cluster_id,
                version_id,
                container_spec,
                img_url,
                **kwargs,
            )
            check_status_code(created_app_response)
            created_app_info = json.loads(created_app_response.text)
            check_response(EXP_RESPONSE, created_app_info)


def action_app_group(paas_client: PAASClient, app_group_name, action, current_status):
    """
    启停指定应用组

    :param paas_client: 登录信息
    :param app_group_name: 应用组名称
    :param action: start/ stop
    :param current_status: 当前状态
    :return:
    """

    with allure.step("action_app_group()"):
        with allure.step("1.获取指定应用组信息"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            assert len(app_group_info['data']) > 0, f"未找到应用组：{app_group_name}"
        with allure.step("2.确认应用组实际状态"):
            act_status = app_group_info['data'][0]['status']
            assert act_status == current_status, allure.attach(
                f"应用组：{app_group_name}，当前状态：{act_status}, 期望状态：{current_status}"
            )
        with allure.step("3.执行操作"):
            app_group_id = app_group_info['data'][0]['uuid']
            action_app_group_response = paas_client.app_mgmt_client.action_app_group(
                app_group_id, action
            )
            check_status_code(action_app_group_response)
            action_app_group_info = json.loads(action_app_group_response.text)
            check_response(EXP_RESPONSE, action_app_group_info)
            return action_app_group_info


def action_app(
    paas_client: PAASClient, app_name, action, current_status, app_group_name=""
):
    """
    启/停/重启指定应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param action: start/ stop/ restart
    :param app_group_name: 应用组名称
    :param current_status: 当前状态
    :return:
    """
    with allure.step("action_app()"):
        with allure.step("1.获取指定应用信息"):
            app_info = get_app_by_name(
                paas_client, app_name=app_name, app_group_name=app_group_name
            )
            assert len(app_info['data']) > 0, f"未找到应用：{app_name}"
        with allure.step("2.确认应用实际状态"):
            act_status = app_info['data'][0]['status']
            assert act_status == current_status, allure.attach(
                f"应用：{app_group_name}，当前状态：{act_status}, 期望状态：{current_status}"
            )
        with allure.step("3.执行操作"):
            app_id = app_info['data'][0]['uuid']
            action_app_response = paas_client.app_mgmt_client.action_app(app_id, action)
            check_status_code(action_app_response)
            action_app_info = json.loads(action_app_response.text)
            check_response(EXP_RESPONSE, action_app_info)
            return action_app_info


def scale_app(paas_client: PAASClient, app_name, resources):
    """
    弹性伸缩应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param resources: 规格信息
    :return:
    """
    with allure.step("scale_app()"):
        with allure.step("1.获取应用信息"):
            app_info = get_app_by_name(paas_client, app_name=app_name)
            assert len(app_info['data']) > 0, f"未找到应用：{app_name}"
            app_id = app_info['data'][0]['uuid']
        with allure.step("2.弹性伸缩"):
            scale_app_response = paas_client.app_mgmt_client.scale_app(
                app_name, app_id, resources
            )
            check_status_code(scale_app_response)
            scale_app_json = json.loads(scale_app_response.text)
            check_response(EXP_RESPONSE, scale_app_json)
        with allure.step("3.确认操作结果"):
            # 循环和超时
            temp = 100 / 5
            cnt = 1
            while cnt < temp:
                app_instance_response = (
                    paas_client.app_mgmt_client.get_app_instances_list(app_id)
                )
                check_status_code(app_instance_response)
                app_instance = json.loads(app_instance_response.text)
                check_response(EXP_RESPONSE, app_instance)
                if len(app_instance['data']) == 1:
                    act_resources = {
                        "limits": {
                            "cpu": str(
                                int(app_instance['data'][0]['cpu_info']['total'] / 1000)
                            ),
                            "memory": str(
                                int(app_instance['data'][0]['mem_info']['total'])
                            )
                            + 'Mi',
                        },
                        "requests": {
                            "cpu": str(
                                int(
                                    app_instance['data'][0]['cpu_info']['request']
                                    / 1000
                                )
                            ),
                            "memory": str(
                                int(app_instance['data'][0]['mem_info']['request'])
                            )
                            + 'Mi',
                        },
                    }
                    for i in act_resources.keys():
                        if resources[i] != act_resources[i]:
                            break
                    else:
                        return
                time.sleep(5)
                cnt += 1
            assert cnt == temp, f"弹性伸缩超时。期望值：{resources}， 实际值：{act_resources}"


def upgrade_jar_app(paas_client: PAASClient, app_name, app_package_info):
    """
    升级jar包应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_package_info: 应用包的信息
    :return:

    """
    with allure.step("upgrade_jar_app()"):
        with allure.step("1.选择应用"):
            app_detail = get_app_detail_by_name(paas_client, app_name)
            app_id = app_detail['data']['uuid']
        with allure.step("2.选择应用包"):
            repository = app_detail['data']['package_visible']
            package_name = app_package_info['package_name']
            package_version = app_package_info['package_version']
            package_type = 'jar'
            package_info = get_deploy_package_by_name_and_version(
                paas_client, package_type, repository, package_name, package_version
            )
            assert package_info, f"未找到指定应用{package_name}"
            version_id = package_info[0]['id']
        with allure.step("3.升级"):
            upgrade_response = paas_client.app_mgmt_client.upgrade_app_of_jar(app_id, version_id, package_version,
                                                                              app_detail)
            check_status_code(upgrade_response)
            upgrade_info = json.loads(upgrade_response.text)
            check_response(EXP_RESPONSE, upgrade_info)
            return upgrade_info


def rollback_jar_app(paas_client: PAASClient, app_name):
    """
    回滚jar包应用

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :return:

    """
    with allure.step("rollback_jar_app()"):
        with allure.step("1.选择应用"):
            app_detail = get_app_detail_by_name(paas_client, app_name)
            app_id = app_detail['data']['uuid']
        with allure.step("2.查看历史版本"):
            app_history_versions_response = (
                paas_client.app_mgmt_client.get_app_history_versions(app_id)
            )
            check_status_code(app_history_versions_response)
            app_history_versions = json.loads(app_history_versions_response.text)
            check_response(EXP_RESPONSE, app_history_versions)
            version = app_history_versions['data'][0]['version']
            version_id = app_history_versions['data'][0]['version_id']
            old_app_detail = app_history_versions['data'][0]
        with allure.step("3.回滚"):
            rollback_response = paas_client.app_mgmt_client.rollback_app_of_jar(
                app_id, version_id, version, old_app_detail
            )
            check_status_code(rollback_response)
            rollback_info = json.loads(rollback_response.text)
            check_response(EXP_RESPONSE, rollback_info)
            return rollback_info


def get_cluster_by_name(paas_client: PAASClient, cluster_type, cluster_name):
    """
    查询集群信息

    :param paas_client: 登录信息
    :param cluster_type: 集群类型
    :param cluster_name: 集群名称
    :return:
    """
    cluster_info_response = paas_client.app_mgmt_client.get_clusters_list_by_type(
        cluster_type
    )
    check_status_code(cluster_info_response)
    exp_cluster = f"$.data[?(@.name=='{cluster_name}')]"
    cluster_info = get_value_from_json(
        cluster_info_response, exp_cluster, list_flag=True
    )
    return cluster_info


def get_mcp_cluster_by_name(paas_client: PAASClient, cluster_name, cluster_type="mcpCluster"):
    """
    查询MCP集群信息

    :param paas_client: 登录信息
    :param cluster_type: 集群类型
    :param cluster_name: 集群名称
    :return:
    """
    cluster_info_response = paas_client.app_mgmt_client.get_clusters_list_by_type(cluster_type)
    check_status_code(cluster_info_response)
    exp_cluster = f"$.data[?(@.mcpName=='{cluster_name}')]"
    cluster_info = get_value_from_json(
        cluster_info_response, exp_cluster, list_flag=True
    )
    return cluster_info


@retry(stop_max_attempt_number=20, stop_max_delay=40000)
def _get_app_external_service(url):
    """
    访问应用的外部访问地址

    :param url: 应用对外访问地址
    :return:

    """
    response = requests.get(url)
    assert response.status_code == 200, f"访问http://{url}失败"
    return response


def get_app_external_service(external_addr, uri):
    """
    访问应用的外部访问地址
    修改：ssh os后台，再执行cmd校验连接方式
    :param external_addr: 应用对外访问地址。IP:Port格式
    :param uri: 应用对外提供访问的URI。例如：/health
    :return:

    """
    # url = "http://" + external_addr + uri
    # result = None
    # try:
    #     response = _get_app_external_service(url)
    #     result = response.text
    # except Exception as e:
    #     allure.attach(f"{e}", name="get_app_external_service")
    # return result

    # host = external_addr.split(":")[0]
    host = settings.HOST
    sc = SSHConnection(host, "root", settings['PASSWORD'])
    sc.connect()
    message = sc.cmd("curl http://" + external_addr + uri)
    sc.close()
    return message


def generate_svc_port(paas_client: PAASClient):
    """
    随机生成集群外访问接口

    :param paas_client: 登录信息
    :return:

    """

    with allure.step("generate_svc_port()"):
        cnt = 1
        while cnt <= 5:
            svc_port = random.sample(range(30000, 32767), 1)[0]
            check_svc_port_resp = paas_client.app_mgmt_client.check_ports_by_cluster_id(settings['CLUSTER_ID'], svc_port)
            check_status_code(check_svc_port_resp)
            check_svc_port = check_svc_port_resp.json()
            check_response(EXP_RESPONSE, check_svc_port)
            if not check_svc_port['data']:
                return svc_port
            cnt += 1
        assert cnt < 5, "5次随机生成端口均被占用"


def check_app_svc_status(
    paas_client: PAASClient, app_name, app_svc_info, app_group_name=""
):
    """
    校验应用对外访问是否正常

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_svc_info: 应用的相关信息
    :param app_group_name: 应用组名称
    :return:
    """
    app_info = get_app_by_name(paas_client, app_name, app_group_name)
    assert len(app_info['data']) > 0, f"未找到应用：{app_name}"
    external_endpoint = app_info['data'][0]['external_endpoint'][0]
    app_uri = app_svc_info['app_uri']
    exp_message = app_svc_info['app_message']
    check_message_timeout(
        exp_message,
        get_app_external_service,
        external_addr=external_endpoint,
        uri=app_uri,
    )


def check_html_status(
    paas_client: PAASClient, app_name, app_svc_info, app_group_name=""
):
    """
    校验结果为网页的应用对外访问是否正常

    :param paas_client: 登录信息
    :param app_name: 应用名称
    :param app_svc_info: 应用的相关信息
    :param app_group_name: 应用组名称
    :return:
    """
    app_info = get_app_by_name(paas_client, app_name, app_group_name)
    assert len(app_info['data']) > 0, f"未找到应用：{app_name}"
    external_endpoint = app_info['data'][0]['external_endpoint'][0]
    app_uri = app_svc_info['app_uri']
    exp_message = app_svc_info['app_message']
    check_contained_message_timeout(
        exp_message,
        get_app_external_service,
        external_addr=external_endpoint,
        uri=app_uri,
    )


def setup_create_app_group(
    paas_client: PAASClient,
    engine_type="Spring Cloud",
    engine_name="",
    namespace=""
):
    """
    初始化：在基于Spring Cloud微服务引擎的应用组中部署jar包

    :param paas_client: 登录信息
    :param engine_type: 引擎类型
    :param engine_name: 引擎名称
    :param namespace: 命名空间名称
    :param is_admin: 是否是系统管理员
    :return:

    """
    with allure.step("1)填写应用组信息"):
        app_group_name = "auto" + get_random_string(6, char_type=0).lower()
        engine_id = ""
        if engine_type == "Spring Cloud":
            with allure.step("1-1)创建Spring Cloud微服务引擎"):
                engine_info = new_spingcloud_engine(paas_client)
                engine_id = engine_info['id']
    with allure.step("2)创建应用组"):
        create_app_group(
            paas_client,
            app_group_name=app_group_name,
            engine_type=engine_type,
            svc_engine_id=engine_id,
        )
    with allure.step("3)查询是否创建成功"):
        exp_status = "running"
        exp_path = "$.data[0].status"
        check_status_timeout(
            exp_status,
            exp_path,
            get_app_group_by_name,
            paas_client=paas_client,
            app_group_name=app_group_name,
        )
    with allure.step("4)返回创建的应用组信息"):
        app_group_info = get_app_group_by_name(paas_client, app_group_name)
        return app_group_info['data'][0]


def setup_create_jar_app(
    paas_client: PAASClient,
    cluster_name,
    package_name,
    package_version,
    container_spec,
    svc_access_control,
    app_svc_info,
    repository=True,
    engine_type="others",
    **kwargs,
):
    """
    初始化：在基于Spring Cloud微服务引擎的应用组中部署jar包

    :param paas_client: 登录信息
    :param cluster_name: 集群名称
    :param package_name: 应用包名称
    :param package_version: 应用包版本
    :param container_spec: 容器规格。包含CPU/ MEM的启动和运行限制
    :param svc_access_control: 服务访问控制信息。包括集群外访问、端口
    :param app_svc_info: 应用的相关信息
    :param repository: 仓库类型。公有（True）/ 私有（False）
    :param engine_type: 应用组的类型
    :return:

    """

    engine_id = ""
    if engine_type == "Spring Cloud":
        with allure.step("1.创Spring Cloud微服务引擎"):
            engine_info = new_spingcloud_engine(paas_client)
            engine_id = engine_info['id']
    with allure.step("2.创建应用组"):
        with allure.step("2-1)创建"):
            app_group_name = "auto" + get_random_string(6, char_type=0).lower()
            create_app_group(paas_client, app_group_name, engine_type=engine_type, svc_engine_id=engine_id)
        with allure.step("2-2)查询是否创建成功"):
            exp_app_group_status = "running"
            exp_path = "$.data[0].status"
            check_status_timeout(
                exp_app_group_status,
                exp_path,
                get_app_group_by_name,
                paas_client=paas_client,
                app_group_name=app_group_name,
            )
    with allure.step("3.创建应用"):
        with allure.step("3-1).创建应用第一步"):
            app_name = get_random_string(5).lower()
            app_version = get_random_string(5, 3)
            package_type = "jar"
            deploy_type = "Deployment"
            # 当前页面只有"容器集群"
            resource_type = "container"
            app_type_info = {"apiVersion": "apps/v1", "kind": "Deployment"}
            cluster_info = {"cluster_type": "kaasCluster", "cluster_name": cluster_name}
        with allure.step("3-2).创建应用第二步"):
            # 应用安装包
            app_package_info = {
                "repository": repository,
                "package_name": package_name,
                "package_version": package_version,
            }
            # 容器规格
            container_spec = {
                "cpu_request": container_spec['cpu_request'],
                "mem_request": container_spec['mem_request'],
                "cpu_limit": container_spec['cpu_limit'],
                "mem_limit": container_spec['mem_limit'],
            }
            # JDK版本
            jdk_version = "1.8"
            # 服务访问控制
            svc_access_control_info = {
                "dns_policy": "ClusterFirst"
                if svc_access_control['dns_policy'] == '集群外访问'
                else "",
                "targetPort": svc_access_control['targetPort'],
                "port": svc_access_control['port'],
                "nodePort": generate_svc_port(paas_client)
            }
        with allure.step("3-3).创建应用"):
            create_jar_app(
                paas_client,
                app_name,
                app_version,
                app_group_name,
                deploy_type,
                resource_type,
                app_type_info,
                cluster_info,
                app_package_info,
                container_spec,
                jdk_version,
                svc_access_control_info=svc_access_control_info,
                **kwargs,
            )
        with allure.step("3-4).检查应用运行状态"):
            exp_path = "$.data[0].status"
            exp_app_status = "OK"
            check_status_timeout(
                exp_app_status,
                exp_path,
                get_app_by_name,
                paas_client=paas_client,
                app_name=app_name,
                app_group_name=app_group_name,
            )
    with allure.step("4.验证对外服务是否正常"):
        app_svc_info = {
            "app_uri": app_svc_info['app_uri'],
            "app_message": app_svc_info['app_message'],
        }
        check_app_svc_status(
            paas_client, app_name, app_svc_info, app_group_name=app_group_name
        )
        app_info = get_app_by_name(paas_client, app_name, app_group_name)
    return app_info


def setup_create_helm_app(
    paas_client: PAASClient,
    cluster_name,
    package_name,
    package_version,
    container_spec,
    app_svc_info,
    application_name,
    repository=True,
    engine_type="others",
    **kwargs,
):
    """
    初始化：部署helm包

    :param paas_client: 登录信息
    :param cluster_name: 集群名称
    :param package_name: 应用包名称
    :param package_version: 应用包版本
    :param container_spec: 配额
    :param app_svc_info: 应用的相关信息
    :param application_name: helm包本身的名字，不带后缀
    :param repository: 仓库类型。公有（True）/ 私有（False）
    :param engine_type: 不同类型的应用组。Spring Cloud/ Istio/ others。
    :return:

    """
    with allure.step("1.创建应用组"):
        with allure.step("1-1)创建"):
            app_group_name = "auto" + get_random_string(6, char_type=0).lower()
            create_app_group(paas_client, app_group_name, engine_type=engine_type)
        with allure.step("1-2)查询是否创建成功"):
            exp_app_group_status = "running"
            exp_path = "$.data[0].status"
            check_status_timeout(
                exp_app_group_status,
                exp_path,
                get_app_group_by_name,
                paas_client=paas_client,
                app_group_name=app_group_name,
            )
    with allure.step("2.创建应用"):
        with allure.step("3-1).创建应用第一步"):
            app_name_prefix = get_random_string(5).lower()
            app_version = get_random_string(5, 3)
            package_type = "helm"
            # 当前页面只有"容器集群"
            resource_type = "container"
            cluster_info = {"cluster_type": "kaasCluster", "cluster_name": cluster_name}
        with allure.step("3-2).创建应用第二步"):
            # 应用安装包
            app_package_info = {
                "repository": repository,
                "package_name": package_name,
                "package_version": package_version,
            }
            # 容器规格
            container_spec = {
                "quota_cpu": container_spec['quota_cpu'],
                "quota_memory": container_spec['quota_memory'],
                "quota_storage": container_spec['quota_storage'],
            }
        with allure.step("3-3).创建应用"):
            create_helm_app(
                paas_client,
                app_name_prefix,
                app_version,
                app_group_name,
                resource_type,
                cluster_info,
                app_package_info,
                container_spec,
                **kwargs,
            )
        with allure.step("3-4).检查应用运行状态"):
            exp_path = "$.data[0].status"
            exp_app_status = "OK"
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_ns = app_group_info['data'][0]['namespace']
            app_name = app_name_prefix + "-" + app_group_ns + "-" + application_name
            check_status_timeout(
                exp_app_status,
                exp_path,
                get_app_by_name,
                paas_client=paas_client,
                app_name=app_name,
                app_group_name=app_group_name,
            )
    with allure.step("3.验证对外服务是否正常"):
        app_svc_info = {
            "app_uri": app_svc_info['app_uri'],
            "app_message": app_svc_info['app_message'],
        }
        check_html_status(
            paas_client, app_name, app_svc_info, app_group_name=app_group_name
        )
        app_info = get_app_by_name(paas_client, app_name, app_group_name)
    return app_info


def setup_create_war_app(
    paas_client: PAASClient,
    cluster_name,
    package_name,
    package_version,
    container_spec,
    svc_access_control,
    app_svc_info,
    repository=True,
    engine_type="others",
    **kwargs,
):
    """
    初始化：部署war包

    :param paas_client: 登录信息
    :param cluster_name: 集群名称
    :param package_name: 应用包名称
    :param package_version: 应用包版本
    :param container_spec: 容器规格。包含CPU/ MEM的启动和运行限制
    :param svc_access_control: 服务访问控制信息。包括集群外访问、端口
    :param app_svc_info: 应用的相关信息。
    :param repository: 仓库类型。公有（True）/ 私有（False）
    :param engine_type: 不同类型的应用组。Spring Cloud/ Istio/ others
    :return:

    """

    with allure.step("setup_create_war_app()"):
        with allure.step("1.创建应用组"):
            with allure.step("1-1)创建"):
                app_group_name = "auto" + get_random_string(6, char_type=0).lower()
                create_app_group(paas_client, app_group_name, engine_type=engine_type)
            with allure.step("1-2)查询是否创建成功"):
                exp_app_group_status = "running"
                exp_path = "$.data[0].status"
                check_status_timeout(
                    exp_app_group_status,
                    exp_path,
                    get_app_group_by_name,
                    paas_client=paas_client,
                    app_group_name=app_group_name,
                )
        with allure.step("2.创建war包应用"):
            with allure.step("3-1).创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                package_type = "war"
                deploy_type = "Deployment"
                # 当前页面只有"容器集群"
                resource_type = "container"
                app_type_info = {"apiVersion": "apps/v1", "kind": "Deployment"}
                cluster_info = {
                    "cluster_type": "kaasCluster",
                    "cluster_name": cluster_name,
                }
            with allure.step("3-2).创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": repository,
                    "package_name": package_name,
                    "package_version": package_version,
                }
                # 容器规格
                container_spec = {
                    "cpu_request": container_spec['cpu_request'],
                    "mem_request": container_spec['mem_request'],
                    "cpu_limit": container_spec['cpu_limit'],
                    "mem_limit": container_spec['mem_limit'],
                }
                # TOMCAT版本
                tomcat_version = "8.5"
                # JDK版本
                jdk_version = "1.8"
                # 服务访问控制
                svc_access_control_info = {
                    "dns_policy": "ClusterFirst"
                    if svc_access_control['dns_policy'] == '集群外访问'
                    else "",
                    "targetPort": svc_access_control['targetPort'],
                    "port": svc_access_control['port'],
                    "nodePort": generate_svc_port(paas_client)
                }
            with allure.step("3-3).创建应用"):
                create_war_app(
                    paas_client,
                    app_name,
                    app_version,
                    app_group_name,
                    deploy_type,
                    resource_type,
                    app_type_info,
                    cluster_info,
                    app_package_info,
                    container_spec,
                    tomcat_version,
                    jdk_version,
                    svc_access_control_info=svc_access_control_info,
                    **kwargs,
                )
            with allure.step("3-4).检查应用运行状态"):
                exp_path = "$.data[0].status"
                exp_app_status = "OK"
                check_status_timeout(
                    exp_app_status,
                    exp_path,
                    get_app_by_name,
                    paas_client=paas_client,
                    app_name=app_name,
                    app_group_name=app_group_name,
                )
        with allure.step("3.验证对外服务是否正常"):
            app_svc_info = {
                "app_uri": app_svc_info['app_uri'],
                "app_message": app_svc_info['app_message'],
            }
            check_html_status(
                paas_client, app_name, app_svc_info, app_group_name=app_group_name
            )
            app_info = get_app_by_name(paas_client, app_name, app_group_name)
        return app_info


def setup_create_front_app(
    paas_client: PAASClient,
    cluster_name,
    package_name,
    package_version,
    container_spec,
    svc_access_control,
    app_svc_info,
    repository=True,
    engine_type="others",
    **kwargs,
):
    """
    初始化：部署前端包

    :param paas_client: 登录信息
    :param cluster_name: 集群名称
    :param package_name: 应用包名称
    :param package_version: 应用包版本
    :param container_spec: 容器规格。包含CPU/ MEM的启动和运行限制
    :param svc_access_control: 服务访问控制信息。包括集群外访问、端口
    :param app_svc_info: 应用的相关信息
    :param repository: 仓库类型。公有（True）/ 私有（False）
    :param engine_type: 不同类型的应用组。Spring Cloud/ Istio/ others
    :return:


    """
    with allure.step("setup_create_front_app()"):
        with allure.step("1.创建应用组"):
            with allure.step("1-1)创建"):
                app_group_name = "auto" + get_random_string(6, char_type=0).lower()
                create_app_group(paas_client, app_group_name, engine_type=engine_type)
            with allure.step("1-2)查询是否创建成功"):
                exp_app_group_status = "running"
                exp_path = "$.data[0].status"
                check_status_timeout(
                    exp_app_group_status,
                    exp_path,
                    get_app_group_by_name,
                    paas_client=paas_client,
                    app_group_name=app_group_name,
                )
        with allure.step("2.创建应用"):
            with allure.step("3-1).创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                package_type = "web"
                deploy_type = "Deployment"
                # 当前页面只有"容器集群"
                resource_type = "container"
                app_type_info = {"apiVersion": "apps/v1", "kind": "Deployment"}
                cluster_info = {
                    "cluster_type": "kaasCluster",
                    "cluster_name": cluster_name,
                }
            with allure.step("3-2).创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": repository,
                    "package_name": package_name,
                    "package_version": package_version,
                }
                # 容器规格
                container_spec = {
                    "cpu_request": container_spec['cpu_request'],
                    "mem_request": container_spec['mem_request'],
                    "cpu_limit": container_spec['cpu_limit'],
                    "mem_limit": container_spec['mem_limit'],
                }
                # TOMCAT版本
                tomcat_version = kwargs['tomcat_version'] if 'tomcat_version' in kwargs.keys() else "8.5"
                # JDK版本
                jdk_version = kwargs['jdk_version'] if 'jdk_version' in kwargs.keys() else "1.8"
                # NGINX版本
                nginx_version = kwargs['nginx_version'] if 'nginx_version' in kwargs.keys() else "1.20"
                # 服务访问控制
                svc_access_control_info = {
                    "dns_policy": "ClusterFirst"
                    if svc_access_control['dns_policy'] == '集群外访问'
                    else "",
                    "targetPort": svc_access_control['targetPort'],
                    "port": svc_access_control['port'],
                    "nodePort": generate_svc_port(paas_client)
                }
            with allure.step("3-3).创建前端包应用"):
                create_front_app(
                    paas_client,
                    app_name,
                    app_version,
                    app_group_name,
                    deploy_type,
                    resource_type,
                    app_type_info,
                    cluster_info,
                    app_package_info,
                    container_spec,
                    tomcat_version,
                    jdk_version,
                    nginx_version,
                    svc_access_control_info=svc_access_control_info,
                    **kwargs,
                )
            with allure.step("3-4).检查应用运行状态"):
                exp_path = "$.data[0].status"
                exp_app_status = "OK"
                check_status_timeout(
                    exp_app_status,
                    exp_path,
                    get_app_by_name,
                    paas_client=paas_client,
                    app_name=app_name,
                    app_group_name=app_group_name,
                )
        with allure.step("3.验证对外服务是否正常"):
            app_svc_info = {
                "app_uri": app_svc_info['app_uri'],
                "app_message": app_svc_info['app_message'],
            }
            check_html_status(
                paas_client, app_name, app_svc_info, app_group_name=app_group_name
            )
            app_info = get_app_by_name(paas_client, app_name, app_group_name)
        return app_info


def setup_create_image_app(
    paas_client: PAASClient,
    cluster_name,
    package_name,
    package_version,
    container_spec,
    svc_access_control,
    app_svc_info,
    engine_type="Istio",
    **kwargs,
):
    """
    初始化：部署容器镜像包

    :param paas_client: 登录信息
    :param cluster_name: 集群名称
    :param package_name: 应用包名称
    :param package_version: 应用包版本
    :param container_spec: 容器规格。包含CPU/ MEM的启动和运行限制
    :param svc_access_control: 服务访问控制信息。包括集群外访问、端口
    :param app_svc_info: 应用的相关信息
    :param engine_type: 不同类型的应用组。Spring Cloud/ Istio/ others
    :return:


    """
    with allure.step("setup_create_image_app()"):
        with allure.step("1.创建应用组"):
            with allure.step("1-1)创建"):
                app_group_name = "auto" + get_random_string(6, char_type=0).lower()
                create_app_group(paas_client, app_group_name, engine_type=engine_type)
            with allure.step("1-2)查询是否创建成功"):
                exp_app_group_status = "running"
                exp_path = "$.data[0].status"
                check_status_timeout(
                    exp_app_group_status,
                    exp_path,
                    get_app_group_by_name,
                    paas_client=paas_client,
                    app_group_name=app_group_name,
                )
        with allure.step("2.创建应用"):
            with allure.step("3-1).创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                package_type = "image"
                deploy_type = "Deployment"
                # 当前页面只有"容器集群"
                resource_type = "container"
                app_type_info = {"apiVersion": "apps/v1", "kind": "Deployment"}
                cluster_info = {
                    "cluster_type": "kaasCluster",
                    "cluster_name": cluster_name,
                }
            with allure.step("3-2).创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": "true",
                    "package_name": package_name,
                    "package_version": package_version,
                }
                # 容器规格
                container_spec = {
                    "cpu_request": container_spec['cpu_request'],
                    "mem_request": container_spec['mem_request'],
                    "cpu_limit": container_spec['cpu_limit'],
                    "mem_limit": container_spec['mem_limit'],
                }
                # 服务访问控制
                svc_access_control_info = {
                    "dns_policy": "ClusterFirst"
                    if svc_access_control['dns_policy'] == '集群外访问'
                    else "",
                    "targetPort": svc_access_control['targetPort'],
                    "port": svc_access_control['port'],
                    "nodePort": generate_svc_port(paas_client)
                }
            with allure.step("3-3).创建应用"):
                create_image_app(
                    paas_client,
                    app_name,
                    app_version,
                    app_group_name,
                    deploy_type,
                    resource_type,
                    app_type_info,
                    cluster_info,
                    app_package_info,
                    container_spec,
                    svc_access_control_info=svc_access_control_info,
                    **kwargs,
                )
            with allure.step("3-4).校验应用创建结果"):
                exp_path = "$.data[0].status"
                exp_app_status = "OK"
                check_status_timeout(
                    exp_app_status,
                    exp_path,
                    get_app_by_name,
                    paas_client=paas_client,
                    app_name=app_name,
                    app_group_name=app_group_name,
                )
        with allure.step("3.验证对外服务是否正常"):
            app_svc_info = {
                "app_uri": app_svc_info['app_uri'],
                "app_message": app_svc_info['app_message'],
            }
            check_html_status(
                paas_client, app_name, app_svc_info, app_group_name=app_group_name
            )
            app_info = get_app_by_name(paas_client, app_name, app_group_name)
        return app_info


def setup_create_war_and_front_app(
    paas_client: PAASClient,
    cluster_name,
    package_info,
    container_spec,
    svc_access_control,
    app_svc_info,
    repository=True,
    engine_type="others",
    **kwargs,
):
    """
    初始化：部署war包和前端包应用

    :param paas_client: 登录信息
    :param cluster_name: 集群名称
    :param package_info: 一组应用包信息
    :param container_spec: 容器规格。包含CPU/ MEM的启动和运行限制
    :param svc_access_control: 一组服务访问控制信息。包括集群外访问、端口
    :param app_svc_info: 一组应用的相关信息
    :param repository: 仓库类型。公有（True）/ 私有（False）
    :param engine_type: 不同类型的应用组。Spring Cloud/ Istio/ others
    :return:

    """
    with allure.step("setup_create_war_and_front_app()"):
        with allure.step("1.创建应用组"):
            with allure.step("1-1)创建"):
                app_group_name = "auto" + get_random_string(6, char_type=0).lower()
                create_app_group(paas_client, app_group_name, engine_type=engine_type)
            with allure.step("1-2)查询是否创建成功"):
                exp_app_group_status = "running"
                exp_path = "$.data[0].status"
                check_status_timeout(
                    exp_app_group_status,
                    exp_path,
                    get_app_group_by_name,
                    paas_client=paas_client,
                    app_group_name=app_group_name,
                )
        with allure.step("2.创建war包应用"):
            with allure.step("2-1).创建应用第一步"):
                war_app_name = get_random_string(5).lower()
                war_app_version = get_random_string(5, 3)
                war_package_type = "war"
                deploy_type = "Deployment"
                # 当前页面只有"容器集群"
                resource_type = "container"
                app_type_info = {"apiVersion": "apps/v1", "kind": "Deployment"}
                cluster_info = {
                    "cluster_type": "kaasCluster",
                    "cluster_name": cluster_name,
                }
            with allure.step("2-2).创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": repository,
                    "package_name": package_info['war']['package_name'],
                    "package_version": package_info['war']['package_version'],
                }
                # 容器规格
                container_spec = {
                    "cpu_request": container_spec['cpu_request'],
                    "mem_request": container_spec['mem_request'],
                    "cpu_limit": container_spec['cpu_limit'],
                    "mem_limit": container_spec['mem_limit'],
                }
                # TOMCAT版本
                tomcat_version = "8.5"
                # JDK版本
                jdk_version = "1.8"
                # 服务访问控制
                svc_access_control_info = {
                    "dns_policy": "ClusterFirst",
                    "targetPort": svc_access_control['war']['targetPort'],
                    "port": svc_access_control['war']['port'],
                    "nodePort": generate_svc_port(paas_client),
                }
            with allure.step("2-3).创建应用"):
                create_war_app(
                    paas_client,
                    war_app_name,
                    war_app_version,
                    app_group_name,
                    deploy_type,
                    resource_type,
                    app_type_info,
                    cluster_info,
                    app_package_info,
                    container_spec,
                    tomcat_version,
                    jdk_version,
                    svc_access_control_info=svc_access_control_info,
                    **kwargs,
                )
            with allure.step("2-4).检查应用运行状态"):
                exp_path = "$.data[0].status"
                exp_app_status = "OK"
                check_status_timeout(
                    exp_app_status,
                    exp_path,
                    get_app_by_name,
                    paas_client=paas_client,
                    app_name=war_app_name,
                    app_group_name=app_group_name,
                )
            with allure.step("2-5).验证对外服务是否正常"):
                war_app_svc_info = {
                    "app_uri": app_svc_info['war']['app_uri'],
                    "app_message": app_svc_info['war']['app_message'],
                }
                check_html_status(
                    paas_client,
                    war_app_name,
                    war_app_svc_info,
                    app_group_name=app_group_name,
                )
        with allure.step("3.创建前端包应用"):
            with allure.step("3-1).创建应用第一步"):
                front_app_name = get_random_string(5).lower()
                front_app_version = get_random_string(5, 3)
                front_package_type = "web"
                deploy_type = "Deployment"
                # 当前页面只有"容器集群"
                resource_type = "container"
                app_type_info = {"apiVersion": "apps/v1", "kind": "Deployment"}
                cluster_info = {
                    "cluster_type": "kaasCluster",
                    "cluster_name": cluster_name,
                }
            with allure.step("3-2).创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": repository,
                    "package_name": package_info['front']['package_name'],
                    "package_version": package_info['front']['package_version'],
                }
                # 容器规格
                container_spec = {
                    "cpu_request": container_spec['cpu_request'],
                    "mem_request": container_spec['mem_request'],
                    "cpu_limit": container_spec['cpu_limit'],
                    "mem_limit": container_spec['mem_limit'],
                }
                # TOMCAT版本
                tomcat_version = kwargs['tomcat_version'] if 'tomcat_version' in kwargs.keys() else "8.5"
                # JDK版本
                jdk_version = kwargs['jdk_version'] if 'jdk_version' in kwargs.keys() else "1.8"
                # NGINX版本
                nginx_version = kwargs['nginx_version'] if 'nginx_version' in kwargs.keys() else "1.20"
                # 服务访问控制
                svc_access_control_info = {
                    "dns_policy": "ClusterFirst",
                    "targetPort": svc_access_control['front']['targetPort'],
                    "port": svc_access_control['front']['port'],
                    "nodePort": generate_svc_port(paas_client),
                }
            with allure.step("3-3).创建前端包应用"):
                create_front_app(
                    paas_client,
                    front_app_name,
                    front_app_version,
                    app_group_name,
                    deploy_type,
                    resource_type,
                    app_type_info,
                    cluster_info,
                    app_package_info,
                    container_spec,
                    tomcat_version,
                    jdk_version,
                    nginx_version,
                    svc_access_control_info=svc_access_control_info,
                    **kwargs,
                )
            with allure.step("3-4).检查应用运行状态"):
                exp_path = "$.data[0].status"
                exp_app_status = "OK"
                check_status_timeout(
                    exp_app_status,
                    exp_path,
                    get_app_by_name,
                    paas_client=paas_client,
                    app_name=front_app_name,
                    app_group_name=app_group_name,
                )
            with allure.step("3-5).验证对外服务是否正常"):
                front_app_svc_info = {
                    "app_uri": app_svc_info['front']['app_uri'],
                    "app_message": app_svc_info['front']['app_message'],
                }
                check_html_status(
                    paas_client,
                    front_app_name,
                    front_app_svc_info,
                    app_group_name=app_group_name,
                )
        with allure.step("4.返回应用组下所有应用信息"):
            app_group_info = get_app_group_by_name(paas_client, app_group_name)
            app_group_id = app_group_info['data'][0]['uuid']
            apps_info = paas_client.app_mgmt_client.get_apps_list(
                appGroupId=app_group_id
            )
            check_status_code(apps_info)
        return json.loads(apps_info.text)


def get_mcp_nodes_list(paas_client: PAASClient, mcp_cluster_name, instance_num=1):
    with allure.step("get_mcp_nodes_list"):
        mcp_nodes_resp = paas_client.app_mgmt_client.get_mcp_nodes_list(mcp_cluster_id=settings['MCP_CLUSTER_ID'])
        check_status_code(mcp_nodes_resp)
        mcp_nodes = mcp_nodes_resp.json()
        check_response(EXP_RESPONSE, mcp_nodes)
        assert mcp_nodes['data'], f"未找到MCP集群详细信息：{mcp_cluster_name}"
        mcp_nodes_list = []
        for mcp_node in mcp_nodes['data']:
            temp = {
                "clusterName": mcp_node['name'],
                "clusterIp": mcp_node['ip'],
                "instanceNum": instance_num,
                "imageUrl": "",
                "envs": None,
                "enable": False,
                "failOver": False
            }
            mcp_nodes_list.append(temp)
        return mcp_nodes_list


def set_svc_control(paas_client: PAASClient, app_name, svc_access_control, node_group_name):
    with allure.step("set_svc_control"):
        app_info = get_app_by_name(paas_client, app_name)
        assert len(app_info['data']) > 0, f"未找到应用：{app_name}"
        app_id = app_info['data'][0]['uuid']
        # 随机生成服务名
        cnt = 1
        while cnt <= 3:
            svc_name = app_name + "-" + get_random_string(5).lower() + "-svc"
            svc_name_check_resp = paas_client.app_mgmt_client.check_svc_name(app_id, svc_name)
            check_status_code(svc_name_check_resp)
            svc_name_check = svc_name_check_resp.json()
            check_response(EXP_RESPONSE, svc_name_check)
            if svc_name_check['data']:
                break
            cnt += 1
        assert cnt < 3, "3次随机生成服务名仍重复"
        port_name = "http-" + app_name + "-svc"
        # 随机生成集群外端口
        cnt = 1
        while cnt <= 3:
            node_port = random.sample(range(30000, 32767), 1)[0]
            node_port_check_resp = paas_client.app_mgmt_client.check_port_status(app_id, node_port)
            check_status_code(node_port_check_resp)
            node_port_check = node_port_check_resp.json()
            check_response(EXP_RESPONSE, node_port_check)
            if not node_port_check['data']:
                break
            cnt += 1
        assert cnt < 3, "3次随机生成集群外端口仍重复"
        # 设置访问方式
        container_port = svc_access_control['targetPort']
        cluster_port = svc_access_control['port']
        set_resp = paas_client.app_mgmt_client.set_svc_control(app_id, svc_name, port_name, container_port, cluster_port,
                                                               node_port, node_group_name)
        check_status_code(set_resp)
        check_response(EXP_RESPONSE, set_resp.json())
