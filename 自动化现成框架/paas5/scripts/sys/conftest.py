import pytest
from .handler_sys import new_project
from resource.base.client import PAASClient
from resource.utils.common import *


@pytest.fixture(scope="function")
def sys_env(paas_admin_login: PAASClient):
    project = new_project(paas_admin_login)
    data = {}
    data['project_id'] = project['id']
    data['project_name'] = project['name']
    data['users'] = []
    yield data
    for user_id in data['users']:
        res = paas_admin_login.sys_client.delete_user(user_id)
        check_status_code(res, 200)
    del_pro = paas_admin_login.sys_client.delete_project(data['project_id'])
    check_status_code(del_pro, 200)
