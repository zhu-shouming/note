import os
import pathlib
import platform
from random import getrandbits

import yaml
from py.path import local

from resource.base.client import PAASClient
from resource.base.login import PAASLogin
from resource.utils.common import *


def setup_env():
    config_dir = local(pathlib.Path(__file__).parent).join('config')
    config_file = config_dir.join("env.yml")
    with open(config_file, 'r', encoding="utf-8") as f:
        settings = yaml.load(f, Loader=yaml.FullLoader)

    """ ##################################################################### """
    """ 登录 """

    user = PAASClient(PAASLogin(settings['USERNAME'], settings['PASSWORD'], settings['HOST'], settings['PORT']))

    proj_admin = PAASClient(PAASLogin(settings['PROJ_ADMIN'], settings['PASSWORD'], settings['HOST'], settings['PORT']))

    """ 获取CLUSTER_ID(云容器引擎-集群) """
    response = user.cce_client.get_cce_list()
    check_status_code(response, 200)
    cluster_name = settings['CLUSTER_NAME']
    expect_cluster = get_value_from_json(response, f"$.data[?(@.name=='{cluster_name}')]")
    assert expect_cluster, f"找不到指定的集群：{cluster_name}"
    cluster_id = expect_cluster["uuid"]
    settings['CLUSTER_ID'] = cluster_id

    """ 获取MCP_CLUSTER_ID """
    # response = user.app_mgmt_client.get_clusters_list_by_type("mcpCluster")
    # check_status_code(response, 200)
    # cluster_name = settings['MCP_CLUSTER_NAME']
    # expect_cluster = get_value_from_json(response, f"$.data[?(@.mcpName=='{cluster_name}')]")
    # assert expect_cluster, f"找不到指定的MCP集群：{cluster_name}"
    # mcp_cluster_id = expect_cluster["uuid"]
    # settings['MCP_CLUSTER_ID'] = mcp_cluster_id

    """ ##################################################################### """
    """ 创建tag """

    tag_name = "auto" + get_random_string(6, char_type=0).lower()
    create_tag_response = user.deploy_client.create_tag(tag_name)
    check_status_code(create_tag_response)
    settings['TAG'] = tag_name
    tags_list_response = user.deploy_client.get_tags_list()
    check_status_code(tags_list_response)
    tag_info = get_value_from_json(tags_list_response, f"$.data[?(@.tag=='{tag_name}')]")
    tag_id = tag_info['id']

    """ ##################################################################### """
    """ 上传应用包到公有&私有仓库 """

    if platform.system() == "Windows":
        settings['PACKAGE_PATH_OF_WAR'] = settings['PACKAGE_PATH_OF_WAR_WINDOWS']
        settings['PACKAGE_PATH_OF_JAR'] = settings['PACKAGE_PATH_OF_JAR_WINDOWS']
        settings['PACKAGE_PATH_OF_WEB'] = settings['PACKAGE_PATH_OF_WEB_WINDOWS']
        settings['PACKAGE_PATH_OF_HELM'] = settings['PACKAGE_PATH_OF_HELM_WINDOWS']
        settings['PACKAGE_PATH_OF_UPGRAGE_FROM_JAR'] = settings['PACKAGE_PATH_OF_UPGRAGE_FROM_JAR_WINDOWS']
        settings['PACKAGE_PATH_OF_ROLLBACK_FROM_JAR'] = settings['PACKAGE_PATH_OF_ROLLBACK_FROM_JAR_WINDOWS']
        settings['PACKAGE_PATH_OF_IMAGE'] = settings['PACKAGE_PATH_OF_IMAGE_WINDOWS']
    else:
        settings['PACKAGE_PATH_OF_WAR'] = settings['PACKAGE_PATH_OF_WAR_LINUX']
        settings['PACKAGE_PATH_OF_JAR'] = settings['PACKAGE_PATH_OF_JAR_LINUX']
        settings['PACKAGE_PATH_OF_WEB'] = settings['PACKAGE_PATH_OF_WEB_LINUX']
        settings['PACKAGE_PATH_OF_HELM'] = settings['PACKAGE_PATH_OF_HELM_LINUX']
        settings['PACKAGE_PATH_OF_UPGRAGE_FROM_JAR'] = settings['PACKAGE_PATH_OF_UPGRAGE_FROM_JAR_LINUX']
        settings['PACKAGE_PATH_OF_ROLLBACK_FROM_JAR'] = settings['PACKAGE_PATH_OF_ROLLBACK_FROM_JAR_LINUX']
        settings['PACKAGE_PATH_OF_IMAGE'] = settings['PACKAGE_PATH_OF_IMAGE_LINUX']

    package_paths_list = [
        {"type": "war", "path": settings['PACKAGE_PATH_OF_WAR'], "flag": "deploy"},
        {"type": "jar", "path": settings['PACKAGE_PATH_OF_JAR'], "flag": "deploy"},
        {"type": "web", "path": settings['PACKAGE_PATH_OF_WEB'], "flag": "deploy"},
        {"type": "helm", "path": settings['PACKAGE_PATH_OF_HELM'], "flag": "deploy"},
        {
            "type": "jar",
            "path_upgrade": settings['PACKAGE_PATH_OF_UPGRAGE_FROM_JAR'],
            "path_rollback": settings['PACKAGE_PATH_OF_ROLLBACK_FROM_JAR'],
            "flag": "upgrade",
        },
    ]

    os_type = platform.system()

    for i in range(len(package_paths_list)):
        # 应用包名称只能小写，否则部署不成功
        package_type = package_paths_list[i]["type"]
        package_name = "auto-" + package_type + "-" + get_random_string(5, char_type=0).lower()
        package_version = get_random_string(5, char_type=3)
        # 项目管理员上传包
        proj_package_name = "auto-" + package_type + "-" + get_random_string(5, char_type=0).lower()
        proj_package_version = get_random_string(5, char_type=3)
        flag = package_paths_list[i]["flag"]

        if flag == "deploy":
            packages_list = []
            file_path = package_paths_list[i]["path"]
            if os_type == "Windows":
                packages_list = file_path.split("\\")
            if os_type == "Linux":
                packages_list = file_path.split("/")
            file_name = packages_list[-1]  # 带后缀的文件名称
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            with open(file_path, mode='rb') as f:
                file_rb = f.read()
            # 上传到公有仓库
            upload_package_response = user.deploy_client.upload_package(package_name, package_version, tag_id,
                                                                        file_name, package_type, file_size, file_rb,
                                                                        True)
            check_status_code(upload_package_response)
            # 上传到私有仓库
            upload_package_response = user.deploy_client.upload_package(package_name, package_version, tag_id,
                                                                        file_name, package_type, file_size, file_rb,
                                                                        False)

            check_status_code(upload_package_response)
            # 将应用包名称和版本保存在settings中
            settings_name = "PACKAGE_NAME_OF_" + package_type.upper()
            settings_version = "PACKAGE_VERSION_OF_" + package_type.upper()
            settings[settings_name] = package_name
            settings[settings_version] = package_version
            # 项目管理员上传到私有仓库
            upload_package_response = proj_admin.deploy_client.upload_package(proj_package_name, proj_package_version,
                                                                              tag_id, file_name, package_type, file_size,
                                                                              file_rb, False)

            check_status_code(upload_package_response)
            settings_name = "PROJ_ADMIN_PACKAGE_NAME_OF_" + package_type.upper()
            settings_version = "PROJ_ADMIN_PACKAGE_VERSION_OF_" + package_type.upper()
            settings[settings_name] = proj_package_name
            settings[settings_version] = proj_package_version
        elif flag == "upgrade":
            # 上传第一个版本到公有仓库
            packages_list = []
            file_path = package_paths_list[i]["path_upgrade"]
            if os_type == "Windows":
                packages_list = file_path.split("\\")
            if os_type == "Linux":
                packages_list = file_path.split("/")
            file_name = packages_list[-1]  # 带后缀的文件名称
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            with open(file_path, mode='rb') as f:
                file_rb = f.read()
            upload_package_response = user.deploy_client.upload_package(package_name, package_version, tag_id,
                                                                        file_name, package_type, file_size, file_rb,
                                                                        True)
            check_status_code(upload_package_response)
            # 上传第一个版本到私有仓库
            upload_package_response = user.deploy_client.upload_package(package_name, package_version, tag_id,
                                                                        file_name, package_type, file_size, file_rb,
                                                                        False)
            check_status_code(upload_package_response)
            settings_upgrade_name = "PACKAGE_NAME_OF_UPGRAGE_FROM_" + package_type.upper()
            settings_upgrade_version = "PACKAGE_VERSION_OF_UPGRAGE_FROM_" + package_type.upper()
            settings[settings_upgrade_name] = package_name
            settings[settings_upgrade_version] = package_version
            # 项目管理员上传第一个版本到私有仓库
            upload_package_response = proj_admin.deploy_client.upload_package(proj_package_name, proj_package_version,
                                                                              tag_id, file_name, package_type, file_size,
                                                                              file_rb, False)
            check_status_code(upload_package_response)
            settings_upgrade_name = "PROJ_ADMIN_PACKAGE_NAME_OF_UPGRAGE_FROM_" + package_type.upper()
            settings_upgrade_version = "PROJ_ADMIN_PACKAGE_VERSION_OF_UPGRAGE_FROM_" + package_type.upper()
            settings[settings_upgrade_name] = proj_package_name
            settings[settings_upgrade_version] = proj_package_version
            # 上传第二个版本到公有仓库
            packages_list = []
            file_path = package_paths_list[i]["path_rollback"]
            if os_type == "Windows":
                packages_list = file_path.split("\\")
            if os_type == "Linux":
                packages_list = file_path.split("/")
            file_name = packages_list[-1]  # 带后缀的文件名称
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            with open(file_path, mode='rb') as f:
                file_rb = f.read()
            package_version = get_random_string(5, char_type=3)
            upload_package_response = user.deploy_client.upload_package(package_name, package_version, tag_id,
                                                                        file_name, package_type, file_size, file_rb,
                                                                        True)
            check_status_code(upload_package_response)
            # 上传第二个版本到私有仓库
            upload_package_response = user.deploy_client.upload_package(package_name, package_version, tag_id,
                                                                        file_name, package_type, file_size, file_rb,
                                                                        False)
            check_status_code(upload_package_response)
            settings_rollback_name = "PACKAGE_NAME_OF_ROLLBACK_FROM_" + package_type.upper()
            settings_rollback_version = "PACKAGE_VERSION_OF_ROLLBACK_FROM_" + package_type.upper()
            settings[settings_rollback_name] = package_name
            settings[settings_rollback_version] = package_version
            # 项目管理员上传第二个版本到私有仓库
            proj_package_version = get_random_string(5, char_type=3)
            upload_package_response = proj_admin.deploy_client.upload_package(proj_package_name, proj_package_version,
                                                                              tag_id, file_name, package_type,
                                                                              file_size, file_rb, False)
            check_status_code(upload_package_response)
            settings_upgrade_name = "PROJ_ADMIN_PACKAGE_NAME_OF_ROLLBACK_FROM_" + package_type.upper()
            settings_upgrade_version = "PROJ_ADMIN_PACKAGE_VERSION_OF_ROLLBACK_FROM_" + package_type.upper()
            settings[settings_upgrade_name] = proj_package_name
            settings[settings_upgrade_version] = proj_package_version

    """ ##################################################################### """
    """ 上传容器镜像包到公有镜像仓库 """

    img_path = settings['PACKAGE_PATH_OF_IMAGE']
    if os_type == "Windows":
        img_path = settings['PACKAGE_PATH_OF_IMAGE_WINDOWS']
    elif os_type == "Linux":
        img_path = settings['PACKAGE_PATH_OF_IMAGE_LINUX']

    # ------------ 如果是手动上传的镜像，则这里直接指定镜像名，不再使用随机名称 ------------
    # img_name = "mytomcatarm"
    img_name = "auto" + get_random_string(4).lower()
    # ---------------------------------------------------------------------------
    img_version = "v1"

    file_size = str(os.path.getsize(img_path))
    file_name = os.path.basename(img_path)

    # ------------ arm镜像太大容易导致失败，如果是手动上传的镜像，则这段直接注释掉 ------------
    with open(img_path, "rb") as f:
        file_data = f.read()
    data = {
        "chunkNumber": "1",
        "chunkSize": "204800000",
        "currentChunkSize": file_size,
        "totalSize": file_size,
        "identifier": str(file_size) + '-' + file_name.replace('.', ''),
        "filename": file_name,
        "relativePath": file_name,
        "totalChunks": "1",
        "description": "",
        "featureInfo": "",
        "file": (file_name, file_data, "application/x-tar"),
    }
    user_id = user.login_info.user_id
    res = user.ccr_client.upload_public_image(img_name, "default", img_version, user_id, data)

    check_status_code(res, 200)
    # -----------------------------------------------------------------------------

    settings['PACKAGE_NAME_OF_IMAGE'] = img_name
    settings['PACKAGE_VERSION_OF_IMAGE'] = img_version
    """ ##################################################################### """
    """ 指定ccr 和cce模块所用的镜像 """

    if os_type == "Windows":
        settings['cce_image'] = settings['PACKAGE_PATH_OF_CCE_WINDOWS']
    elif os_type == "Linux":
        settings['cce_image'] = settings['PACKAGE_PATH_OF_CCE_LINUX']

    """ 保存初始化变量 """
    config_dir = local(pathlib.Path(__file__).parent).join('config')
    config_file = config_dir.join("settings.yml")
    with open(config_file, 'w', encoding="utf-8") as f:
        yaml.dump(settings, f)
