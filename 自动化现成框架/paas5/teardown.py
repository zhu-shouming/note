import pathlib
import re
import time

import allure
import yaml
from py.path import local

from resource.base.client import PAASClient
from resource.base.login import PAASLogin
from resource.utils.common import get_value_from_json, check_status_code
from scripts.ccr.handler_ccr import *

config_dir = local(pathlib.Path(__file__).parent).join('config')
config_file = config_dir.join("env.yml")
with open(config_file, 'r', encoding="utf-8") as f:
    envs = yaml.load(f, Loader=yaml.FullLoader)


def teardown_env():
    """清理环境"""
    with allure.step("登录"):
        user = PAASClient(
            PAASLogin(envs['USERNAME'], envs['PASSWORD'], envs['HOST'], envs['PORT'])
        )

    with allure.step("删除应用组"):
        teardown_delete_groups(user)

    with allure.step("删除微服务引擎"):
        teardown_delete_engines(user)

    with allure.step("删除分类"):
        teardown_delete_tag(user)

    with allure.step("删除私有镜像组织"):
        teardown_delete_private_image_project(user)

    with allure.step("删除公有镜像"):
        teardown_delete_public_imgs(user)

    with allure.step("删除服务网关"):
        teardown_delete_gateway(user)

    # with allure.step("删除命名空间"):
    #     teardown_delete_namespace(user)

    # with allure.step("删除诊断实例"):
    #     teardown_delete_techops(user)
    with allure.step("删除上传的包"):
        teardown_delete_packages(user, True)
        teardown_delete_packages(user, False)
    # # with allure.step("删除pvc"):
    # teardown_delete_pvc(user)

    with allure.step("删除用户和项目"):
        teardown_project_and_users(user)

    with allure.step("删除私有镜像 默认仓库中的镜像包"):
        del_private_default_proj_images(user)


def teardown_project_and_users(user: PAASClient):
    r = user.sys_client.get_projects_list(page=1, pagesize=100, name="auto")
    projects = get_value_from_json(r, "$..id", list_flag=True)
    if projects:
        for project in projects:
            res = user.sys_client.get_project_users(project)
            user_list = get_value_from_json(res, "$.data.res[*]", list_flag=True)
            if bool(user_list):
                for item in user_list:
                    user.sys_client.remove_user_from_project(
                        project, item['id'], item['role_id']
                    )
                    user.sys_client.delete_user(item['id'])
            user.sys_client.delete_project(project)


def teardown_delete_groups(user: PAASClient):
    """删除应用组"""
    app_group_response = user.app_mgmt_client.get_app_groups_list(
        name="auto", page=1, page_size=1000
    )
    check_status_code(app_group_response)
    app_groups_list = app_group_response.json()

    if len(app_groups_list['data']) > 0:
        for app_group in app_groups_list['data']:
            app_group_id = app_group['uuid']
            delete_app_group_response = user.app_mgmt_client.delete_app_group(
                app_group_id
            )
            check_status_code(delete_app_group_response)


def teardown_delete_packages(user: PAASClient, repository=True):
    """删除应用仓库中的应用包"""
    package_info_response = user.deploy_client.get_packages_list(
        label="auto", visible=repository, page=1, size=1000
    )
    check_status_code(package_info_response)
    packages_list = package_info_response.json()
    for package_info in packages_list['data']:
        package_id = package_info['id']
        print(package_info)
        version_ids = ""
        if package_info['version_number'] > 0:
            package_version_ids = []
            for package_version in package_info['versions']:
                package_version_ids.append(package_version['id'])
            for package_version_id in package_version_ids:
                version_ids += package_version_id + ","
            version_ids = version_ids[:-1]
        delete_package_response = user.deploy_client.delete_package(
            package_id, version_ids
        )
        check_status_code(delete_package_response)


def teardown_delete_tag(user: PAASClient):
    """删除分类"""
    tags_list_response = user.deploy_client.get_tags_list()
    check_status_code(tags_list_response)
    tags_list = get_value_from_json(
        tags_list_response, f"$.data[?('auto' in @.tag[0:4])]", list_flag=True
    )
    if tags_list:
        for tag in tags_list:
            delete_tag_response = user.deploy_client.delete_tag(tag['id'])
            check_status_code(delete_tag_response)


def teardown_delete_engines(user: PAASClient):
    """删除微服务引擎"""
    r = user.msg_client.get_msg_list(
        user.login_info.default_project_id,  engineName="auto"
    )
    check_status_code(r, 200)
    msg_list = r.json()
    if len(msg_list['data']) > 0:
        for msg in msg_list['data']:
            engine_type = msg['engineType']
            if engine_type == "Spring Cloud":
                cluster_id = msg['clusterId']
                response = user.msg_client.delete_springcloud_engine(
                    cluster_id, msg["id"]
                )
            else:
                response = user.msg_client.delete_dubbo_engine(msg["id"])
            check_status_code(response, 200)


def teardown_delete_private_image_project(user: PAASClient):
    """删除私有镜像组织及镜像"""

    res = user.ccr_client.get_image_orgs(page=1, size=100, name="auto")
    check_status_code(res, 200)
    img_orgs_list = get_value_from_json(res, "$..name", list_flag=True)
    if not img_orgs_list:
        return
    else:
        for img_project in img_orgs_list:
            del_img_project(user, img_project)


