from time import sleep
import pytest
import allure
import os
from scripts.cce.handler_cce import *
import yaml
from config.config import settings


@pytest.mark.cce
@allure.feature("云容器引擎")
@allure.story("云容器引擎")
class TestCCE:
    @pytest.mark.L5
    @allure.title("新建命名空间")
    def test_add_namespace(self, paas_admin_login: PAASClient):
        name = "auto" + get_random_string(4).lower()
        description = ""
        clusterId = settings['CLUSTER_ID']
        r = paas_admin_login.cce_client.add_namespace(name, clusterId, description)
        check_status_code(r, 200)
        assert get_value_from_json(r, "$..status")
        time.sleep(4)
        r_check = paas_admin_login.cce_client.get_ns_of_cluster(clusterId, name=name)
        check_status_code(r_check, 200)
        assert get_value_from_json(r_check, "$..total") == 1, "新建命名空间失败"
        time.sleep(2)
        paas_admin_login.cce_client.del_namespace(name, clusterId)

    @pytest.mark.L5
    @allure.title("删除命名空间")
    def test_del_namespace(self, paas_admin_login: PAASClient):
        with allure.step("新建命名空间"):
            namespace = new_namespace(paas_admin_login)
            name = namespace['name']
            clusterid = settings['CLUSTER_ID']
        with allure.step("删除命名空间"):
            r = paas_admin_login.cce_client.del_namespace(name, clusterid)
            check_status_code(r, 200)
            cnt = 0
            while cnt < 4:
                sleep(5)
                r_check = paas_admin_login.cce_client.get_ns_of_cluster(
                    clusterid, name=name
                )
                check_status_code(r_check, 200)
                if get_value_from_json(r_check, "$..total") == 0:
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 4, "删除命名空间失败"
