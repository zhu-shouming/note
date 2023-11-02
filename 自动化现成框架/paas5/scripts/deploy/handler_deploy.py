import os
import platform

import allure

from config.config import settings
from resource.base.client import PAASClient
from resource.utils.common import *

# 响应成功时返回体中包含的字段
EXP_RESPONSE = {
    "code": "",
    "status": True
}


def create_tag(paas_client: PAASClient, tag_name):
    """
    创建分类

    :param paas_client: 登录信息
    :param tag_name: 分类名称
    :return:

    """
    with allure.step("create_tag()"):
        created_resp = paas_client.deploy_client.create_tag(tag_name)
        check_status_code(created_resp)
        tag_info = created_resp.json()
        check_response(EXP_RESPONSE, tag_info)


def get_tags_list(paas_client: PAASClient):
    """
    查询分类列表

    :param paas_client: 登录信息
    :return:

    """
    with allure.step("get_tags_list()"):
        tags_list_response = paas_client.deploy_client.get_tags_list()
        check_status_code(tags_list_response)
        tags_list = tags_list_response.json()
        check_response(EXP_RESPONSE, tags_list)
        return tags_list


def get_tag_by_name(paas_client: PAASClient, tag_name):
    """
    根据名称查询分类

    :param paas_client: 登录信息
    :param tag_name: 分类名称
    :return:

    """
    with allure.step("get_tag_by_name()"):
        tags_list_resp = paas_client.deploy_client.get_tags_list()
        check_status_code(tags_list_resp)
        tag_info = get_value_from_json(tags_list_resp, f"$.data[?(@.tag=='{tag_name}')]", list_flag=False)
        return tag_info


def delete_tag(paas_client: PAASClient, tag_name):
    """
    根据名称删除分类

    :param paas_client: 登录信息
    :param tag_name: 分类名称
    :return:

    """
    with allure.step("delete_tag()"):
        tag_info = get_tag_by_name(paas_client, tag_name)
        assert tag_info, f"未找到分类：{tag_name}"
        tag_id = tag_info['id']
        delete_tag_resp = paas_client.deploy_client.delete_tag(tag_id)
        check_status_code(delete_tag_resp)
        check_response(EXP_RESPONSE, delete_tag_resp.json())
        tag_info = get_tag_by_name(paas_client, tag_name)
        assert not tag_info, f"未删除分类：{tag_name}"


def upload_package(paas_client: PAASClient, package_name, package_version, tag_name, package_type, file_path,
                   repository=True, **kwargs):
    """
    应用仓库上传应用包

    :param paas_client: 登录信息
    :param package_name: 应用包名称
    :param package_version: 应用包版本
    :param tag_name: 应用包分类
    :param package_type: 应用包类型。如，war/ jar/ helm/ 前端包
    :param file_path: 应用包路径和名称。例如，D:\\abc\\file_name.zip
    :param repository: 公有仓库（true）/ 私有仓库（false）
    :param kwargs:
    :return:

    """
    with allure.step("upload_package()"):
        tag_info = get_tag_by_name(paas_client, tag_name)
        assert tag_info, f"未找到分类：{tag_name}"
        tag_id = tag_info['id']
        os_type = platform.system()
        packages_list = []
        if os_type == "Windows":
            packages_list = file_path.split("\\")
        if os_type == "Linux":
            packages_list = file_path.split("/")

        file_name = packages_list[-1]   # 带后缀的文件名称
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        with open(file_path, mode='rb') as f:
            file_rb = f.read()
        upload_package_resp = paas_client.deploy_client.upload_package(package_name, package_version, tag_id, file_name,
                                                                       package_type, file_size, file_rb, repository,
                                                                       **kwargs)
        check_status_code(upload_package_resp)
        check_response(EXP_RESPONSE, upload_package_resp.json())


def delete_package(paas_client: PAASClient, package_name, package_versions, visible=True):
    """
    根据名称和版本删除应用包

    :param paas_client: 登录信息
    :param package_name: 应用包名称
    :param package_versions: 版本名称列表
    :param visible: 公有仓库（True）/ 私有仓库（False）
    :return:

    """
    with allure.step("delete_package()"):
        package_info = get_package_by_name(paas_client, package_name, visible)
        assert len(package_info['data']) > 0, f"未找到指定应用包：{package_name}"
        package_id = package_info['data'][0]['id']
        package_version_ids = []
        for package_version in package_versions:
            package_version_info = get_value_from_json(package_info, f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]")
            assert package_version_info, f"未找到应用包:{package_name} 的版本：{package_version}"
            package_version_ids.append(package_version_info['id'])
        with allure.step("2.删除应用包"):
            version_ids = ""
            for package_version_id in package_version_ids:
                version_ids += package_version_id + ","
            delete_package_response = paas_client.deploy_client.delete_package(package_id, version_ids[:-1])
            check_status_code(delete_package_response)
            delete_package_json = json.loads(delete_package_response.text)
            check_response(EXP_RESPONSE, delete_package_json)
        with allure.step("3.删除确认"):
            if len(package_versions) > 0:
                package_info = get_package_by_name(paas_client, package_name, visible)
                for package_version in package_versions:
                    package_version_info = get_value_from_json(package_info, f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]")
                    assert not package_version_info, f"未删除应用包：{package_name} 的版本：{package_version}"
            else:
                package_info = get_package_by_name(paas_client, package_name, visible)
                assert len(package_info['data']) == 0, f"删除指定应用包失败：{package_name}"


