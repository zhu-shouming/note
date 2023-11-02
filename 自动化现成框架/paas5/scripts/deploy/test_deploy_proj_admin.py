from sys import platform

import pytest
import allure
import os
import yaml

from config.config import settings
from resource.utils.common import *
from scripts.app_mgmt.handler_app_mgmt import *

cur_path = os.path.dirname(os.path.realpath(__file__))
if platform.system() == "Windows":
    dataPath = os.path.join(cur_path, 'data_proj_admin_win.yml')
else:
    dataPath = os.path.join(cur_path, 'data_proj_admin_linux.yml')

with open(dataPath, encoding='utf-8') as f:
    data_file = yaml.safe_load(f)


@allure.feature("应用管理")
@allure.story("应用仓库")
@pytest.mark.deploy
class TestDeploy:

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_upload_package'])
    def test_upload_package(self, paas_proj_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("1.应用包信息"):
            tag_name = settings['TAG']
            package_type = args['package_type']
            package_name = "auto-" + package_type + "-" + get_random_string(5, char_type=5).lower()
            package_version = get_random_string(5, char_type=3)
            file_path = args['file_path']
            repository = False
        with allure.step("2.上传应用包到私有仓库"):
            upload_package(paas_proj_admin_login, package_name, package_version, tag_name, package_type, file_path,
                           repository)
        with allure.step("TEARDOWN：删除应用包"):
            delete_package(paas_proj_admin_login, package_name, [package_version], repository)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_apply_for_publishing_package_to_public'])
    def test_apply_for_publishing_package_to_public(self, paas_admin_login, paas_proj_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 上传应用包到私有仓库"):
            tag_name = settings['TAG']
            package_type = args['package_type']
            package_name = "auto-" + package_type + "-" + get_random_string(5, char_type=3).lower()
            package_version = get_random_string(5, char_type=3)
            file_path = args['file_path']
            repository = False
            upload_package(paas_proj_admin_login, package_name, package_version, tag_name, package_type, file_path,
                           repository)
        with allure.step("2.申请发布应用包到公有仓库"):
            apply_for_publishing_package(paas_proj_admin_login, package_name, package_version)
        with allure.step("3.当前默认流程是一级审批"):
            time.sleep(3)
            processes_info = get_processes_by_kwargs(paas_admin_login, status="PROCESSING", nameLike=package_name,
                                                     createUserNameLike=settings['PROJ_ADMIN'],
                                                     nextCandidateUser=settings['USERNAME'])
            assert len(processes_info['data']) > 0, "无指定审批流程"
            exp_ids = "$.data[*].id"
            processes_ids = jsonpath.jsonpath(processes_info, exp_ids)
            approve_processes(paas_admin_login, processes_ids, True, "OK")
        with allure.step("TEARDOWN：删除公有&私有仓库应用包"):
            time.sleep(5)
            # 公有仓库只有系统管理员有删除权限
            delete_package(paas_admin_login, package_name, [package_version], visible=True)
            delete_package(paas_proj_admin_login, package_name, [package_version], visible=False)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_delete_package_with_more_visions'])
    def test_delete_package_with_more_visions(self, paas_proj_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 上传应用包"):
            tag_name = settings['TAG']
            package_type = args['package_type']
            file_path = args['file_path']
            repository = False
            package_versions = []
            # 应用包名称只能小写，否则部署不成功
            package_name = "auto-" + package_type + "-" + get_random_string(5, char_type=3).lower()
            for i in range(args['version_numbers']):
                package_version = get_random_string(5, char_type=3)
                upload_package(paas_proj_admin_login, package_name, package_version, tag_name, package_type, file_path,
                               repository)
                package_versions.append(package_version)
            # 查看应用包是否上传成功
            package_info = get_package_by_name(paas_proj_admin_login, package_name, visible=repository)
            assert len(package_info['data']) > 0, f"未找到上传应用包：{package_name}"
            # 查看应用包的各个版本是否上传成功
            for package_version in package_versions:
                package_version_info = get_value_from_json(package_info,
                                                           f"$.data[?(@.name=='{package_name}')].versions[?(@.version=='{package_version}')]")
                assert package_version_info, f"上传应用包：{package_name}的版本：{package_version}失败"
        with allure.step("TEARDOWN：删除应用包"):
            delete_package(paas_proj_admin_login, package_name, package_versions, repository)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_upload_package'])
    @allure.description("下载应用包")
    def test_download_package(self, paas_proj_admin_login, args):
        show_testcase_title("项目管理员 -- 下载" + args['title'])
        with allure.step("SETUP: 上传应用包"):
            tag_name = settings['TAG']
            package_version = get_random_string(5, char_type=3)
            package_type = args['package_type']
            package_name = "auto-" + package_type + "-" + get_random_string(5, char_type=3).lower()
            file_path = args['file_path']
            repository = False
            upload_package(paas_proj_admin_login, package_name, package_version, tag_name, package_type, file_path,
                           repository)
            original_size = os.stat(file_path).st_size
        with allure.step("下载应用包"):
            downloaded_file = download_package(paas_proj_admin_login, package_name, package_version, repository)
            current_size = os.stat(downloaded_file).st_size
            assert original_size == current_size, f"文件下载前后大小不一致"
        with allure.step("TEARDOWN：删除应用包"):
            delete_package(paas_proj_admin_login, package_name, [package_version], repository)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_deploy_package_of_war'])
    @allure.description("项目管理员从应用仓库部署war包应用")
    def test_deploy_package_of_war(self, paas_proj_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("1.应用包信息"):
            # 应用包名称只能小写，否则部署不成功
            package_name = "auto" + get_random_string(6, char_type=0).lower()
            package_version = get_random_string(5, char_type=3)
            package_type = args['package_type']
            tag_name = settings['TAG']
            file_path = args['file_path']
            repository = False
        with allure.step("2.填写上传应用包"):
            upload_package(paas_proj_admin_login, package_name, package_version, tag_name, package_type, file_path,
                           repository)
        with allure.step("3.创建应用组并部署应用且应用正常对外提供服务"):
            cluster_name = settings['CLUSTER_NAME']
            container_spec = args['container_spec']
            svc_access_control = args['svc_access_control']
            # 随机生成集群外访问端口
            node_port = generate_svc_port(paas_proj_admin_login)
            node_port_info = {
                "nodePort": node_port
            }
            svc_access_control.update(node_port_info)
            app_svc_info = args['app_svc_info']
            app_info_init = setup_create_war_app(paas_proj_admin_login, cluster_name, package_name, package_version,
                                                 container_spec, svc_access_control, app_svc_info, repository,
                                                 engine_type="others")
            app_name = app_info_init['data'][0]['name']
            app_group_name = app_info_init['data'][0]['app_group_name']
        with allure.step("3.校验应用创建结果"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_proj_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_html_status(paas_proj_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 1.删除应用组"):
            delete_app_group_by_name(paas_proj_admin_login, app_group_name)
            check_del_result_timeout(get_app_group_by_name, paas_client=paas_proj_admin_login, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 2.删除应用包"):
            package_version = [package_version]
            delete_package(paas_proj_admin_login, package_name, package_version, repository)

