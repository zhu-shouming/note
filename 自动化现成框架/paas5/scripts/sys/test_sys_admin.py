# import pytest
# import os
# import yaml
# from scripts.sys.handler_sys import *
# from resource.utils.common import *

# cur_path = os.path.dirname(os.path.realpath(__file__))
# datafile = os.path.join(cur_path, 'data_admin.yaml')

# with open(datafile, encoding='utf-8') as f:
#     data = yaml.safe_load(f)


# @pytest.mark.sys
# @allure.feature("系统")
# @allure.story("系统")
# class TestSys:
#     @pytest.mark.Smoke
#     @pytest.mark.parametrize('args', data["create_project"])
#     def test_create_project(self, paas_admin_login: PAASClient, args):
#         allure.dynamic.title(args['title'])
#         with allure.step(" 设置项目名称 和描述"):
#             name = "autoP" + get_random_string(4)
#             description = args['description']
#             response = paas_admin_login.sys_client.create_project(name, description)
#             check_status_code(response, 200)

#         with allure.step("校验新建项目是否成功"):
#             response = paas_admin_login.sys_client.get_projects_list()
#             check_status_code(response, 200)
#             sleep(2)
#             new_project = get_value_from_json(
#                 response, "$.data.res[?(@.name=='{}')]".format(name)
#             )
#             assert new_project, "项目管理列表中找不到新建的项目"
#             assert new_project['name'] == name, "新建项目的名字和输入的名字不一致"
#             assert new_project['description'] == description, "新建项目的描述和输入的描述不一致"
#             paas_admin_login.sys_client.delete_project(new_project['id'])

#     @pytest.mark.L5
#     @pytest.mark.Smoke
#     @allure.title("删除项目")
#     def test_delete_project(self, paas_admin_login: PAASClient):
#         with allure.step("新建一个待删除的项目"):
#             name = "fordel" + get_random_string(4)
#             project = new_project(paas_admin_login, name)
#         with allure.step("删除该项目"):
#             response = paas_admin_login.sys_client.delete_project(project['id'])
#             check_status_code(response, 200)
#         with allure.step("校验删除是否成功"):
#             cnt = 0
#             while cnt < 5:
#                 project = get_project_by_name(paas_admin_login, name)
#                 if not project:
#                     break
#                 sleep(2)
#                 cnt = cnt + 1
#             assert project is False, "删除项目失败,该项目仍然存在于列表中"

#     @pytest.mark.L5
#     @pytest.mark.Smoke
#     @pytest.mark.parametrize('args', data['create_user'])
#     def test_create_user(self, paas_admin_login: PAASClient, args):
#         allure.dynamic.title(args['title'])
#         with allure.step("新建一个项目"):
#             pro_name = "auto" + get_random_string(4)
#             project = new_project(paas_admin_login, pro_name)
#         with allure.step("设置用户相关信息"):
#             name = "auto" + get_random_string(5)
#             nickname = args['nickname']
#             passwd = args["passwd"]
#             email = args["email"]
#             if "role" in args:
#                 role = args["role"]
#                 response = paas_admin_login.sys_client.get_role_list()
#                 check_status_code(response, 200)
#                 role_id = get_value_from_json(
#                     response, f"$.data[?(@.name=='{role}')].id"
#                 )
#                 assert role_id, f"获取角色ID失败，指定的角色名为：{role}"
#                 project_id = project['id']
#                 project_name = pro_name
#                 response = paas_admin_login.sys_client.creat_user(
#                     name,
#                     nickname,
#                     passwd,
#                     email,
#                     project_id,
#                     project_name,
#                     role,
#                     role_id,
#                 )
#             else:
#                 response = paas_admin_login.sys_client.creat_user(
#                     name, nickname, passwd, email
#                 )
#         with allure.step("校验新建用户操作是否成功"):
#             check_status_code(response, 200)
#             cnt = 0
#             while cnt < 5:
#                 response = paas_admin_login.sys_client.get_users_list(
#                     page=1, pagesize=10, name=name
#                 )
#                 check_status_code(response)
#                 user_new = get_value_from_json(
#                     response, f"$.data.res[?(@.name=='{name}')]"
#                 )
#                 if user_new:
#                     break
#                 cnt = cnt + 1
#                 sleep(5)
#             assert user_new, f"用户列表中找不到新建的用户{name}"
#         with allure.step("清理测试资源"):
#             paas_admin_login.sys_client.remove_user_from_project(
#                 project_id, user_new['id'], user_new['role_id']
#             )
#             paas_admin_login.sys_client.delete_user(user_new['id'])
#             paas_admin_login.sys_client.delete_project(project_id)

#     @pytest.mark.L5
#     @pytest.mark.Smoke
#     @pytest.mark.parametrize("args", data["modify_project_quota"])
#     def test_modify_project_quota(self, paas_admin_login: PAASClient, args):
#         allure.dynamic.title(args['title'])
#         cpu = args['cpu_quota']
#         mem = args['mem_quota']
#         storage = args['store_quota']
#         with allure.step("新建一个项目"):
#             name = "auto" + get_random_string(4)
#             project = new_project(paas_admin_login, name)
#         with allure.step("修改项目配额"):
#             resp = paas_admin_login.sys_client.modify_project_quotas(
#                 project['id'], cpu, mem, storage
#             )
#             check_status_code(resp, 200)

#             check = paas_admin_login.sys_client.get_project_quota(project['id'])
#             quota_info = get_value_from_json(check, "$.data[*].limited")
#             assert int(quota_info["cpu"]) == cpu, "cpu配额和预期不符"
#             assert int(quota_info["memory"]) == mem, "内存配额和预期不符"
#             assert int(quota_info["requests.storage"]) == storage, "存储配额和预期不符"

#         with allure.step("清理环境"):
#             clean = paas_admin_login.sys_client.delete_project(project['id'])
#             check_status_code(clean, 200)
