from time import sleep
import pytest, allure, os, yaml

from resource.base.login import PAASLogin
from scripts.cce.handler_cce import *
from config.config import settings
from scripts.ccr.handler_ccr import upload_public_img

cur_path = os.path.dirname(os.path.realpath(__file__))
datafile = os.path.join(cur_path, 'workload_data.yaml')
with open(datafile, encoding='utf-8') as f:
    data = yaml.safe_load(f)


@pytest.mark.cce
@allure.feature("云容器引擎")
@allure.story("工作负载")
class TestWorkload:
    def setup_class(self):
        self.user = PAASClient(
            PAASLogin(
                settings['PROJ_ADMIN'],
                settings['PASSWORD'],
                settings['HOST'],
                settings['PORT'],
            )
        )
        ns_name = "auto" + get_random_string(4).lower()
        self.ns = new_namespace(self.user, ns_name)
        r = self.user.ccr_client.get_public_images(img_name="autotest-cce")
        if get_value_from_json(r, "$..total") == 1:
            pass
        else:
            img_path = settings['cce_image']
            upload_public_img(self.user, img_path, "autotest-cce", "v1")

    def teardown_class(self):
        self.user.cce_client.del_namespace(self.ns['name'], settings['CLUSTER_ID'])

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['create_deployment_workload'])
    def test_create_workload(self, args):
        allure.dynamic.title('项目管理员' + args['title'])
        yaml_str = str(args['yaml'])
        deploy_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        ns = self.ns['name']
        r = self.user.cce_client.create_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, yaml_str
        )
        check_status_code(r, 200)
        cnt = 0
        while cnt < 5:
            sleep(10)
            r_check = self.user.cce_client.get_deployment_by_ns(
                payload_type, settings['CLUSTER_ID'], ns
            )
            deploy = get_value_from_json(
                r_check, f"$.data[?(@.name=='{deploy_name}')]"
            )
            if deploy["status"] == "running":
                break
            else:
                cnt = cnt + 1
        assert cnt < 5, f"新建{payload_type}工作负载失败"
        sleep(4)
        r = self.user.cce_client.del_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        check_status_code(r, 200)

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['create_deployment_workload'])
    def test_del_workload(self, args):
        yaml_str = str(args['yaml'])
        deploy_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        allure.dynamic.title('项目管理员' + f"删除{payload_type}工作负载")
        ns = self.ns['name']
        new_workload(self.user, payload_type, deploy_name, yaml_str, ns)

        r = self.user.cce_client.del_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        check_status_code(r, 200)
        cnt = 0
        while cnt < 15:
            sleep(8)
            r_check = self.user.cce_client.get_deployment_by_ns(
                payload_type, settings['CLUSTER_ID'], ns
            )
            result = get_value_from_json(
                r_check, f"$.data[?(@.name=='{deploy_name}')]"
            )
            if not bool(result):
                break
            else:
                cnt = cnt + 1
        assert cnt < 15, f"删除{payload_type}工作负载失败: 操作超时"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['stop_and_start_workload'])
    def test_stop_and_start_workload(self, args):
        allure.dynamic.title('项目管理员' + args['title'])
        yaml_str = str(args['yaml'])
        deploy_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        ns = self.ns['name']
        new_workload(self.user, payload_type, deploy_name, yaml_str, ns)
        r_check = self.user.cce_client.get_deployment_by_ns(
            payload_type, settings['CLUSTER_ID'], ns
        )
        check_status_code(r_check, 200)
        result = get_value_from_json(
            r_check, f"$.data[?(@.name=='{deploy_name}')]"
        )
        assert result['status'] == "running"
        action = self.user.cce_client.stop_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        check_status_code(action, 200)
        cnt = 0
        while cnt < 15:
            sleep(8)
            r_check = self.user.cce_client.get_deployment_by_ns(
                payload_type, settings['CLUSTER_ID'], ns
            )
            result = get_value_from_json(
                r_check, f"$.data[?(@.name=='{deploy_name}')]"
            )
            if result['status'] == "stop":
                break
            else:
                cnt = cnt + 1

        assert cnt < 15, f"操作超时：停止{payload_type}工作负载失败"
        sleep(3)
        action = self.user.cce_client.start_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        check_status_code(action, 200)
        cnt = 0
        while cnt < 15:
            sleep(8)
            r_check = self.user.cce_client.get_deployment_by_ns(
                payload_type, settings['CLUSTER_ID'], ns
            )
            result = get_value_from_json(
                r_check, f"$.data[?(@.name=='{deploy_name}')]"
            )
            if result['status'] == 'running':
                break
            else:
                cnt = cnt + 1
        assert cnt < 15, f"操作超时：启动{payload_type}工作负载失败"
        sleep(4)
        r = self.user.cce_client.del_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['create_deployment_workload'])
    def test_scale_deploy(self, args):
        yaml_str = str(args['yaml'])
        deploy_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        ns = self.ns['name']
        new_workload(self.user, payload_type, deploy_name, yaml_str, ns)
        payload_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        workload = payload_type.strip('s')
        allure.dynamic.title('项目管理员' + f"{workload}实例伸缩")
        if payload_type == "daemonsets":
            post_data = {
                "containers": [
                    {
                        "name": payload_name,
                        "resources": {
                            "requests": {"cpu": 0.1, "memory": "64Mi"},
                            "limits": {"cpu": 1, "memory": "512Mi"},
                        },
                    }
                ]
            }
        else:
            post_data = {"replicas": 2}
        ns = self.ns['name']
        r = self.user.cce_client.scale_workload(
            payload_type, settings['CLUSTER_ID'], ns, payload_name, post_data
        )
        check_status_code(r, 200)
        if payload_type != "daemonsets":
            cnt = 0
            while cnt < 5:
                sleep(8)
                r_check = self.user.cce_client.get_deployment_by_ns(
                    payload_type, settings['CLUSTER_ID'], ns
                )
                result = get_value_from_json(
                    r_check, f"$.data[?(@.name=='{payload_name}')]"
                )
                if result['replicas'] == 2:
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, "操作超时， deployment实例弹性扩展失败"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['job_workload'])
    @allure.title("项目管理员新建job")
    def test_create_job_workload(self, args):
        yaml_str = str(args['yaml'])
        deploy_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        ns = self.ns['name']
        r = self.user.cce_client.create_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, yaml_str
        )
        check_status_code(r, 200)
        cnt = 0
        while cnt < 5:
            sleep(10)
            r_check = self.user.cce_client.get_deployment_by_ns(
                payload_type, settings['CLUSTER_ID'], ns
            )
            deploy = get_value_from_json(
                r_check, f"$.data[?(@.name=='{deploy_name}')]"
            )
            if deploy["status"] == "Complete":
                break
            else:
                cnt = cnt + 1
        assert cnt < 5, "新建job工作负载失败"
        sleep(4)
        r = self.user.cce_client.del_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['job_workload'])
    @allure.title("项目管理员删除job")
    def test_delete_job_workload(self, args):
        with allure.step("新建一个job"):
            yaml_str = str(args['yaml'])
            deploy_name = args['yaml']['metadata']['name']
            payload_type = args['type']
            ns = self.ns['name']
            r = self.user.cce_client.create_deployment_workload(
                payload_type, settings['CLUSTER_ID'], ns, yaml_str
            )
            check_status_code(r, 200)
            cnt = 0
            while cnt < 5:
                sleep(10)
                r_check = self.user.cce_client.get_deployment_by_ns(
                    payload_type, settings['CLUSTER_ID'], ns
                )
                deploy = get_value_from_json(
                    r_check, f"$.data[?(@.name=='{deploy_name}')]"
                )
                if deploy["status"] == "Complete":
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, "新建job工作负载失败"
        with allure.step("删除job工作负载"):
            r = self.user.cce_client.del_deployment_workload(
                payload_type, settings['CLUSTER_ID'], ns, deploy_name
            )
            check_status_code(r, 200)
            cnt = 0
            while cnt < 5:
                sleep(5)
                r_check = self.user.cce_client.get_deployment_by_ns(
                    payload_type, settings['CLUSTER_ID'], ns
                )
                deploy = get_value_from_json(
                    r_check, f"$.data[?(@.name=='{deploy_name}')]"
                )
                if bool(deploy):
                    cnt = cnt + 1
                else:
                    break
            assert cnt < 5, "新建job工作负载失败"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['cronjob_workload'])
    @allure.title("项目管理员新建cronjob工作负载")
    def test_create_cronjob(self, args, paas_proj_admin_login: PAASClient):
        yaml_str = str(args['yaml'])
        deploy_name = args['yaml']['metadata']['name']
        payload_type = args['type']
        ns = self.ns['name']
        r = paas_proj_admin_login.cce_client.create_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, yaml_str
        )
        check_status_code(r, 200)
        cnt = 0
        while cnt < 5:
            sleep(10)
            r_check = paas_proj_admin_login.cce_client.get_deployment_by_ns(
                payload_type, settings['CLUSTER_ID'], ns
            )
            deploy = get_value_from_json(
                r_check, f"$.data[?(@.name=='{deploy_name}')]"
            )
            if deploy["status"] == "running":
                break
            else:
                cnt = cnt + 1
        assert cnt < 5, "新建cronjob工作负载失败"
        sleep(4)
        r = paas_proj_admin_login.cce_client.del_deployment_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        sleep(3)

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['cronjob_workload'])
    @allure.title("项目管理员删除cronjob工作负载")
    def test_delete_cronjob(self, args, paas_proj_admin_login: PAASClient):
        with allure.step("新建一个cronjob"):
            yaml_str = str(args['yaml'])
            deploy_name = args['yaml']['metadata']['name']
            payload_type = args['type']
            ns = self.ns['name']
            r = paas_proj_admin_login.cce_client.create_deployment_workload(
                payload_type, settings['CLUSTER_ID'], ns, yaml_str
            )
            check_status_code(r, 200)
            cnt = 0
            while cnt < 5:
                sleep(10)
                r_check = paas_proj_admin_login.cce_client.get_deployment_by_ns(
                    payload_type, settings['CLUSTER_ID'], ns
                )
                deploy = get_value_from_json(
                    r_check, f"$.data[?(@.name=='{deploy_name}')]"
                )
                if deploy["status"] == "running":
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, "新建cronjob工作负载失败"
        with allure.step("删除cronjob工作负载"):
            r = paas_proj_admin_login.cce_client.del_deployment_workload(
                payload_type, settings['CLUSTER_ID'], ns, deploy_name
            )
            check_status_code(r, 200)
            cnt = 0
            while cnt < 5:
                sleep(5)
                r_check = paas_proj_admin_login.cce_client.get_deployment_by_ns(
                    payload_type, settings['CLUSTER_ID'], ns
                )
                deploy = get_value_from_json(
                    r_check, f"$.data[?(@.name=='{deploy_name}')]"
                )
                if bool(deploy):
                    cnt = cnt + 1
                else:
                    break
            assert cnt < 5, "删除cronjob工作负载失败"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['cronjob_workload'])
    @allure.title("项目管理员停止、启动cronjob工作负载")
    def test_stop_cronjob(self, args, paas_proj_admin_login: PAASClient):
        with allure.step("新建一个cronjob"):
            yaml_str = str(args['yaml'])
            deploy_name = args['yaml']['metadata']['name']
            payload_type = args['type']
            ns = self.ns['name']
            r = paas_proj_admin_login.cce_client.create_deployment_workload(
                payload_type, settings['CLUSTER_ID'], ns, yaml_str
            )
            check_status_code(r, 200)
            cnt = 0
            while cnt < 5:
                sleep(10)
                r_check = paas_proj_admin_login.cce_client.get_deployment_by_ns(
                    payload_type, settings['CLUSTER_ID'], ns
                )
                deploy = get_value_from_json(
                    r_check, f"$.data[?(@.name=='{deploy_name}')]"
                )
                if deploy["status"] == "running":
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, "新建cronjob工作负载失败"
            sleep(4)
        r = paas_proj_admin_login.cce_client.stop_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        check_status_code(r, 200)
        result = wait_action_finish_until_timeout(
            paas_proj_admin_login.cce_client.get_deployment_by_ns,
            f"$.data[?(@.name=='{deploy_name}')].status",
            "stop",
            200,
            10,
            payload_type,
            settings['CLUSTER_ID'],
            ns,
        )
        assert result, f'停止cronjob工作负载{deploy_name}操作失败'
        sleep(5)
        r = paas_proj_admin_login.cce_client.start_workload(
            payload_type, settings['CLUSTER_ID'], ns, deploy_name
        )
        check_status_code(r, 200)
        result = wait_action_finish_until_timeout(
            paas_proj_admin_login.cce_client.get_deployment_by_ns,
            f"$.data[?(@.name=='{deploy_name}')].status",
            "running",
            200,
            10,
            payload_type,
            settings['CLUSTER_ID'],
            ns,
        )
        assert result, f'启动cronjob工作负载{deploy_name}操作失败'