def download_package(paas_client: PAASClient, package_name, package_version, visible=True):
    """
    根据名称和版本下载应用包

    :param paas_client: 登录信息
    :param package_name: 应用包名称
    :param package_version: 版本名称
    :param visible: 公有仓库（True）/ 私有仓库（False）
    :return:

    """
    with allure.step("download_package()"):
        with allure.step("1.查询应用包和版本"):
            package_info = get_package_by_name(paas_client, package_name, visible)
            assert len(package_info['data']) > 0, f"未找到指定应用包：{package_name}"
            exp_package_version = f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]"
            package_version_info = jsonpath.jsonpath(package_info, exp_package_version)
            assert package_version_info, f"未找到应用包：{package_name} 的版本：{package_version}"
            package_version_id = package_version_info[0]['id']
            file_name = package_info['data'][0]['versions'][0]['file_name']
        with allure.step("2.下载应用包"):
            download_package_response = paas_client.deploy_client.download_package(package_version_id)
            check_status_code(download_package_response)
        with allure.step("3.保存文件"):
            os_type = platform.system()
            prefix_path = "C:\\"
            if os_type == "Linux":
                prefix_path = "/home/"
            file_path = prefix_path + file_name
            with open(file_path, "wb") as f:
                for chunk in download_package_response.iter_content(1024):
                    f.write(chunk)
            return file_path


def publish_package(paas_client: PAASClient, package_name, package_version):
    """
    发布应用包到公有仓库

    :param paas_client: 登录信息
    :param package_name: 应用包名称
    :param package_version: 版本名称
    :return:

    """
    with allure.step("publish_package()"):
        with allure.step("1.在私有仓库中查询应用包和版本"):
            package_info = get_package_by_name(paas_client, package_name, visible=False)
            assert len(package_info['data']) > 0, f"未找到指定应用包：{package_name}"
            package_id = package_info['data'][0]['id']
            exp_package_version = f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]"
            package_version_info = jsonpath.jsonpath(package_info, exp_package_version)
            assert package_version_info, f"未找到应用包：{package_name} 的版本：{package_version}"
            package_version_id = package_version_info[0]['id']
        with allure.step("2.发布到公有仓库"):
            publish_package_response = paas_client.deploy_client.publish_package(package_id, package_version_id)
            check_status_code(publish_package_response)
            publish_package_json = json.loads(publish_package_response.text)
            check_response(EXP_RESPONSE, publish_package_json)
        with allure.step("3.发布确认"):
            package_info = get_package_by_name(paas_client, package_name, visible=True)
            assert len(package_info['data']) > 0, f"发布应用包失败：{package_name}"


def apply_for_publishing_package(paas_client: PAASClient, package_name, package_version):
    """
    申请发布应用包到公有仓库

    :param paas_client: 登录信息
    :param package_name: 应用包名称
    :param package_version: 版本名称
    :return:

    """
    with allure.step("apply_for_publishing_package()"):
        with allure.step("1.在私有仓库中查询应用包和版本"):
            package_info = get_package_by_name(paas_client, package_name, visible=False)
            assert len(package_info['data']) > 0, f"未找到指定应用包：{package_name}"
            package_id = package_info['data'][0]['id']
            exp_package_version = f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]"
            package_version_info = jsonpath.jsonpath(package_info, exp_package_version)
            assert package_version_info, f"未找到应用包：{package_name} 的版本：{package_version}"
            package_version_id = package_version_info[0]['id']
        with allure.step("2.申请发布到公有仓库"):
            apply4publish_package_resp = paas_client.deploy_client.apply_for_publishing_package(package_id,
                                                                                                package_version_id)
            check_status_code(apply4publish_package_resp)
            check_response(EXP_RESPONSE, apply4publish_package_resp.json())


def get_package_by_name(paas_client: PAASClient, package_name="", visible=True, page=1, size=1000):
    """
    根据应用包名和版本查询应用包信息

    :param paas_client: 登录信息
    :param package_name: 应用包名
    :param visible: 公有仓库（True）/ 私有仓库（False）
    :param page: 页码
    :param size: 数据量
    :return:
    """
    with allure.step("get_package_by_name()"):
        package_info_response = paas_client.deploy_client.get_packages_list(page, size, visible, label=package_name)
        check_status_code(package_info_response)
        package_info = package_info_response.json()
        check_response(EXP_RESPONSE, package_info)
    return package_info


def get_deploy_package_by_name_and_version(paas_client: PAASClient, pkg_type, repository_type, package_name,
                                           package_version, **kwargs):
    """
    根据部署包名查询应用包信息

    :param paas_client: 登录信息
    :param pkg_type: 应用包类型
    :param repository_type: 私有仓库（false）/ 公有仓库（true）
    :param package_name: 应用包名
    :param package_version: 应用包版本
    :param kwargs:
    :return:
    """
    deploy_packages_response = paas_client.deploy_client.get_deploy_packages_list(pkg_type, repository_type, page=1,
                                                                                  size=100, **kwargs)
    exp_package = f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]"
    deploy_package = get_value_from_json(deploy_packages_response, exp_package, list_flag=True)
    return deploy_package
