import pytest
import allure
import os
import yaml
from time import sleep
from resource.base.login import PAASLogin
from scripts.msg.handler_msg import *
from resource.utils.common import *

cur_path = os.path.dirname(os.path.realpath(__file__))
datafile = os.path.join(cur_path, "data.yml")
with open(datafile, encoding="utf-8") as f:
    data = yaml.safe_load(f)


@pytest.mark.L4
@pytest.mark.msg
@allure.feature("微服务")
@allure.story("微服务引擎")
class TestMicroEngine:
    @pytest.mark.L1
    @pytest.mark.parametrize("args", data["create_springcloud_msg"])
    def test_create_micro_engine_with_springcloud(
        self, paas_proj_user_login: PAASClient, args
    ):
        allure.dynamic.title(args["title"])
        cluster_name = settings["CLUSTER_NAME"]
        version = args["version"]
        engine_name = "auto" + get_random_string(4)
        org_id = paas_proj_user_login.login_info.default_project_id
        midware = []
        if settings["cluster_name"] == "default":
            midware_type = 0
        else:
            midware_type = 1
        description = args["describe"]
        engine_ip = args["engineIp"]
        with allure.step("指定集群"):
            response = paas_proj_user_login.cce_client.get_cce_list(name=cluster_name)
            check_status_code(response)
            cluster = get_value_from_json(
                response, f"$.data[?(@.name=='{cluster_name}')]"
            )
            assert cluster, f"找不到指定的集群：{cluster_name}"
            cluster_id = cluster["uuid"]
        with allure.step("配置引擎类型及版本信息"):
            response = paas_proj_user_login.msg_client.get_msg_sku_list()
            check_status_code(response, 200)
            spingcloud_msg = get_value_from_json(
                response, f"$.data[?(@.version=='{version}')]"
            )
            assert spingcloud_msg, f"找不到指定的引擎信息: 类型springcloud, 版本：{version}"
        with allure.step("配置注册中心"):
            component_type = "native"
            discover = {
                "duplicate": args["discover"]["duplicate"],
                "reqCPU": args["discover"]["reqCPU"],
                "reqMemory": args["discover"]["reqMemory"],
                "limitCPU": args["discover"]["limitCPU"],
                "limitMemory": args["discover"]["limitMemory"],
                "storageClass": args["discover"]["storageClass"],
                "clusterPort": "",
                "nodePort": "",
                "component": args["discover"]["component"],
            }
            if args["discover"]["component"] == "nacos":
                r = paas_proj_user_login.msg_client.get_msg_sku_list()
                nacos_v = get_value_from_json(
                    r, "$..frameworkComponents[?(@.name=='nacos')].version"
                )
                assert nacos_v, "获取nacos组件版本信息失败"
                discover["version"] = nacos_v
                component_type = "nacos"
                mysql_info = {
                    "middleWare": "mysql",
                    "url": settings["HOST"],
                    "port": "3306",
                    "user": "os_admin",
                    "passWord": "SDNDX0Nsb3VkMFMjUGFhU0BDVFQyMDE5",
                }
                midware.append(mysql_info)
            else:
                response = paas_proj_user_login.msg_client.get_discovery_info(version)
                check_status_code(response, 200)
                discover_version = get_value_from_json(response, f"$..version")
                assert discover_version, f"获取注册中心版本信息失败"
                discover["version"] = discover_version
            components = []
            components.append(discover)
        if "config" in args:
            with allure.step("设置配置中心"):

                response = paas_proj_user_login.msg_client.get_config_info(version)
                check_status_code(response, 200)
                config_version = get_value_from_json(response, f"$..version")
                assert config_version, f"获取配置中心版本信息失败"
                config = {
                    "version": config_version,
                    "duplicate": args["config"]["duplicate"],
                    "reqCPU": args["config"]["reqCPU"],
                    "reqMemory": args["config"]["reqMemory"],
                    "limitCPU": args["config"]["limitCPU"],
                    "limitMemory": args["config"]["limitMemory"],
                    "storageClass": args["config"]["storageClass"],
                    "clusterPort": "",
                    "nodePort": "",
                    "component": "config",
                }
                components.append(config)
                if settings["CLUSTER_NAME"] == "default":
                    mysql_info = {
                        "middleWare": "mysql",
                        "url": "",
                        "port": "",
                        "user": "",
                        "passWord": "",
                    }
                else:
                    mysql_info = {
                        "middleWare": "mysql",
                        "url": settings["HOST"],
                        "port": "3306",
                        "user": "os_admin",
                        "passWord": "SDNDX0Nsb3VkMFMjUGFhU0BDVFQyMDE5",
                    }
                midware.append(mysql_info)

        if "gateway" in args:
            with allure.step("设置API网关和缓存信息"):

                response = paas_proj_user_login.msg_client.get_gateway_info(version)
                check_status_code(response, 200)
                gateway_version = get_value_from_json(response, f"$..version")
                assert gateway_version, f"获取API网关版本信息失败"
                gateway = {
                    "version": gateway_version,
                    "duplicate": args["gateway"]["duplicate"],
                    "reqCPU": args["gateway"]["reqCPU"],
                    "reqMemory": args["gateway"]["reqMemory"],
                    "limitCPU": args["gateway"]["limitCPU"],
                    "limitMemory": args["gateway"]["limitMemory"],
                    "storageClass": args["gateway"]["storageClass"],
                    "clusterPort": "",
                    "nodePort": "",
                    "component": "gateway",
                }
                components.append(gateway)
                if settings["CLUSTER_NAME"] == "default":
                    redis_info = {
                        "middleWare": "redis",
                        "url": "",
                        "port": "",
                        "passWord": "",
                    }
                else:
                    redis_info = {
                        "middleWare": "redis",
                        "url": settings["HOST"],
                        "port": "6379",
                        "passWord": "SDNDX0Nsb3VkMFNfUGFhU19DVFQyMDIw",
                    }

                midware.append(redis_info)
        with allure.step("创建微服务引擎"):
            response = (
                paas_proj_user_login.msg_client.create_micro_engine_with_springcloud(
                    engine_name,
                    org_id,
                    cluster_name,
                    cluster_id,
                    description,
                    version,
                    engine_ip,
                    components,
                    midware,
                    midware_type,
                    component_type,
                )
            )
            check_status_code(response, 200)
        with allure.step("校验微服务引擎状态"):
            cnt = 0
            while cnt < 30:
                engine = get_micro_engine_by_name(paas_proj_user_login, engine_name)
                if bool(engine):
                    if engine["state"] == "RUNNING":
                        break

                sleep(10)
                cnt = cnt + 1
            assert bool(engine), f"列表中找不到新建的微服务引擎: {engine_name}"
            status = engine["state"]
            assert (
                engine["state"] == "RUNNING"
            ), f"超时错误： 新建的微服务引擎{engine_name}状态异常，预期为RUNNING,实际为{status}"

        time.sleep(3)
        delete_micro_engine(paas_proj_user_login, engine_name)

    @pytest.mark.L5
    @allure.title("删除微服务引擎")
    def test_delete_micro_engine(self, paas_proj_user_login):
        with allure.step("新建微服务引擎"):
            name = "auto" + get_random_string(4)
            new_spingcloud_engine(paas_proj_user_login, name)
        with allure.step("删除微服务引擎"):
            time.sleep(3)
            delete_micro_engine(paas_proj_user_login, name)

    @pytest.mark.L5
    @pytest.mark.Smoke
    @allure.title("查询微服务引擎列表")
    def test_get_micro_engines_list(self, paas_proj_user_login: PAASClient):
        with allure.step("查询微服务引擎列表"):
            org_id = paas_proj_user_login.login_info.default_project_id
            micro_engine_list_response = (
                paas_proj_user_login.msg_client.query_micro_engine(
                    orgId=org_id, size=10, page=1
                )
            )
            check_status_code(micro_engine_list_response)

    @pytest.mark.L1
    @pytest.mark.parametrize("args", data["create_dubbo_msg"])
    def test_create_micro_engine_with_dubbo(
        self, paas_proj_user_login: PAASClient, args
    ):
        allure.dynamic.title(args["title"])
        msg_name = "auto" + get_random_string("5")
        cluster_name = settings["CLUSTER_NAME"]
        org_id = paas_proj_user_login.login_info.default_project_id

        description = args["describe"]
        engine_ip = args["engineIp"]
        with allure.step("指定集群"):
            response = paas_proj_user_login.cce_client.get_cce_list(name=cluster_name)
            check_status_code(response)
            cluster = get_value_from_json(
                response, f"$.data[?(@.name=='{cluster_name}')]"
            )
            assert cluster, f"找不到指定的集群：{cluster_name}"
            cluster_id = cluster["uuid"]

            if settings["CLUSTER_NAME"] == "default":
                midware_type = 0
            else:
                midware_type = 1
        with allure.step("配置引擎类型及版本信息"):
            response = paas_proj_user_login.msg_client.get_msg_sku_list()
            version = get_value_from_json(
                response, "$.data[?(@.name=='dubbo')].version"
            )
            assert version, "获取dubbo微服务引擎版本信息失败"
            check_status_code(response, 200)
            zookeeper_version = get_value_from_json(
                response,
                "$.data[?(@.name=='dubbo')].frameworkComponents[?(@.name=='dubbo-zookeeper')].version",
            )
            nacos_version = get_value_from_json(
                response,
                "$.data[?(@.name=='dubbo')].frameworkComponents[?(@.name=='nacos')].version",
            )
        conponentType = "native"
        components = []
        if "zookeeper" in args:
            discover = {
                "version": zookeeper_version,
                "duplicate": 3,
                "reqCPU": args["zookeeper"]["reqCPU"],
                "reqMemory": args["zookeeper"]["reqMemory"],
                "limitCPU": args["zookeeper"]["limitCPU"],
                "limitMemory": args["zookeeper"]["limitMemory"],
                "storageClass": args["zookeeper"]["storageClass"],
                "clusterPort": 0,
                "nodePort": 0,
                "component": "dubbo-zookeeper",
                "type": 6,
            }
            components.append(discover)
            midware = []
        if "config" in args:
            config = {
                "version": nacos_version,
                "duplicate": args["config"]["duplicate"],
                "reqCPU": args["config"]["reqCPU"],
                "reqMemory": args["config"]["reqMemory"],
                "limitCPU": args["config"]["limitCPU"],
                "limitMemory": args["config"]["limitMemory"],
                "clusterPort": 0,
                "nodePort": 0,
                "component": "nacos",
                "type": 10,
            }
            components.append(config)

            midware = [
                {
                    "middleWare": "mysql",
                    "url": settings["HOST"],
                    "port": 3306,
                    "user": "os_admin",
                    "passWord": "SDNDX0Nsb3VkMFMjUGFhU0BDVFQyMDE5",
                }
            ]
        if "nacos" in args:
            conponentType = "nacos"
            discover = {
                "version": nacos_version,
                "duplicate": args['nacos']['replica'],
                "reqCPU": args["nacos"]["reqCPU"],
                "reqMemory": args["nacos"]["reqMemory"],
                "limitCPU": args["nacos"]["limitCPU"],
                "limitMemory": args["nacos"]["limitMemory"],
                "storageClass": args["nacos"]["storageClass"],
                "clusterPort": 0,
                "nodePort": 0,
                "component": "nacos",
                "type": 10,
            }
            components.append(discover)
            nacos_config = discover
            components.append(nacos_config)
            midware = [
                {
                    "middleWare": "mysql",
                    "url": settings["HOST"],
                    "port": 3306,
                    "user": "os_admin",
                    "passWord": "SDNDX0Nsb3VkMFMjUGFhU0BDVFQyMDE5",
                }
            ]
        create_msg_response = (
            paas_proj_user_login.msg_client.create_micro_engine_with_dubbo(
                org_id,
                msg_name,
                cluster_name,
                cluster_id,
                description,
                engine_ip,
                version,
                components,
                midware_type,
                midware,
                conponentType,
            )
        )
        check_status_code(create_msg_response)
        cnt = 0
        while cnt < 30:
            engine = get_micro_engine_by_name(paas_proj_user_login, msg_name)
            if bool(engine):
                if engine["state"] == "RUNNING":
                    break
            sleep(20)
            cnt = cnt + 1
        assert bool(engine), f"列表中找不到新建的微服务引擎: {msg_name}"
        status = engine["state"]
        assert (
            engine["state"] == "RUNNING"
        ), f"超时错误：新建的微服务引擎{msg_name}状态异常，预期为RUNNING,实际为{status}"

        sleep(2)
        delete_micro_engine(paas_proj_user_login, msg_name)

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data["modify_msg_info"])
    def test_moidfy_msg_info(self, paas_proj_user_login: PAASClient, args):
        allure.dynamic.title(args["title"])
        msg = new_spingcloud_engine(paas_proj_user_login)
        msg_id = msg["id"]
        name = "modify" + get_random_string(4).lower()
        engineIp = args["engineIp"]
        description = args["description"]
        cluser_id = settings["CLUSTER_ID"]
        res = paas_proj_user_login.msg_client.modify_msg_info(
            cluser_id, msg_id, name, engineIp, description
        )
        check_status_code(res, 200)
        assert name == get_value_from_json(res, "$..name")
        assert description == get_value_from_json(res, "$..description")
        assert engineIp == get_value_from_json(res, "$..engineIp")
        time.sleep(2)
        delete_micro_engine(paas_proj_user_login, name)

    @pytest.mark.L1
    @allure.title("springcloud微服务引擎添加API网关组件")
    def test_add_component(self, paas_proj_user_login: PAASClient):
        name = "auto" + get_random_string(4).lower()
        mse_info = add_spring_mse(paas_proj_user_login, name)
        host = "172.25.16.180"
        if settings["CLUSTER_NAME"] != "default":
            midware_type = 1
        else:
            midware_type = 0
        data = {
            "id": mse_info['id'],
            "middleWares": [
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
            ],
            "middlewareCustomType": midware_type,
            "componentType": "native",
            "components": [
                {
                    "component": "gateway",
                    "version": "2.0.4",
                    "duplicate": 1,
                    "reqCPU": "0.5",
                    "reqMemory": "512Mi",
                    "limitCPU": "1",
                    "limitMemory": "1024Mi",
                    "clusterPort": "",
                    "nodePort": "",
                    "middlewareCustomType": midware_type,
                }
            ],
        }
        resp = paas_proj_user_login.msg_client.add_mse_compoent(mse_info['id'], data)
        check_status_code(resp, 200)
        cnt = 0
        while cnt < 30:
            time.sleep(20)
            r = paas_proj_user_login.msg_client.get_mse_component_status(
                settings['CLUSTER_ID'], mse_info['id']
            )
            gateway_info = get_value_from_json(
                r, "$..components[?(@.componentType=='springcloud-gateway')]"
            )
            if  gateway_info and gateway_info['status'] == 'RUNNING':
                break
            else:
                cnt = cnt + 1
        assert cnt < 30, "给springcloud微服务引擎添加api网关失败"
        time.sleep(3)
        delete_micro_engine(paas_proj_user_login, name)

    @pytest.mark.L1
    @pytest.mark.parametrize("args", data["update_component_flavor"])
    def test_update_component_flavor(self, paas_proj_user_login: PAASClient, args):
        allure.dynamic.title(args['title'])
        name = "auto" + get_random_string(4).lower()
        mse_info = add_spring_mse(paas_proj_user_login, name)
        mse_id = mse_info['id']
        resp = paas_proj_user_login.msg_client.get_mse_component(mse_id)
        check_status_code(resp)
        cluster_port = get_value_from_json(resp, "$..clusterPort")
        node_port = get_value_from_json(resp, "$..nodePort")
        if settings["CLUSTER_NAME"] != "default":
            midware_type = 1
        else:
            midware_type = 0
        data = {
            "id": mse_id,
            "middleWares": [
                {
                    "middleWare": "mysql",
                    "url": "",
                    "port": "",
                    "user": "",
                    "passWord": "",
                },
                {"middleWare": "redis", "url": "", "port": "", "passWord": ""},
            ],
            "middlewareCustomType": midware_type,
            "componentType": "native",
            "components": [
                {
                    "version": "1.9.3",
                    "duplicate": args['replicas'],
                    "reqCPU": "0.5",
                    "reqMemory": "512Mi",
                    "limitCPU": args['limit_cpu'],
                    "limitMemory": args['limit_mem'],
                    "storageClass": "",
                    "clusterPort": cluster_port,
                    "nodePort": node_port,
                    "middlewareCustomType": midware_type,
                    "component": "discover",
                }
            ],
        }
        r = paas_proj_user_login.msg_client.update_mse_component_flavor(mse_id, data)
        check_status_code(r)
        cnt = 0
        while cnt < 30:
            time.sleep(20)
            r = paas_proj_user_login.msg_client.get_mse_component_status(
                settings['CLUSTER_ID'], mse_id
            )
            gateway_info = get_value_from_json(r, "$..components[0]")
            if gateway_info['status'] == 'RUNNING':
                break
            else:
                cnt = cnt + 1
        assert cnt < 30, args['title'] + "失败"
        check = paas_proj_user_login.msg_client.get_mse_component(mse_id)
        assert get_value_from_json(check, "$..replica") == args['replicas']
        assert get_value_from_json(check, "$..limitCpu") == args['limit_cpu']
        assert get_value_from_json(check, "$..limitMemory") == args['limit_mem']
        time.sleep(3)
        delete_micro_engine(paas_proj_user_login, name)