def teardown_delete_public_imgs(user: PAASClient):
    """删除公有仓库镜像"""
    get_res = user.ccr_client.get_public_images(page=1, size=100, img_name="auto")
    images_list = get_value_from_json(get_res, "$..imageName", list_flag=True)
    if not images_list:
        return
    else:
        for image in images_list:
            del_public_img(user, image)


def teardown_delete_gateway(user: PAASClient):
    """删除网关"""
    gw_list_response = user.gw_client.get_gw_list(page=1, size=100, name="auto")
    check_status_code(gw_list_response)
    gw_list = gw_list_response.json()
    if len(gw_list['data']) > 0:
        for gw in gw_list['data']:
            gw_id = gw['uuid']
            deleted_response = user.gw_client.delete_gateway(gw_id)
            check_status_code(deleted_response)
            temp = 60
            cnt = 1
            while cnt <= temp:
                gw_list_response = user.gw_client.get_gw_list(name=gw['name'])
                check_status_code(gw_list_response)
                gw_info = gw_list_response.json()
                if len(gw_info['data']) == 0:
                    break
                time.sleep(5)
                cnt = cnt + 1
            if cnt > temp:
                raise Exception(f"超时")


def teardown_delete_namespace(user: PAASClient):
    """删除命名空间"""
    cluster_name = envs['CLUSTER_NAME']
    project_name = envs['PROJECT_NAME']

    proj_list_res = user.sys_client.get_projects_list(
        page=1, pagesize=100, name=project_name
    )
    check_status_code(proj_list_res, 200)
    project_id = get_value_from_json(proj_list_res, "$..id")

    cce_list_res = user.cce_client.get_cce_list()
    check_status_code(cce_list_res, 200)
    expect_cluster = get_value_from_json(
        cce_list_res, f"$.data[?(@.name=='{cluster_name}')]"
    )
    assert expect_cluster, f"找不到指定的集群：{cluster_name}"
    cluster_id = expect_cluster["uuid"]

    ns_info_res = user.cce_client.get_ns_of_cluster(cluster_id, 1, 10, name="auto")
    check_status_code(ns_info_res, 200)
    ns_names_list = ns_info_res.json()
    
    for ns_info in ns_names_list['data']['data']:
        ns_name = ns_info['name']
        del_res = user.cce_client.del_namespace(ns_name, cluster_id, project_id)
        check_status_code(del_res, 200)
        temp = 60
        cnt = 1
        while cnt <= temp:
            ns_info_res = user.cce_client.get_ns_of_cluster(
                cluster_id, 1, 10, name=ns_name
            )
            check_status_code(ns_info_res, 200)
            if len(ns_info_res.json()['data']['data']) == 0:
                break
            time.sleep(5)
            cnt = cnt + 1
        if cnt > temp:
            raise Exception(f"超时")


def teardown_delete_techops(user: PAASClient):
    """删除诊断实例"""
    techops_skymgt_info_resp = user.techops_client.get_skymgt_list(
        page=1, size=1000, name="auto"
    )
    check_status_code(techops_skymgt_info_resp)
    techops_skymgt_list = techops_skymgt_info_resp.json()
    if len(techops_skymgt_list['data']) > 0:
        for techops_skymgt in techops_skymgt_list['data']:
            techops_id = techops_skymgt['uuid']
            techops_name = techops_skymgt['name']
            delete_techops_response = user.techops_client.delete_techops(
                techops_id=techops_id
            )
            check_status_code(delete_techops_response)
            temp = 60
            cnt = 1
            while cnt <= temp:
                techops_skymgt_info_resp = user.techops_client.get_skymgt_list(
                    page=1, size=1000, name=techops_name
                )
                check_status_code(techops_skymgt_info_resp)
                if len(techops_skymgt_info_resp.json()['data']) == 0:
                    break
                time.sleep(5)
                cnt = cnt + 1
            if cnt > temp:
                raise Exception(f"超时")


# def teardown_delete_pvc(user: PAASClient):
#     """ 删除PV """
#     delete_pvc(user, user.login_info.context.get("envs")['CLUSTER_NAME'])


def teardown_delete_middleware(user: PAASClient):
    """删除中间件实例"""
    # 1. 删除kafka
    cluster_info_response = user.sys_client.get_mqs_cluster(type="kafka")
    check_status_code(cluster_info_response)
    cluster_info_list = cluster_info_response.json()
    if len(cluster_info_list['data']) > 0:
        for cluster_info in cluster_info_list['data']:
            if re.match(r"(auto)", cluster_info['name']):
                cluster_id = cluster_info['id']
                delete_cluster_response = user.sys_client.delete_mqs_cluster(cluster_id)
                check_status_code(delete_cluster_response)
    # 2. 删除zookeeper
    cluster_info_response = user.sys_client.get_mqs_cluster(type="zookeeper")
    check_status_code(cluster_info_response)
    cluster_info_list = cluster_info_response.json()
    if len(cluster_info_list['data']) > 0:
        for cluster_info in cluster_info_list['data']:
            if re.match(r"(auto)", cluster_info['name']):
                cluster_id = cluster_info['id']
                delete_cluster_response = user.sys_client.delete_mqs_cluster(cluster_id)
                check_status_code(delete_cluster_response)


if __name__ == '__main__':
    teardown_env()
