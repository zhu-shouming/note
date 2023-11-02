import pytest
import os
import yaml
from scripts.gateway.handler_gateway import *
from resource.utils.common import *

cur_path = os.path.dirname(os.path.realpath(__file__))
dataPath = os.path.join(cur_path, 'data_proj_user.yml')
with open(dataPath, encoding='utf-8') as f:
    data_file = yaml.safe_load(f)


@pytest.mark.gateway
@allure.feature("服务网关")
@allure.story("服务网关")
class TestGateway:

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['test_create_gateway'])
    def test_create_gateway(self, paas_proj_user_login, args):
        show_testcase_title(args['title'])
        with allure.step("1.填写信息"):
            resource = args['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            cluster_name = args['cluster_name'] if 'cluster_name' in args.keys() else settings['CLUSTER_NAME']
            storage_class = args['storage_class']
            data_volume = args['data_volume']
            gw_name = "auto" + get_random_string(5, char_type=0)
            loop = 3
            while loop:
                http_port = generate_kong_port(paas_proj_user_login, kong_ip, cluster_name=cluster_name)
                https_port = generate_kong_port(paas_proj_user_login, kong_ip, cluster_name=cluster_name)
                if http_port == https_port:
                    loop -= 1
                else:
                    break
            assert loop > 0, "生成的HTTP和HTTPS端口3次均相同"
            role_name = paas_proj_user_login.login_info.user_role
        with allure.step("2.创建服务网关"):
            create_gateway(paas_proj_user_login, gw_name, kong_ip, http_port, https_port, resource, cluster_name,
                           data_volume, role_name=role_name, storage_class=storage_class)
        with allure.step("3.校验状态"):
            exp_status = "RUNNING"
            exp_path = "$.data[0].status"
            check_status_timeout(exp_status, exp_path, get_gw_by_name, 1800, paas_client=paas_proj_user_login, name=gw_name)
        with allure.step("4.删除服务网关"):
            delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_gateway'])
    def test_restart_gateway(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 重启服务网关")
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args['storage_class']
            data_volume = args['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
        with allure.step("重启服务网关"):
            restart_gateway(paas_proj_user_login, gw_name)
        with allure.step("TEARDOWN：删除服务网关"):
            delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_gateway'])
    def test_resize_gateway(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 扩缩容服务网关容器规格")
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            old_resource = args['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args['storage_class']
            data_volume = args['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, old_resource, kong_ip, storage_class, data_volume)
        with allure.step("1.扩容服务网关"):
            new_resource = {
                "cpu_request": str(int(float(old_resource['cpu_request']) * 2.0)),
                "mem_request": str(int(float(old_resource['mem_request'].split("Gi")[0]) * 2.0)) + 'Gi',
                "cpu_limit": str(int(float(old_resource['cpu_limit']) * 2.0)),
                "mem_limit": str(int(float(old_resource['mem_limit'].split("Gi")[0]) * 2.0)) + 'Gi'
            }
            resize_gateway(paas_proj_user_login, gw_name, new_resource)
        with allure.step("2.缩容服务网关"):
            resize_gateway(paas_proj_user_login, gw_name, old_resource)
        with allure.step("TEARDOWN: 删除服务网关"):
            delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_gateway'])
    def test_replicas_gateway(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 扩缩容服务网关容器实例")
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args['storage_class']
            data_volume = args['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
            gw_info = get_gw_by_name(paas_proj_user_login, gw_name)['data'][0]
            origin_kong_ip = gw_info['kongIp']
            origin_http_port = gw_info['kongHttpProxyPort']
            origin_https_port = gw_info['kongHttpsProxyPort']
        with allure.step("1.扩容服务网关"):
            replicas_kong_ip = get_worker_node(paas_proj_user_login, 1)
            exp_business_ips = origin_kong_ip + "," + replicas_kong_ip
            exp_http_ports = origin_http_port + "," + origin_http_port
            exp_https_ports = origin_https_port + "," + origin_https_port
            replicas_gateway(paas_proj_user_login, gw_name, exp_business_ips, exp_http_ports, exp_https_ports)
        with allure.step("2.缩容服务网关"):
            replicas_gateway(paas_proj_user_login, gw_name, origin_kong_ip, origin_http_port, origin_https_port)
        with allure.step("TEARDOWN: 删除服务网关"):
            delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_gateway'])
    def test_create_api_group(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 创建接口分组")
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args['storage_class']
            data_volume = args['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
        with allure.step("创建接口分组"):
            api_group_name = "auto" + get_random_string(5, char_type=0)
            create_api_group(paas_proj_user_login, gw_name, api_group_name)
        with allure.step("TEARDOWN"):
            with allure.step("1.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("2.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args1', data_file['setup_create_gateway'])
    @pytest.mark.parametrize('args', data_file['test_create_api'])
    def test_create_api(self, paas_proj_user_login, args1, args):
        show_testcase_title("普通用户 -- 创建接口")
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args1['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args1['storage_class']
            data_volume = args1['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
        with allure.step("创建接口分组"):
            api_group_name = "auto" + get_random_string(5, char_type=0)
            create_api_group(paas_proj_user_login, gw_name, api_group_name)
        with allure.step("发布接口"):
            api_name = "auto" + get_random_string(5, char_type=0)
            svc_params = args['svc_params']
            svc_params['services'] = [{
                "host": settings['APP_ADDR1'],
                "weight": 100
            }]
            kong_params = args['kong_params']
            create_apis(paas_proj_user_login, gw_name, api_group_name, api_name, svc_params, kong_params)
        with allure.step("验证接口功能"):
            sleep(10)
            api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
            kong_url = api_detail['data']['kongUrl'][0]
            # response = requests.get("http://" + kong_url)
            # assert response.status_code == 200, f"访问http://{kong_url}失败"
            message = get_gateway_api(kong_url)
            assert message == svc_params[
                'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
        with allure.step("TEARDOWN"):
            with allure.step("1.删除接口"):
                delete_api_by_name(paas_proj_user_login, gw_name, api_name)
            with allure.step("2.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args1', data_file['setup_create_apis'])
    @pytest.mark.parametrize('args', data_file['test_create_api_versions'])
    def test_create_api_versions(self, paas_proj_user_login, args1, args):
        show_testcase_title("普通用户 -- 创建接口版本")
        with allure.step("SETUP"):
            with allure.step("1.创建服务网关"):
                gw_name = "auto" + get_random_string(5, char_type=0)
                resource = args1['container_spec']
                kong_ip = get_worker_node(paas_proj_user_login, 0)
                storage_class = args1['storage_class']
                data_volume = args1['data_volume']
                setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
            with allure.step("2.创建接口分组"):
                api_group_name = "auto" + get_random_string(5, char_type=0)
                create_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.发布接口"):
                api_name = "auto" + get_random_string(5, char_type=0)
                svc_params = args1['svc_params']
                svc_params['services'] = [{
                    "host": settings['APP_ADDR1'],
                    "weight": 100
                }]
                init_path = args1['kong_params']['kong_path']
                path = init_path + get_random_string(3, char_type=0).lower()
                args1['kong_params']['kong_path'] = path
                kong_params = args1['kong_params']
                create_apis(paas_proj_user_login, gw_name, api_group_name, api_name, svc_params, kong_params)
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # response = requests.get("http://" + kong_url)
                # assert response.status_code == 200, f"访问http://{kong_url}失败"
                message = get_gateway_api(kong_url)
                assert message == svc_params[
                    'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
        with allure.step("创建版本"):
            version = get_random_string(5, char_type=0)
            service_list = [
                {
                    "host": settings['APP_ADDR2'],
                    "weight": 100
                }
            ]
            items_header = [args['items_header']]
            create_apis_version(paas_proj_user_login, gw_name, api_name, version, service_list, items_header=items_header)
        with allure.step("验证新版本"):
            header = {}
            for item in items_header[0]:
                header[item.split(":")[0]] = item.split(":")[1]

            url = "http://" + settings['APP_ADDR2'] + args['svc_path']
            # response = requests.get(url=url, headers=header)
            # assert response.status_code == 200, f"访问{url}失败"
            message = get_gateway_api(url)
            assert message == args['app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
        with allure.step("TEARDOWN"):
            with allure.step("1.删除接口"):
                delete_api_by_name(paas_proj_user_login, gw_name, api_name)
            with allure.step("2.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_apis'])
    def test_offline_online_apis(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 下线/上线接口")
        with allure.step("SETUP"):
            with allure.step("1.创建服务网关"):
                gw_name = "auto" + get_random_string(5, char_type=0)
                resource = args['container_spec']
                kong_ip = get_worker_node(paas_proj_user_login, 0)
                storage_class = args['storage_class']
                data_volume = args['data_volume']
                setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
            with allure.step("2.创建接口分组"):
                api_group_name = "auto" + get_random_string(5, char_type=0)
                create_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.发布接口"):
                api_name = "auto" + get_random_string(5, char_type=0)
                svc_params = args['svc_params']
                svc_params['services'] = [{
                    "host": settings['APP_ADDR1'],
                    "weight": 100
                }]
                init_path = args['kong_params']['kong_path']
                path = init_path + get_random_string(3, char_type=0).lower()
                args['kong_params']['kong_path'] = path
                kong_params = args['kong_params']
                create_apis(paas_proj_user_login, gw_name, api_group_name, api_name, svc_params, kong_params)
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # response = requests.get("http://" + kong_url)
                # assert response.status_code == 200, f"访问http://{kong_url}失败"
                message = get_gateway_api(kong_url)
                assert message == svc_params[
                    'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
        with allure.step("下线接口"):
            offline_apis_by_name(paas_proj_user_login, gw_name, api_name)
        with allure.step("上线接口"):
            online_apis_by_name(paas_proj_user_login, gw_name, api_name, svc_params['app_message'])
        with allure.step("TEARDOWN"):
            with allure.step("1.删除接口"):
                delete_api_by_name(paas_proj_user_login, gw_name, api_name)
            with allure.step("2.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_gateway'])
    def test_create_proxy_cache(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 创建代理缓存策略")
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args['storage_class']
            data_volume = args['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
        with allure.step("创建代理缓存策略"):
            policy_name = "auto" + get_random_string(5, char_type=0)
            create_proxy_cache(paas_proj_user_login, gw_name, policy_name)
        with allure.step("TEARDOWN"):
            with allure.step("1.删除代理缓存策略"):
                delete_proxy_cache(paas_proj_user_login, gw_name, policy_name)
            with allure.step("2.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_apis'])
    def test_proxy_cache_bind_and_unbind_api(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 代理缓存策略绑定/解绑网关")
        with allure.step("SETUP"):
            with allure.step("1.创建服务网关"):
                gw_name = "auto" + get_random_string(5, char_type=0)
                resource = args['container_spec']
                kong_ip = get_worker_node(paas_proj_user_login, 0)
                storage_class = args['storage_class']
                data_volume = args['data_volume']
                setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
            with allure.step("2.创建接口分组"):
                api_group_name = "auto" + get_random_string(5, char_type=0)
                create_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.发布接口"):
                api_name = "auto" + get_random_string(5, char_type=0)
                svc_params = args['svc_params']
                svc_params['services'] = [{
                    "host": settings['APP_ADDR1'],
                    "weight": 100
                }]
                init_path = args['kong_params']['kong_path']
                path = init_path + get_random_string(3, char_type=0).lower()
                args['kong_params']['kong_path'] = path
                kong_params = args['kong_params']
                create_apis(paas_proj_user_login, gw_name, api_group_name, api_name, svc_params, kong_params)
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # response = requests.get("http://" + kong_url)
                # assert response.status_code == 200, f"访问http://{kong_url}失败"
                message = get_gateway_api(kong_url)
                assert message == svc_params[
                    'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
            with allure.step("4.创建代理缓存策略"):
                policy_name = "auto" + get_random_string(5, char_type=0)
                create_proxy_cache(paas_proj_user_login, gw_name, policy_name)
        with allure.step("1.代理缓存策略绑定接口"):
            bind_apis_with_proxy_cache(paas_proj_user_login, gw_name, policy_name, api_name, api_group_name)
        with allure.step("2.校验绑定接口"):
            sleep(5)
            api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
            kong_url = api_detail['data']['kongUrl'][0]
            # TODO:
            # requests.get("http://" + kong_url)
            # response = requests.get("http://" + kong_url)
            # assert response.status_code == 200, f"访问http://{kong_url}失败"
            # assert 'X-Cache-Status' in response.headers.keys() and response.headers.get('X-Cache-Status') == 'Hit', \
            #     "代理缓存未生效或接口未绑定成功"
        with allure.step("3.代理缓存策略解绑接口"):
            unbind_apis_with_proxy_cache(paas_proj_user_login, gw_name, policy_name, api_name, api_group_name)
        with allure.step("4.校验解绑接口"):
            sleep(5)
            api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
            kong_url = api_detail['data']['kongUrl'][0]
            # TODO:
            # response = requests.get("http://" + kong_url)
            # assert response.status_code == 200, f"访问http://{kong_url}失败"
            # assert 'X-Cache-Status' not in response.headers.keys(), "代理缓存未成功解绑接口"
        with allure.step("TEARDOWN"):
            with allure.step("1.删除代理缓存策略"):
                delete_proxy_cache(paas_proj_user_login, gw_name, policy_name)
            with allure.step("2.删除接口"):
                delete_api_by_name(paas_proj_user_login, gw_name, api_name)
            with allure.step("3.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("4.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args1', data_file['setup_create_gateway'])
    @pytest.mark.parametrize('args', data_file['test_create_flow_control'])
    def test_create_flow_control(self, paas_proj_user_login, args1, args):
        show_testcase_title(args['title'])
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args1['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args1['storage_class']
            data_volume = args1['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
        with allure.step("创建流控策略"):
            policy_name = "auto" + get_random_string(5, char_type=0)
            limit_by = args['limit_by']
            per_sec = args['per_sec']
            per_min = args['per_min']
            per_hour = args['per_hour']
            per_day = args['per_day']
            create_flow_control(paas_proj_user_login, gw_name, policy_name, limit_by, per_sec, per_min, per_hour,
                                per_day)
        with allure.step("TEARDOWN"):
            with allure.step("1.删除流控策略"):
                delete_flow_control(paas_proj_user_login, gw_name, policy_name)
            with allure.step("2.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_apis'])
    def test_flow_control_bind_and_unbind_api(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 流控策略（按接口）绑定/解绑接口")
        with allure.step("SETUP"):
            with allure.step("1.创建服务网关"):
                gw_name = "auto" + get_random_string(5, char_type=0)
                resource = args['container_spec']
                kong_ip = get_worker_node(paas_proj_user_login, 0)
                storage_class = args['storage_class']
                data_volume = args['data_volume']
                setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
            with allure.step("2.创建接口分组"):
                api_group_name = "auto" + get_random_string(5, char_type=0)
                create_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.发布接口"):
                api_name = "auto" + get_random_string(5, char_type=0)
                svc_params = args['svc_params']
                svc_params['services'] = [{
                    "host": settings['APP_ADDR1'],
                    "weight": 100
                }]
                init_path = args['kong_params']['kong_path']
                path = init_path + get_random_string(3, char_type=0).lower()
                args['kong_params']['kong_path'] = path
                kong_params = args['kong_params']
                create_apis(paas_proj_user_login, gw_name, api_group_name, api_name, svc_params, kong_params)
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # response = requests.get("http://" + kong_url)
                # assert response.status_code == 200, f"访问http://{kong_url}失败"
                message = get_gateway_api(kong_url)
                assert message == svc_params[
                    'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
            with allure.step("4.创建流控策略"):
                policy_name = "auto" + get_random_string(5, char_type=0)
                limit_by = "service"
                per_sec = "-1"
                per_min = "30"
                per_hour = "-1"
                per_day = "-1"
                create_flow_control(paas_proj_user_login, gw_name, policy_name, limit_by, per_sec, per_min, per_hour,
                                    per_day)
            with allure.step("1.流控策略绑定接口"):
                bind_apis_with_flow_control(paas_proj_user_login, gw_name, policy_name, api_name, api_group_name)
            with allure.step("2.校验绑定接口"):
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # TODO:
                # response = requests.get("http://" + kong_url)
                # current_sec = response.headers['Date'].split("2023")[1].split("GMT")[0].replace(" ", "").split(":")[-1]
                # if int(current_sec) >= 45:
                #     time.sleep(20)
                # limit_min = response.headers['X-RateLimit-Limit-minute']
                # assert per_min == limit_min, f"流控策略未生效。实际：{limit_min}， 期望：{per_min}"
                # count = 0
                # num = int(per_min) * 2
                # while num > 0:
                #     response = requests.get("http://" + kong_url)
                #     if "API rate limit exceeded" in response.text:
                #         count += 1
                #     num -= 1
                # quota = float(count / (int(limit_min) * 2))
                # assert quota >= 0.45, f"流控策略失效。出现概率：{quota}"
            with allure.step("3.代理缓存策略解绑接口"):
                unbind_apis_with_flow_control(paas_proj_user_login, gw_name, policy_name, api_name, api_group_name)
            with allure.step("4.校验解绑接口"):
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # TODO:
                # response = requests.get("http://" + kong_url)
                # assert 'X-RateLimit-Limit-minute' not in response.headers.keys(), \
                #     "流控策略解绑失败。仍有头信息：X-RateLimit-Limit-minute"
                # current_sec = response.headers['Date'].split("2023")[1].split("GMT")[0].replace(" ", "").split(":")[-1]
                # if int(current_sec) >= 45:
                #     time.sleep(20)
                # num = int(per_min) * 2
                # while num > 0:
                #     response = requests.get("http://" + kong_url)
                #     assert 'API rate limit exceeded' not in response.headers.keys(), \
                #         "流控策略解绑失败。仍有：API rate limit exceeded"
                #     num -= 1
        with allure.step("TEARDOWN"):
            with allure.step("1.删除流控策略"):
                delete_flow_control(paas_proj_user_login, gw_name, policy_name)
            with allure.step("2.删除接口"):
                delete_api_by_name(paas_proj_user_login, gw_name, api_name)
            with allure.step("3.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("4.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args1', data_file['setup_create_gateway'])
    @pytest.mark.parametrize('args', data_file['test_create_access_control'])
    def test_create_access_control(self, paas_proj_user_login, args1, args):
        with allure.step("SETUP：创建服务网关"):
            gw_name = "auto" + get_random_string(5, char_type=0)
            resource = args1['container_spec']
            kong_ip = get_worker_node(paas_proj_user_login, 0)
            storage_class = args1['storage_class']
            data_volume = args1['data_volume']
            setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
        with allure.step("创建安全控制策略"):
            policy_name = "auto" + get_random_string(5, char_type=0)
            limit_type = args['limit_type']
            config = {
                "items_header": [args['items_header']]
            }
            create_access_control(paas_proj_user_login, gw_name, policy_name, limit_type, config=config)
        with allure.step("TEARDOWN"):
            with allure.step("1.删除安全控制策略"):
                delete_access_control(paas_proj_user_login, gw_name, policy_name)
            with allure.step("2.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)

    @pytest.mark.L5
    @pytest.mark.parametrize('args', data_file['setup_create_apis'])
    def test_access_control_bind_and_unbind_api(self, paas_proj_user_login, args):
        show_testcase_title("普通用户 -- 安全控制策略绑定/解绑接口")
        with allure.step("SETUP"):
            with allure.step("1.创建服务网关"):
                gw_name = "auto" + get_random_string(5, char_type=0)
                resource = args['container_spec']
                kong_ip = get_worker_node(paas_proj_user_login, 0)
                storage_class = args['storage_class']
                data_volume = args['data_volume']
                setup_create_gateway(paas_proj_user_login, gw_name, resource, kong_ip, storage_class, data_volume)
            with allure.step("2.创建接口分组"):
                api_group_name = "auto" + get_random_string(5, char_type=0)
                create_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("3.发布接口"):
                api_name = "auto" + get_random_string(5, char_type=0)
                svc_params = args['svc_params']
                svc_params['services'] = [{
                    "host": settings['APP_ADDR1'],
                    "weight": 100
                }]
                init_path = args['kong_params']['kong_path']
                path = init_path + get_random_string(3, char_type=0).lower()
                args['kong_params']['kong_path'] = path
                kong_params = args['kong_params']
                create_apis(paas_proj_user_login, gw_name, api_group_name, api_name, svc_params, kong_params)
                sleep(10)
                api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
                kong_url = api_detail['data']['kongUrl'][0]
                # response = requests.get("http://" + kong_url)
                # assert response.status_code == 200, f"访问http://{kong_url}失败"
                message = get_gateway_api(kong_url)
                assert message == svc_params[
                    'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
            with allure.step("4.创建安全控制策略"):
                policy_name = "auto" + get_random_string(5, char_type=0)
                limit_type = "rule"
                config = {
                    "items_header": [["k1:v1"]]
                }
                create_access_control(paas_proj_user_login, gw_name, policy_name, limit_type, config=config)
        with allure.step("1.安全控制策略绑定接口"):
            bind_apis_with_access_control(paas_proj_user_login, gw_name, policy_name, api_name, api_group_name)
        with allure.step("2.校验绑定接口"):
            sleep(5)
            api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
            kong_url = api_detail['data']['kongUrl'][0]
            # TODO:
            # headers = {
            #     "k1": "v1"
            # }
            # response = requests.get("http://" + kong_url, headers=headers)
            # assert response.status_code == 503
            # assert "Service unavailable" in response.text, f"接口响应：实际：{response.text}，期望：Service unavailable"
        with allure.step("3.安全控制策略解绑接口"):
            unbind_apis_with_access_control(paas_proj_user_login, gw_name, policy_name, api_name, api_group_name)
        with allure.step("4.校验解绑接口"):
            sleep(5)
            api_detail = get_apis_detail_by_name(paas_proj_user_login, gw_name, api_name)
            kong_url = api_detail['data']['kongUrl'][0]
            # response = requests.get("http://" + kong_url)
            # assert response.status_code == 200, f"访问http://{kong_url}失败"
            message = get_gateway_api(kong_url)
            assert message == svc_params[
                'app_message'], f"访问http://{kong_url}失败。期望：{svc_params['app_message']}，实际：{message}"
        with allure.step("TEARDOWN"):
            with allure.step("1.删除安全控制"):
                delete_access_control(paas_proj_user_login, gw_name, policy_name)
            with allure.step("2.删除接口"):
                delete_api_by_name(paas_proj_user_login, gw_name, api_name)
            with allure.step("3.删除接口分组"):
                delete_api_group(paas_proj_user_login, gw_name, api_group_name)
            with allure.step("4.删除网关"):
                delete_gateway(paas_proj_user_login, gw_name)