@pytest.mark.L5
@pytest.mark.msg
class TestMse:
    def setup_class(self):
        self.user = PAASClient(
            PAASLogin(
                settings['PROJ_USER'],
                settings['PASSWORD'],
                settings['HOST'],
                settings['PORT'],
            )
        )
        name = "auto" + get_random_string(4).lower()
        mse_info = new_spingcloud_engine(self.user, name)
        self.mse_id = mse_info['id']

    def teardown_class(self):
        self.user.msg_client.delete_springcloud_engine(
            settings['CLUSTER_ID'], self.mse_id
        )

    @allure.title("跟新配置项")
    def test_update_configmap(self, paas_proj_user_login: PAASClient):
        with allure.step("新建配置"):
            mse_id = self.mse_id
            key = "k1"
            value = "v1"
            resp = paas_proj_user_login.msg_client.create_config(mse_id, key, value)
            check_status_code(resp)
            time.sleep(3)
            check = paas_proj_user_login.msg_client.get_mse_configmap(mse_id)
            cm_info = get_value_from_json(check, "$.data[0]")
            assert cm_info['name'] == key
            assert cm_info['value'] == value
            cm_id = cm_info['id']
        with allure.step("更新配置"):
            new_value = "value new"
            resp = paas_proj_user_login.msg_client.update_configmap(
                mse_id, cm_id, cm_info['name'], new_value
            )
            check_status_code(resp)
        with allure.step("校验修改是否成功"):
            check = paas_proj_user_login.msg_client.get_mse_configmap(mse_id)
            cm_info = get_value_from_json(check, "$.data[0]")
            assert cm_info['name'] == key
            assert cm_info['value'] == new_value
            time.sleep(3)
            cm_id = str(cm_info['id'])
            paas_proj_user_login.msg_client.delete_configmap(mse_id, cm_id)

    @pytest.mark.L3
    @allure.title("新建配置项")
    def test_create_configmap(self, paas_proj_user_login: PAASClient):
        mse_id = self.mse_id
        key = "k1"
        value = "v1"
        resp = paas_proj_user_login.msg_client.create_config(mse_id, key, value)
        check_status_code(resp)
        time.sleep(3)
        check = paas_proj_user_login.msg_client.get_mse_configmap(mse_id)
        cm_info = get_value_from_json(check, "$.data[0]")
        assert cm_info['name'] == key
        assert cm_info['value'] == value

    @allure.title("删除配置项")
    def test_del_configmap(self, paas_proj_user_login: PAASClient):
        mse_id = self.mse_id
        key = "k1"
        value = "v1"
        resp = paas_proj_user_login.msg_client.create_config(mse_id, key, value)
        check_status_code(resp)
        time.sleep(3)
        check = paas_proj_user_login.msg_client.get_mse_configmap(mse_id)
        cm_info = get_value_from_json(check, "$.data[0]")
        cm_id = cm_info['id']
        time.sleep(3)
        del_r = paas_proj_user_login.msg_client.delete_configmap(mse_id, cm_id)
        check_status_code(del_r)
        time.sleep(3)
        check2 = paas_proj_user_login.msg_client.get_mse_configmap(mse_id)
        assert get_value_from_json(check2, "$..total") == 0, "微服务引擎删除配置失败"
