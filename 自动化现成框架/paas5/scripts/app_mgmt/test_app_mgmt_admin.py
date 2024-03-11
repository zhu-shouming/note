import pytest
import allure
import os
import yaml

from scripts.app_mgmt.handler_app_mgmt import *
from scripts.cce.handler_cce import *

cur_path = os.path.dirname(os.path.realpath(__file__))
dataPath = os.path.join(cur_path, 'data_admin.yml')
with open(dataPath, encoding='utf-8') as f:
    data_file = yaml.safe_load(f)


@allure.feature("应用管理")
@allure.story("应用组")
@pytest.mark.appmgmt
class TestAppMgmt:

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_app_group'])
    @allure.description("新建基于SpringCloud/ Istio/ 自定义微服务引擎的应用组")
    def test_create_app_group(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        app_group_name = "auto" + get_random_string(6, char_type=0).lower()
        engine_type = args['engine_type']
        engine_name = ""
        engine_id = ""
        if engine_type == "Spring Cloud":
            engine_info = new_spingcloud_engine(paas_admin_login)
            engine_name = engine_info['name']
            engine_id = engine_info['id']
        with allure.step("1.创建应用组"):
            create_app_group(paas_admin_login, app_group_name, engine_type=engine_type, svc_engine_id=engine_id)
            exp_status = "running"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_group_by_name, paas_client=paas_admin_login,
                                 app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组和微服务引擎"):
            delete_app_group_by_name(paas_admin_login, app_group_name)
            if engine_type == "Spring Cloud":
                delete_micro_engine(paas_admin_login, engine_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_app_group'])
    @allure.description("新建基于SpringCloud/ Istio/ 自定义微服务引擎的带有ns的应用组")
    def test_create_app_group_with_ns(self, paas_admin_login, args):
        show_testcase_title(args['title'] + "带NS")
        app_group_name = "auto" + get_random_string(6, char_type=0).lower()
        namespace = "auto" + get_random_string(5, char_type=3).lower()
        engine_type = args['engine_type']
        engine_name = ""
        engine_id = ""
        if engine_type == "Spring Cloud":
            engine_info = new_spingcloud_engine(paas_admin_login)
            engine_name = engine_info['name']
            engine_id = engine_info['id']
        with allure.step("1.创建应用组"):
            create_app_group(paas_admin_login, app_group_name, namespace=namespace, engine_type=engine_type,
                             svc_engine_id=engine_id)
            exp_status = "running"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_group_by_name, paas_client=paas_admin_login,
                                 app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组和微服务引擎"):
            delete_app_group_by_name(paas_admin_login, app_group_name)
            if engine_type == "Spring Cloud":
                delete_micro_engine(paas_admin_login, engine_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args1', data_file['setup_create_war_app'])
    @pytest.mark.parametrize('args', data_file['test_action_app_group_with_war'])
    @allure.description("停止/启动部署有war包的自定义应用组")
    def test_action_app_group_with_war(self, paas_admin_login, args1, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组并部署应用且应用正常对外提供服务"):
            cluster_name = settings['CLUSTER_NAME']
            package_name = settings['PACKAGE_NAME_OF_WAR']
            package_version = settings['PACKAGE_VERSION_OF_WAR']
            container_spec = args1['container_spec']
            svc_access_control = args1['svc_access_control']
            app_svc_info = args1['app_svc_info']
            # 缺省部署到公有仓库
            app_info = setup_create_war_app(paas_admin_login, cluster_name, package_name, package_version,
                                            container_spec, svc_access_control, app_svc_info, engine_type="others")
        with allure.step("1.停止应用组"):
            app_name = app_info['data'][0]['name']
            app_group_name = app_info['data'][0]['app_group_name']
            action_stop = args['action_stop']
            status_running = "running"
            exp_stopped = "stopped"
            action_app_group(paas_admin_login, app_group_name, action_stop, status_running)
            exp_path = "$.data[0].status"
            # 应用状态变化
            check_status_timeout("Stopped", exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
            check_status_timeout(exp_stopped, exp_path, get_app_group_by_name, paas_client=paas_admin_login,
                                 app_group_name=app_group_name)
        with allure.step("2.启动应用组"):
            action_start = args['action_start']
            status_stopped = "stopped"
            exp_running = "running"
            action_app_group(paas_admin_login, app_group_name, action_start, status_stopped)
            exp_path = "$.data[0].status"
            check_status_timeout("OK", exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
            check_status_timeout(exp_running, exp_path, get_app_group_by_name, paas_client=paas_admin_login,
                                 app_group_name=app_group_name)
        with allure.step("TEARDOWN：清理资源"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_jar_app_with_spring_cloud'])
    @allure.description("部署基于SpringCloud微服务引擎应用组的jar包应用")
    def test_create_jar_app_with_spring_cloud(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建基于Spring Cloud微服务引擎的应用组"):
            package_name = settings['PACKAGE_NAME_OF_JAR']
            package_version = settings['PACKAGE_VERSION_OF_JAR']
            app_group_info = setup_create_app_group(paas_admin_login)
            app_group_name = app_group_info['name']
            engine_name = app_group_info['engine_name']
        with allure.step("1.填写应用信息"):
            with allure.step("1-1.创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
                # 当前页面只有"容器集群"
                resource_type = "container" if args['resource_type'] == "容器集群" else "edge"
                app_type_info = {}
                app_type = args['app_type']
                if app_type == '无状态应用':
                    app_type_info = {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment"
                    }
                cluster_info = {
                    "cluster_type": "kaasCluster" if args['cluster_info']['cluster_type'] == "独享集群" else "",
                    "cluster_name": settings['CLUSTER_NAME']
                }
            with allure.step("1-2.创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": True if args['repository'] == "公有" else False,
                    "package_name": package_name,
                    "package_version": package_version
                }
                # 容器规格
                container_spec = {
                    "cpu_request": args['container_spec']['cpu_request'],
                    "mem_request": args['container_spec']['mem_request'],
                    "cpu_limit": args['container_spec']['cpu_limit'],
                    "mem_limit": args['container_spec']['mem_limit']
                }
                # JDK版本
                jdk_version = args['jdk_version']
                # 服务访问控制
                svc_access_control_info = {}
                if 'svc_access_control' in args.keys():
                    svc_access_control_info = {
                        "dns_policy": "ClusterFirst" if args['svc_access_control'][
                                                            'dns_policy'] == "集群外访问" else "ClusterFirst",
                        "targetPort": args['svc_access_control']['targetPort'],
                        "port": args['svc_access_control']['port']
                    }
                    # 随机生成集群外访问端口
                    node_port = generate_svc_port(paas_admin_login)
                    node_port_info = {
                        "nodePort": node_port
                    }
                    svc_access_control_info.update(node_port_info)
        with allure.step("2.创建应用"):
            create_jar_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
                           app_type_info, cluster_info, app_package_info, container_spec, jdk_version,
                           svc_access_control_info=svc_access_control_info)
        with allure.step("3.校验应用创建结果"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_app_svc_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 清理资源"):
            with allure.step("1).删除应用组"):
                delete_app_group_by_name(paas_admin_login, app_group_name)
            with allure.step("2).删除微服务引擎"):
                delete_micro_engine(paas_admin_login, engine_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args1', data_file['setup_create_image_app'])
    @pytest.mark.parametrize('args', data_file['test_action_app_with_image'])
    @allure.description("重启/停止/启动容器镜像包的应用")
    def test_action_app_with_image(self, paas_admin_login, args1, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组并部署应用且应用正常对外提供服务"):
            cluster_name = settings['CLUSTER_NAME']
            package_name = settings['PACKAGE_NAME_OF_IMAGE']
            package_version = settings['PACKAGE_VERSION_OF_IMAGE']
            container_spec = args1['container_spec']
            svc_access_control = args1['svc_access_control']
            app_svc_info = args1['app_svc_info']
            app_info_init = setup_create_image_app(paas_admin_login, cluster_name, package_name, package_version,
                                                   container_spec, svc_access_control, app_svc_info, engine_type="Istio")
        with allure.step("1.重启应用"):
            app_name = app_info_init['data'][0]['name']
            app_group_name = app_info_init['data'][0]['app_group_name']
            action_restart = args['action_restart']
            current_status = "OK"
            exp_status = "OK"
            action_app_info = action_app(paas_admin_login, app_name, action_restart, current_status, app_group_name)
            assert action_app_info['data'] is True, f"重启{app_name}失败"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
            check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("2.停止应用"):
            action_stop = args['action_stop']
            current_status = "OK"
            exp_status = "Stopped"
            action_app_info = action_app(paas_admin_login, app_name, action_stop, current_status, app_group_name)
            assert action_app_info['data'] is True, f"停止{app_name}失败"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("3.启动应用"):
            action_start = args['action_start']
            current_status = "Stopped"
            exp_status = "OK"
            action_app_info = action_app(paas_admin_login, app_name, action_start, current_status, app_group_name)
            assert action_app_info['data'] is True, f"启动{app_name}失败"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
            check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L0
    @pytest.mark.parametrize('args1', data_file['setup_create_jar_app'])
    @pytest.mark.parametrize('args', data_file['test_upgrade_and_rollback_jar_app'])
    @allure.description("升级和回滚jar包应用")
    def test_upgrade_and_rollback_jar_app(self, paas_admin_login, args1, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组并部署应用且应用正常对外提供服务"):
            cluster_name = settings['CLUSTER_NAME']
            package_name = settings['PACKAGE_NAME_OF_UPGRAGE_FROM_JAR']
            package_version = settings['PACKAGE_VERSION_OF_UPGRAGE_FROM_JAR']
            container_spec = args1['container_spec']
            svc_access_control = args1['svc_access_control']
            old_app_svc_info = args1['app_svc_info']
            app_info_init = setup_create_jar_app(paas_admin_login, cluster_name, package_name, package_version,
                                                 container_spec, svc_access_control, old_app_svc_info,
                                                 engine_type="others")
        with allure.step("1.升级应用"):
            app_name = app_info_init['data'][0]['name']
            app_group_name = app_info_init['data'][0]['app_group_name']
            app_package_info = {
                "package_name": settings['PACKAGE_NAME_OF_ROLLBACK_FROM_JAR'],
                "package_version": settings['PACKAGE_VERSION_OF_ROLLBACK_FROM_JAR']
            }
            upgrade_jar_app(paas_admin_login, app_name, app_package_info)
        with allure.step("2.检查应用是否升级成功"):
            new_app_svc_info = args['app_svc_info']
            check_app_svc_status(paas_admin_login, app_name, new_app_svc_info)
        with allure.step("3.回滚应用"):
            rollback_jar_app(paas_admin_login, app_name)
        with allure.step("2.检查应用是否回滚成功"):
            old_app_svc_info = {
                "app_uri": args1['app_svc_info']['app_uri'],
                "app_message": args1['app_svc_info']['app_message']
            }
            check_app_svc_status(paas_admin_login, app_name, old_app_svc_info)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_war_app'])
    @allure.description("部署war包应用")
    def test_create_war_app(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组"):
            package_name = settings['PACKAGE_NAME_OF_WAR']
            package_version = settings['PACKAGE_VERSION_OF_WAR']
            app_group_info = setup_create_app_group(paas_admin_login, engine_type="others")
            app_group_name = app_group_info['name']
        with allure.step("1.填写应用信息"):
            with allure.step("1-1.创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
                # 当前页面只有"容器集群"
                resource_type = "container" if args['resource_type'] == "容器集群" else "edge"
                app_type_info = {}
                app_type = args['app_type']
                if app_type == '无状态应用':
                    app_type_info = {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment"
                    }
                cluster_info = {
                    "cluster_type": "kaasCluster" if args['cluster_info']['cluster_type'] == "独享集群" else "",
                    "cluster_name": settings['CLUSTER_NAME']
                }
            with allure.step("1-2.创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": True if args['repository'] == "公有" else False,
                    "package_name": package_name,
                    "package_version": package_version
                }
                # 容器规格
                container_spec = {
                    "cpu_request": args['container_spec']['cpu_request'],
                    "mem_request": args['container_spec']['mem_request'],
                    "cpu_limit": args['container_spec']['cpu_limit'],
                    "mem_limit": args['container_spec']['mem_limit']
                }
                # TOMCAT版本
                tomcat_version = args['tomcat_version']
                # JDK版本
                jdk_version = args['jdk_version']
                # 服务访问控制
                svc_access_control_info = {}
                if 'svc_access_control' in args.keys():
                    svc_access_control_info = {
                        "dns_policy": "ClusterFirst" if args['svc_access_control'][
                                                            'dns_policy'] == "集群外访问" else "ClusterFirst",
                        "targetPort": args['svc_access_control']['targetPort'],
                        "port": args['svc_access_control']['port']
                    }
                    # 随机生成集群外访问端口
                    node_port = generate_svc_port(paas_admin_login)
                    node_port_info = {
                        "nodePort": node_port
                    }
                    svc_access_control_info.update(node_port_info)
        with allure.step("2.创建应用"):
            create_war_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
                           app_type_info, cluster_info, app_package_info, container_spec, tomcat_version, jdk_version,
                           svc_access_control_info=svc_access_control_info)
        with allure.step("3.校验应用创建结果"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_front_app'])
    @allure.description("部署前端包应用")
    def test_create_front_app(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组"):
            package_name = settings['PACKAGE_NAME_OF_WEB']
            package_version = settings['PACKAGE_VERSION_OF_WEB']
            app_group_info = setup_create_app_group(paas_admin_login, engine_type="others")
            app_group_name = app_group_info['name']
        with allure.step("1.填写应用信息"):
            with allure.step("1-1.创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
                # 当前页面只有"容器集群"
                resource_type = "container" if args['resource_type'] == "容器集群" else "edge"
                app_type_info = {}
                app_type = args['app_type']
                if app_type == '无状态应用':
                    app_type_info = {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment"
                    }
                cluster_info = {
                    "cluster_type": "kaasCluster" if args['cluster_info']['cluster_type'] == "独享集群" else "",
                    "cluster_name": settings['CLUSTER_NAME']
                }
            with allure.step("1-2.创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": True if args['repository'] == "公有" else False,
                    "package_name": package_name,
                    "package_version": package_version
                }
                # 容器规格
                container_spec = {
                    "cpu_request": args['container_spec']['cpu_request'],
                    "mem_request": args['container_spec']['mem_request'],
                    "cpu_limit": args['container_spec']['cpu_limit'],
                    "mem_limit": args['container_spec']['mem_limit']
                }
                # TOMCAT版本
                tomcat_version = args['tomcat_version']
                # JDK版本
                jdk_version = args['jdk_version']
                # NGINX版本
                nginx_version = args['nginx_version']
                # 服务访问控制
                svc_access_control_info = {}
                if 'svc_access_control' in args.keys():
                    svc_access_control_info = {
                        "dns_policy": "ClusterFirst" if args['svc_access_control'][
                                                            'dns_policy'] == "集群外访问" else "ClusterFirst",
                        "targetPort": args['svc_access_control']['targetPort'],
                        "port": args['svc_access_control']['port']
                    }
                    # 随机生成集群外访问端口
                    node_port = generate_svc_port(paas_admin_login)
                    node_port_info = {
                        "nodePort": node_port
                    }
                    svc_access_control_info.update(node_port_info)
        with allure.step("2.创建应用"):
            create_front_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
                             app_type_info, cluster_info, app_package_info, container_spec, tomcat_version,
                             jdk_version, nginx_version, svc_access_control_info=svc_access_control_info)
        with allure.step("3.校验应用运行状态"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_helm_app'])
    @allure.description("部署helm包应用")
    def test_create_helm_app(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组"):
            package_name = settings['PACKAGE_NAME_OF_HELM']
            package_version = settings['PACKAGE_VERSION_OF_HELM']
            app_group_info = setup_create_app_group(paas_admin_login, engine_type="others")
            app_group_name = app_group_info['name']
            app_group_ns = app_group_info['namespace']
        with allure.step("1.填写应用信息"):
            with allure.step("1-1.创建应用第一步"):
                app_name_prefix = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
                # 当前页面只有"容器集群"
                resource_type = "container" if args['resource_type'] == "容器集群" else "edge"
                cluster_info = {
                    "cluster_type": "kaasCluster" if args['cluster_info']['cluster_type'] == "独享集群" else "",
                    "cluster_name": settings['CLUSTER_NAME']
                }
            with allure.step("1-2.创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": True if args['repository'] == "公有" else False,
                    "package_name": package_name,
                    "package_version": package_version
                }
                # 容器规格
                container_spec = {
                    "quota_cpu": args['container_spec']['quota_cpu'],
                    "quota_memory": args['container_spec']['quota_memory'],
                    "quota_storage": args['container_spec']['quota_storage']
                }
                allure.attach(
                    f"应用仓库：{app_package_info['repository']}\n"
                    f"应用包名称：{package_name}\n"
                    f"应用包版本：{package_version}\n"
                    f"配额：CPU： {container_spec['quota_cpu']} 核, 内存: {container_spec['quota_memory']} MB\n",
                    name="创建应用第二步填写的信息")
        with allure.step("2.创建应用"):
            create_helm_app(paas_admin_login, app_name_prefix, app_version, app_group_name, resource_type,
                            cluster_info, app_package_info, container_spec)
        with allure.step("3.校验应用运行状态"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            app_name = app_name_prefix + "-" + app_group_ns + "-" + args['application_name']
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_app_svc_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_image_app'])
    @allure.description("部署容器镜像包应用")
    def test_create_image_app(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建应用组"):
            package_name = settings['PACKAGE_NAME_OF_IMAGE']
            package_version = settings['PACKAGE_VERSION_OF_IMAGE']
            app_group_info = setup_create_app_group(paas_admin_login, engine_type="Istio")
            app_group_name = app_group_info['name']
        with allure.step("1.填写应用信息"):
            with allure.step("1-1.创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
                # 当前页面只有"容器集群"
                resource_type = "container" if args['resource_type'] == "容器集群" else "edge"
                app_type_info = {}
                app_type = args['app_type']
                if app_type == '无状态应用':
                    app_type_info = {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment"
                    }
                cluster_info = {
                    "cluster_type": "kaasCluster" if args['cluster_info']['cluster_type'] == "独享集群" else "",
                    "cluster_name": settings['CLUSTER_NAME']
                }
            with allure.step("1-2.创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": True if args['repository'] == "公有" else False,
                    "package_name": package_name,
                    "package_version": package_version
                }
                # 容器规格
                container_spec = {
                    "cpu_request": args['container_spec']['cpu_request'],
                    "mem_request": args['container_spec']['mem_request'],
                    "cpu_limit": args['container_spec']['cpu_limit'],
                    "mem_limit": args['container_spec']['mem_limit']
                }
                # 服务访问控制
                svc_access_control_info = {}
                if 'svc_access_control' in args.keys():
                    svc_access_control_info = {
                        "dns_policy": "ClusterFirst" if args['svc_access_control'][
                                                            'dns_policy'] == "集群外访问" else "ClusterFirst",
                        "targetPort": args['svc_access_control']['targetPort'],
                        "port": args['svc_access_control']['port']
                    }
                    # 随机生成集群外访问端口
                    node_port = generate_svc_port(paas_admin_login)
                    node_port_info = {
                        "nodePort": node_port
                    }
                    svc_access_control_info.update(node_port_info)
        with allure.step("2.创建应用"):
            create_image_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
                             app_type_info, cluster_info, app_package_info, container_spec,
                             svc_access_control_info=svc_access_control_info)
        with allure.step("3.校验应用创建结果"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @allure.title("批量删除应用")
    @pytest.mark.parametrize('args1', data_file['setup_create_war_and_front_app'])
    @pytest.mark.parametrize('args', data_file['test_delete_apps_patch'])
    def test_delete_apps_patch(self, paas_admin_login, args1, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建war包和前端包应用"):
            cluster_name = settings['CLUSTER_NAME']
            package_info = {
                "war": {
                    "package_name": settings['PACKAGE_NAME_OF_WAR'],
                    "package_version": settings['PACKAGE_VERSION_OF_WAR']
                },
                "front": {
                    "package_name": settings['PACKAGE_NAME_OF_WEB'],
                    "package_version": settings['PACKAGE_VERSION_OF_WEB']
                }
            }
            container_spec = args1['container_spec']
            svc_access_control = args1['svc_access_control']
            app_svc_info = args1['app_svc_info']
            apps_info_init = setup_create_war_and_front_app(paas_admin_login, cluster_name, package_info, container_spec,
                                                            svc_access_control, app_svc_info, engine_type="others")
            app_group_name = apps_info_init['data'][0]['app_group_name']
        with allure.step("批量删除应用"):
            exp_names_path = f"$.data[*].name"
            app_names = get_value_from_json(apps_info_init, exp_names_path, list_flag=True)
            delete_pvc = args['delete_pvc']
            delete_apps_patch_by_names(paas_admin_login, app_names, delete_pvc)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_front_app'])
    @allure.title("系统管理员 -- 弹性伸缩应用")
    def test_scale_front_app(self, paas_admin_login, args):
        with allure.step("SETUP"):
            with allure.step("1.创建应用组并部署应用且应用正常对外提供服务"):
                cluster_name = settings['CLUSTER_NAME']
                package_name = settings['PACKAGE_NAME_OF_WEB']
                package_version = settings['PACKAGE_VERSION_OF_WEB']
                container_spec = args['container_spec']
                svc_access_control = args['svc_access_control']
                app_svc_info = args['app_svc_info']
                app_info_init = setup_create_front_app(paas_admin_login, cluster_name, package_name, package_version,
                                                       container_spec, svc_access_control, app_svc_info,
                                                       engine_type="others")
                assert len(app_info_init['data']) > 0, f"初始化创建前端包失败"
                app_info = app_info_init['data'][0]
                app_name = app_info['name']
                app_group_name = app_info['app_group_name']
                # 获取应用当前规格
                resources = app_info['metadata']['image_metadata']['metadata']['resources'][1]['spec']['template']['spec']['containers'][0]['resources']
        with allure.step("2.扩容"):   # 扩容规格= current*2，组装扩容请求
            new_resources = {
                "limits": {
                    "cpu": str(int(float(resources['limits']['cpu']) * 2)),
                    "memory": str(int(float(resources['limits']['memory'].split('Mi')[0]) * 2)) + 'Mi'
                },
                "requests": {
                    "cpu": str(int(float(resources['requests']['cpu']) * 2)),
                    "memory": str(int(float(resources['requests']['memory'].split('Mi')[0]) * 2)) + 'Mi'
                }
            }
            scale_app(paas_admin_login, app_name, new_resources)
        with allure.step("3.缩容"):
            scale_app(paas_admin_login, app_name, resources)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_jar_app_with_storage'])
    @allure.description("部署jar包应用并挂在存储卷")
    def test_create_jar_app_with_storage(self, paas_admin_login, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP: 创建自定义应用组"):
            package_name = settings['PACKAGE_NAME_OF_UPGRAGE_FROM_JAR']
            package_version = settings['PACKAGE_VERSION_OF_UPGRAGE_FROM_JAR']
            app_group_info = setup_create_app_group(paas_admin_login, engine_type="others")
            app_group_name = app_group_info['name']
        with allure.step("1.填写应用信息"):
            with allure.step("1-1.创建应用第一步"):
                app_name = get_random_string(5).lower()
                app_version = get_random_string(5, 3)
                deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
                # 当前页面只有"容器集群"
                resource_type = "container" if args['resource_type'] == "容器集群" else "edge"
                app_type_info = {}
                app_type = args['app_type']
                if app_type == '无状态应用':
                    app_type_info = {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment"
                    }
                cluster_info = {
                    "cluster_type": "kaasCluster" if args['cluster_info']['cluster_type'] == "独享集群" else "",
                    "cluster_name": settings['CLUSTER_NAME']
                }
            with allure.step("1-2.创建应用第二步"):
                # 应用安装包
                app_package_info = {
                    "repository": True if args['repository'] == "公有" else False,
                    "package_name": package_name,
                    "package_version": package_version
                }
                # 容器规格
                container_spec = {
                    "cpu_request": args['container_spec']['cpu_request'],
                    "mem_request": args['container_spec']['mem_request'],
                    "cpu_limit": args['container_spec']['cpu_limit'],
                    "mem_limit": args['container_spec']['mem_limit']
                }
                # JDK版本
                jdk_version = args['jdk_version']
                # 服务访问控制
                svc_access_control_info = {}
                if 'svc_access_control' in args.keys():
                    svc_access_control_info = {
                        "dns_policy": "ClusterFirst" if args['svc_access_control'][
                                                            'dns_policy'] == "集群外访问" else "ClusterFirst",
                        "targetPort": args['svc_access_control']['targetPort'],
                        "port": args['svc_access_control']['port']
                    }
                    # 随机生成集群外访问端口
                    node_port = generate_svc_port(paas_admin_login)
                    node_port_info = {
                        "nodePort": node_port
                    }
                    svc_access_control_info.update(node_port_info)
                # 挂载存储
                pvs = args['pv']
                pvc_resource = {
                    "pv": [],
                    "pvc": []
                }
                volume_mounts = []
                volumes = []

                for item in pvs:
                    temp_pv_dict = {}
                    temp_name = app_name + get_random_string(3, char_type=0).lower() + "pvc"

                    if item['type'] == "动态供给":
                        temp_pv_dict = {
                            "clusterId": settings['CLUSTER_ID'],
                            "data": {
                                "accessMode": "ReadWriteOnce" if item[
                                                                     'access_mode'] == "单节点读写" else "ReadWriteOnce",
                                "capacity": (item['capacity'].split('M')[0] + "Mi") if 'M' in item[
                                    'capacity'] else (item['capacity'].split('G')[0] + "Gi"),
                                "storageClass": item['storage_class']
                            },
                            "pvcName": temp_name,
                            "type": "dynamic",
                            "volumeType": None
                        }
                    pvc_resource['pv'].append(temp_pv_dict)

                    temp_vol_dict = {
                        "name": temp_name,
                        "mountPath": item['container_path']
                    }
                    volume_mounts.append(temp_vol_dict)

                    temp_volumes = {
                        "name": temp_name,
                        "persistentVolumeClaim": {
                            "claimName": temp_name
                        }
                    }
                    volumes.append(temp_volumes)
        with allure.step("2.创建应用"):
            create_jar_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
                           app_type_info, cluster_info, app_package_info, container_spec, jdk_version,
                           svc_access_control_info=svc_access_control_info, pvc_resource=pvc_resource,
                           volume_mounts=volume_mounts, volumes=volumes)
        with allure.step("3.校验应用创建结果"):
            exp_status = "OK"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
                                 app_group_name=app_group_name)
        with allure.step("4.验证应用正常对外提供服务"):
            app_svc_info = {
                "app_uri": args['app_svc_info']['app_uri'],
                "app_message": args['app_svc_info']['app_message']
            }
            check_app_svc_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
        with allure.step("TEARDOWN: 删除应用组"):
            delete_app_group_by_name(paas_admin_login, app_group_name)

    """ MCP用例 """

    # @pytest.mark.L5
    # @pytest.mark.parametrize('args', data_file['test_create_jar_app_with_spring_cloud_on_mcp'])
    # @allure.description("在MCP部署基于SpringCloud微服务引擎应用组的jar包应用")
    # def test_create_jar_app_with_spring_cloud_on_mcp(self, paas_admin_login, args):
    #     show_testcase_title(args['title'])
    #     with allure.step("SETUP: 创建基于Spring Cloud微服务引擎的应用组"):
    #         package_name = settings['PACKAGE_NAME_OF_JAR']
    #         package_version = settings['PACKAGE_VERSION_OF_JAR']
    #         app_group_info = setup_create_app_group(paas_admin_login)
    #         app_group_name = app_group_info['name']
    #         engine_name = app_group_info['engine_name']
    #     with allure.step("1.创建应用"):
    #         app_name = get_random_string(5).lower()
    #         app_version = get_random_string(5, 3)
    #         deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
    #         resource_type = args['resource_type'].lower()
    #         app_type_info = {}
    #         app_type = args['app_type']
    #         if app_type == '无状态应用':
    #             app_type_info = {
    #                 "apiVersion": "apps/v1",
    #                 "kind": "Deployment"
    #             }
    #         cluster_info = {
    #             "cluster_type": "mcpCluster" if args['cluster_info']['cluster_type'] == "MCP集群" else "",
    #             "cluster_name": settings['CLUSTER_NAME']
    #         }
    #         # 应用安装包
    #         app_package_info = {
    #             "repository": True if args['repository'] == "公有" else False,
    #             "package_name": package_name,
    #             "package_version": package_version
    #         }
    #         # 容器规格
    #         container_spec = {
    #             "cpu_request": args['container_spec']['cpu_request'],
    #             "mem_request": args['container_spec']['mem_request'],
    #             "cpu_limit": args['container_spec']['cpu_limit'],
    #             "mem_limit": args['container_spec']['mem_limit']
    #         }
    #         # JDK版本
    #         jdk_version = args['jdk_version']
    #         # 服务访问控制
    #         svc_access_control_info = {}
    #         if 'svc_access_control' in args.keys():
    #             svc_access_control_info = {
    #                 "dns_policy": "ClusterFirst" if args['svc_access_control'][
    #                                                     'dns_policy'] == "集群外访问" else "ClusterFirst",
    #                 "targetPort": args['svc_access_control']['targetPort'],
    #                 "port": args['svc_access_control']['port']
    #             }
    #             # 随机生成集群外访问端口
    #             node_port = generate_svc_port(paas_admin_login)
    #             node_port_info = {
    #                 "nodePort": node_port
    #             }
    #             svc_access_control_info.update(node_port_info)
    #         # 查询边缘节点
    #         mcp_plaintext_list = get_mcp_nodes_list(paas_admin_login, settings['MCP_CLUSTER_NAME'])
    #         # 创建应用
    #         create_jar_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
    #                        app_type_info, cluster_info, app_package_info, container_spec, jdk_version,
    #                        mcp_plaintext_list=mcp_plaintext_list, svc_access_control_info=svc_access_control_info)
    #     with allure.step("2.校验应用创建结果"):
    #         exp_status = "OK"
    #         exp_path = "$.data[0].status"
    #         check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
    #                              app_group_name=app_group_name)
    #     with allure.step("3.验证应用正常对外提供服务"):
    #         app_svc_info = {
    #             "app_uri": args['app_svc_info']['app_uri'],
    #             "app_message": args['app_svc_info']['app_message']
    #         }
    #         check_app_svc_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
    #     with allure.step("TEARDOWN: 删除应用组"):
    #         delete_app_group_by_name(paas_admin_login, app_group_name)
    #         delete_micro_engine(paas_admin_login, engine_name)

    # @pytest.mark.L5
    # @pytest.mark.parametrize('args', data_file['test_create_war_app_on_mcp'])
    # @allure.description("在MCP部署war包应用")
    # def test_create_war_app_on_mcp(self, paas_admin_login, args):
    #     show_testcase_title(args['title'])
    #     with allure.step("SETUP: 创建应用组"):
    #         package_name = settings['PACKAGE_NAME_OF_WAR']
    #         package_version = settings['PACKAGE_VERSION_OF_WAR']
    #         app_group_info = setup_create_app_group(paas_admin_login, engine_type="others")
    #         app_group_name = app_group_info['name']
    #     with allure.step("1.创建应用"):
    #         app_name = get_random_string(5).lower()
    #         app_version = get_random_string(5, 3)
    #         deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
    #         resource_type = args['resource_type'].lower()
    #         app_type_info = {}
    #         app_type = args['app_type']
    #         if app_type == '无状态应用':
    #             app_type_info = {
    #                 "apiVersion": "apps/v1",
    #                 "kind": "Deployment"
    #             }
    #         cluster_info = {
    #             "cluster_type": "mcpCluster" if args['cluster_info']['cluster_type'] == "MCP集群" else "",
    #             "cluster_name": settings['CLUSTER_NAME']
    #         }
    #         # 应用安装包
    #         app_package_info = {
    #             "repository": True if args['repository'] == "公有" else False,
    #             "package_name": package_name,
    #             "package_version": package_version
    #         }
    #         # 容器规格
    #         container_spec = {
    #             "cpu_request": args['container_spec']['cpu_request'],
    #             "mem_request": args['container_spec']['mem_request'],
    #             "cpu_limit": args['container_spec']['cpu_limit'],
    #             "mem_limit": args['container_spec']['mem_limit']
    #         }
    #         # TOMCAT版本
    #         tomcat_version = args['tomcat_version']
    #         # JDK版本
    #         jdk_version = args['jdk_version']
    #         # 服务访问控制
    #         svc_access_control_info = {}
    #         if 'svc_access_control' in args.keys():
    #             svc_access_control_info = {
    #                 "dns_policy": "ClusterFirst" if args['svc_access_control'][
    #                                                     'dns_policy'] == "集群外访问" else "ClusterFirst",
    #                 "targetPort": args['svc_access_control']['targetPort'],
    #                 "port": args['svc_access_control']['port']
    #             }
    #             # 随机生成集群外访问端口
    #             node_port = generate_svc_port(paas_admin_login)
    #             node_port_info = {
    #                 "nodePort": node_port
    #             }
    #             svc_access_control_info.update(node_port_info)
    #         # 查询边缘节点
    #         mcp_plaintext_list = get_mcp_nodes_list(paas_admin_login, settings['MCP_CLUSTER_NAME'])
    #         # 创建应用
    #         create_war_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
    #                        app_type_info, cluster_info, app_package_info, container_spec, tomcat_version, jdk_version,
    #                        mcp_plaintext_list=mcp_plaintext_list, svc_access_control_info=svc_access_control_info)
    #     with allure.step("2.校验应用创建结果"):
    #         exp_status = "OK"
    #         exp_path = "$.data[0].status"
    #         check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
    #                              app_group_name=app_group_name)
    #     with allure.step("3.验证应用正常对外提供服务"):
    #         app_svc_info = {
    #             "app_uri": args['app_svc_info']['app_uri'],
    #             "app_message": args['app_svc_info']['app_message']
    #         }
    #         check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
    #     with allure.step("TEARDOWN: 删除应用组"):
    #         delete_app_group_by_name(paas_admin_login, app_group_name)

    # @pytest.mark.L5
    # @pytest.mark.parametrize('args', data_file['test_create_front_app_on_mcp'])
    # @allure.description("在MCP部署前端包应用")
    # def test_create_front_app_on_mcp(self, paas_admin_login, args):
    #     show_testcase_title(args['title'])
    #     with allure.step("SETUP: 创建应用组"):
    #         package_name = settings['PACKAGE_NAME_OF_WEB']
    #         package_version = settings['PACKAGE_VERSION_OF_WEB']
    #         app_group_info = setup_create_app_group(paas_admin_login, engine_type="others")
    #         app_group_name = app_group_info['name']
    #     with allure.step("1.创建应用"):
    #         app_name = get_random_string(5).lower()
    #         app_version = get_random_string(5, 3)
    #         deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
    #         resource_type = args['resource_type'].lower()
    #         app_type_info = {}
    #         app_type = args['app_type']
    #         if app_type == '无状态应用':
    #             app_type_info = {
    #                 "apiVersion": "apps/v1",
    #                 "kind": "Deployment"
    #             }
    #         cluster_info = {
    #             "cluster_type": "mcpCluster" if args['cluster_info']['cluster_type'] == "MCP集群" else "",
    #             "cluster_name": settings['CLUSTER_NAME']
    #         }
    #         # 应用安装包
    #         app_package_info = {
    #             "repository": True if args['repository'] == "公有" else False,
    #             "package_name": package_name,
    #             "package_version": package_version
    #         }
    #         # 容器规格
    #         container_spec = {
    #             "cpu_request": args['container_spec']['cpu_request'],
    #             "mem_request": args['container_spec']['mem_request'],
    #             "cpu_limit": args['container_spec']['cpu_limit'],
    #             "mem_limit": args['container_spec']['mem_limit']
    #         }
    #         # TOMCAT版本
    #         tomcat_version = args['tomcat_version']
    #         # JDK版本
    #         jdk_version = args['jdk_version']
    #         # NGINX版本
    #         nginx_version = args['nginx_version']
    #         # 服务访问控制
    #         svc_access_control_info = {}
    #         if 'svc_access_control' in args.keys():
    #             svc_access_control_info = {
    #                 "dns_policy": "ClusterFirst" if args['svc_access_control'][
    #                                                     'dns_policy'] == "集群外访问" else "ClusterFirst",
    #                 "targetPort": args['svc_access_control']['targetPort'],
    #                 "port": args['svc_access_control']['port']
    #             }
    #             # 随机生成集群外访问端口
    #             node_port = generate_svc_port(paas_admin_login)
    #             node_port_info = {
    #                 "nodePort": node_port
    #             }
    #             svc_access_control_info.update(node_port_info)
    #         # 查询边缘节点
    #         mcp_plaintext_list = get_mcp_nodes_list(paas_admin_login, settings['MCP_CLUSTER_NAME'])
    #         # 创建应用
    #         create_front_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
    #                          app_type_info, cluster_info, app_package_info, container_spec, tomcat_version,
    #                          jdk_version, nginx_version, mcp_plaintext_list=mcp_plaintext_list,
    #                          svc_access_control_info=svc_access_control_info)
    #     with allure.step("2.校验应用运行状态"):
    #         exp_status = "OK"
    #         exp_path = "$.data[0].status"
    #         check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
    #                              app_group_name=app_group_name)
    #     with allure.step("3.验证应用正常对外提供服务"):
    #         app_svc_info = {
    #             "app_uri": args['app_svc_info']['app_uri'],
    #             "app_message": args['app_svc_info']['app_message']
    #         }
    #         check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
    #     with allure.step("TEARDOWN: 删除应用组"):
    #         delete_app_group_by_name(paas_admin_login, app_group_name)

    # @pytest.mark.L5
    # @pytest.mark.parametrize('args', data_file['test_create_image_app_on_mcp'])
    # @allure.description("在MCP部署容器镜像包应用")
    # def test_create_image_app_on_mcp(self, paas_admin_login, args):
    #     show_testcase_title(args['title'])
    #     with allure.step("SETUP: 创建应用组"):
    #         package_name = settings['PACKAGE_NAME_OF_IMAGE']
    #         package_version = settings['PACKAGE_VERSION_OF_IMAGE']
    #         app_group_info = setup_create_app_group(paas_admin_login, engine_type="Istio")
    #         app_group_name = app_group_info['name']
    #     with allure.step("1.创建应用"):
    #         app_name = get_random_string(5).lower()
    #         app_version = get_random_string(5, 3)
    #         deploy_type = "Deployment" if args['deploy_type'] == "传统方式部署" else ""
    #         resource_type = args['resource_type'].lower()
    #         app_type_info = {}
    #         app_type = args['app_type']
    #         if app_type == '无状态应用':
    #             app_type_info = {
    #                 "apiVersion": "apps/v1",
    #                 "kind": "Deployment"
    #             }

    #         cluster_info = {
    #             "cluster_type": "mcpCluster" if args['cluster_info']['cluster_type'] == "MCP集群" else "",
    #             "cluster_name": settings['CLUSTER_NAME']
    #         }
    #         # 应用安装包
    #         app_package_info = {
    #             "repository": True if args['repository'] == "公有" else False,
    #             "package_name": package_name,
    #             "package_version": package_version
    #         }
    #         # 容器规格
    #         container_spec = {
    #             "cpu_request": args['container_spec']['cpu_request'],
    #             "mem_request": args['container_spec']['mem_request'],
    #             "cpu_limit": args['container_spec']['cpu_limit'],
    #             "mem_limit": args['container_spec']['mem_limit']
    #         }
    #         # 服务访问控制
    #         svc_access_control_info = {}
    #         if 'svc_access_control' in args.keys():
    #             svc_access_control_info = {
    #                 "dns_policy": "ClusterFirst" if args['svc_access_control'][
    #                                                     'dns_policy'] == "集群外访问" else "ClusterFirst",
    #                 "targetPort": args['svc_access_control']['targetPort'],
    #                 "port": args['svc_access_control']['port']
    #             }
    #             # 随机生成集群外访问端口
    #             node_port = generate_svc_port(paas_admin_login)
    #             node_port_info = {
    #                 "nodePort": node_port
    #             }
    #             svc_access_control_info.update(node_port_info)
    #         # 查询边缘节点
    #         mcp_plaintext_list = get_mcp_nodes_list(paas_admin_login, settings['MCP_CLUSTER_NAME'])
    #         # 创建应用
    #         create_image_app(paas_admin_login, app_name, app_version, app_group_name, deploy_type, resource_type,
    #                          app_type_info, cluster_info, app_package_info, container_spec,
    #                          mcp_plaintext_list=mcp_plaintext_list, svc_access_control_info=svc_access_control_info)
    #     with allure.step("2.校验应用创建结果"):
    #         exp_status = "OK"
    #         exp_path = "$.data[0].status"
    #         check_status_timeout(exp_status, exp_path, get_app_by_name, paas_client=paas_admin_login, app_name=app_name,
    #                              app_group_name=app_group_name)
    #     with allure.step("3.验证应用正常对外提供服务"):
    #         app_svc_info = {
    #             "app_uri": args['app_svc_info']['app_uri'],
    #             "app_message": args['app_svc_info']['app_message']
    #         }
    #         check_html_status(paas_admin_login, app_name, app_svc_info, app_group_name=app_group_name)
    #     with allure.step("TEARDOWN: 删除应用组"):
    #         delete_app_group_by_name(paas_admin_login, app_group_name)