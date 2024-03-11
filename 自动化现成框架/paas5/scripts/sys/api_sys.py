from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode


class SysAPI(RestAPIBase):
    def create_project(self, project_name, description=None):

        uri = "/api/sys/oapi/v1/projects"

        data = {
            "project": {
                "parent_id": "9052ae85792143ff955c35c52e8e41bd",
                "name": project_name,
            }
        }
        if description:
            data["project"]['description'] = description
        return self._post(uri, data)

    def creat_user(
        self,
        name,
        nickname,
        passwd,
        email,
        project_id,
        project='',
        role='',
        role_id='',
    ):
        """新建用户

        Args:
            name : 用户登录名
            nickname : 昵称
            passwd :密码
            email (_type_): 邮箱地址
            project_id (_type_, optional): 项目ID
            project (str, optional): 项目名称
            role (str, optional): 角色名称
            role_id (str, optional): 角色ID

        Returns:
            requests.response: 返回新建用户请求的 response
        """
        uri = '/api/sys/oapi/v1/users'
        data = {
            "user": {
                "role_id": role_id,
                "name": name,
                "nickname": nickname,
                "password": passwd,
                "passwordRepeat": passwd,
                "email": email,
                "phone": "",
                "domain_id": "default",
                "enabled": True,
                "role_name": role,
                "default_project_id": project_id,
                "projects_and_roles": [
                    {
                        "role_id": role_id,
                        "role_name": role,
                        "project_name": project,
                        "project_id": project_id,
                    }
                ],
                "project_name": project,
            }
        }
        return self._post(uri, json=data)

    def modify_user(self, user_id):
        pass

    def delete_user(self, user_id):
        """删除用户

        Args:
            user_id (_type_): 用户ID

        Returns:
            requests.response:
        """
        uri = "/api/sys/oapi/v1/users/" + user_id
        return self._delete(uri)

    def remove_user_from_project(self, project_id, user_id, role_id):
        """从项目中移除用户

        Args:
            project_id (_type_): 项目id
            user_id (_type_): 用户id
            role_id (_type_): 角色id
        """
        uri = f"/api/sys/oapi/v1/projects/{project_id}/users/{user_id}/roles/{role_id}"
        return self._delete(uri)

    def modify_user_role(self, project, userid, old_role_id, new_role_id):
        uri = "/api/sys/oapi/v1/modifyUserRole"
        data = {
            "projectId": project,
            "roleIdNew": new_role_id,
            "roleIdOld": old_role_id,
            "userId": userid,
        }
        return self._post(uri, data)

    def get_role_list(self):
        uri = "/api/sys/oapi/v1/roles"
        return self._get(uri)

    def get_users_list(self, **kwargs):
        """查询用户列表

        Returns:
            _type_: _description_
        """
        uri = '/api/sys/oapi/v1/users'
        if kwargs:
            uri += "?" + urlencode(kwargs)
        return self._get(uri)

    def delete_project(self, id):
        """删除项目

        Args:
            id (str): 项目id
        """
        uri = '/api/sys/oapi/v1/projects/' + id
        return self._delete(uri)

    def get_project_quota(self, project):
        uri = f'/api/sys/oapi/v1/projects/{project}/quotas'
        return self._get(uri)

    def get_bpm_processes(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        uri = "/api/sys/bpm/processes"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_users_projects(self, user_id, **kwargs):
        """
        获取用户的组织信息

        :param user_id: 用户ID
        :param kwargs:
        :return:
        """

        uri = "/api/sys/oapi/v1/users/" + user_id + "/projects"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def modify_project_quotas(self, project_id, cpu, memory, storage):
        """在系统菜单中修改项目总配额

        Args:
            project_id (str): 项目的ID
            cpu: CPU配额
            memory: 内存配额 单位 G
            storage: 存储
        """

        uri = (
            '/api/sys/oapi/v1/projects/'
            + project_id
            + '/quotas?service=cce-project-manager'
        )
        post_data = {
            "quotas": {"cpu": cpu, "memory": memory, "requests.storage": storage}
        }
        return self._post(uri, post_data)

    def get_projects_list(self, **kwargs):
        """
        获取系统--项目管理列表

        :return:
        """
        uri = "/api/sys/oapi/v1/projects"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_contact_users(self, **kwargs):
        """
        获取告警联系人列表

        :param kwargs:
        :return:
        """
        uri = "/api/sys/alert/api/v1/contact/users"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_project_users(self, projectId, **kwargs):
        uri = f"/api/sys/oapi/v1/projects/{projectId}/users"
        if kwargs:
            uri = uri + '?' + urlencode(kwargs)
        return self._get(uri)

    def get_processes(self, **kwargs):
        """
        流程列表。包括待审批流程

        :param kwargs: 如，nextCandidateUser申请人
        :return:
        """

        uri = "/api/sys/bpm/processes"

        if kwargs:
            uri = uri + '?' + urlencode(kwargs)
        return self._get(uri=uri)

    def deal_with_process(self, process_ids, is_pass, message=""):
        """
        审批流程

        :param process_ids: 流程ID
        :param is_pass: 同意（True）/ 反驳（False）
        :param message: 处理意见
        :return:

        """

        uri = "/api/sys/bpm/processes/batchApprove"

        data = {
            "processIds": process_ids,
            "approval": {"message": message, "pass": is_pass},
        }

        response = self._post(uri=uri, json=data)
        return response

    def check_mqs_cluster_name(self, cluster_id, namespace, name):
        """
        创建kafka时集群名称重名校验

        :param cluster_id: 集群ID
        :param namespace: 命名空间
        :param name: 集群名称
        :return:

        """

        uri = "/api/sys/mqs/base/cluster/check"

        data = {"cceClusterId": cluster_id, "namespace": namespace, "name": name}

        response = self._post(uri=uri, json=data)
        return response

    def create_kafka_cluster(self, name, project_id, cce_cluster_id, cce_cluster_name, owner_id, owner_name, namespace,
                             kafka_info, zk_info, **kwargs):
        """
        创建kafka集群

        :param name: 集群名称
        :param project_id: 项目ID
        :param cce_cluster_id: CCE集群ID
        :param cce_cluster_name: CCE集群名称
        :param owner_id: 所有者ID
        :param owner_name: 所有者名称
        :param namespace: 命名空间名称
        :param kafka_info: kafka信息
        :param zk_info: zookeeper信息
        :param kwargs:
        :return:

        """

        uri = "/api/sys/mqs/base/cluster"

        data = {
            "name": name,
            "type": "kafka",
            "projectId": project_id,
            "cceClusterId": cce_cluster_id,
            "cceClusterName": cce_cluster_name,
            "ownerId": owner_id,
            "owner": owner_name,
            "namespace": namespace,
            "replicas": kafka_info['replicas'],
            "version": kafka_info['kafka_version'] if 'kafka_version' in kafka_info.keys() else "3.1.0",
            "cpu": {
                "request": int(kafka_info['cpu_info']['request']) * 1000,
                "limit": int(kafka_info['cpu_info']['limit']) * 1000,
            },
            "memory": {
                "request": int(kafka_info['memory_info']['request'])
                * 1024
                * 1024
                * 1024
                * 1000,
                "limit": int(kafka_info['memory_info']['limit'])
                * 1024
                * 1024
                * 1024
                * 1000,
            },
            "storage": {
                "type": "storageclass",
                "name": kafka_info['storage_info']['name'],
                "size": kafka_info['storage_info']['size'],
            },
            "custom": {
                "replicas": zk_info['replicas'],
                "version": zk_info['zk_version'] if 'zk_version' in zk_info.keys() else "3.6.3",
                "cpu": {
                    "request": int(zk_info['cpu_info']['request']) * 1000,
                    "limit": int(zk_info['cpu_info']['limit']) * 1000,
                },
                "memory": {
                    "request": int(zk_info['memory_info']['request'])
                    * 1024
                    * 1024
                    * 1024
                    * 1000,
                    "limit": int(zk_info['memory_info']['limit'])
                    * 1024
                    * 1024
                    * 1024
                    * 1000,
                },
                "storage": {
                    "type": "storageclass",
                    "name": zk_info['storage_info']['name'],
                    "size": zk_info['storage_info']['size'],
                },
            },
            "externalAccess": kwargs['external_access'] if 'external_access' in kwargs.keys() else False,
            "monitorInterval": kafka_info['monitor_interval'],
            "alertConfig": {
                "methods": [
                    "email"
                ],
                "period": "4h",
                "sendResolved": False,
                "contactUsers": []
            }
        }

        response = self._post(uri=uri, json=data)
        return response

    def restart_kafka_cluster(self, cluster_id):
        """
        重启kafka集群

        :param cluster_id: 集群ID
        :return:

        """

        uri = "/api/sys/mqs/base/cluster/" + cluster_id + "/restart"

        response = self._post(uri=uri)
        return response

    def create_zookeeper_cluster(
        self,
        name,
        project_id,
        cce_cluster_id,
        cce_cluster_name,
        owner_id,
        owner_name,
        namespace,
        zk_info,
        **kwargs
    ):
        """
        创建zookeeper集群

        :param name: 集群名称
        :param project_id: 项目ID
        :param cce_cluster_id: CCE集群ID
        :param cce_cluster_name: CCE集群名称
        :param owner_id: 所有者ID
        :param owner_name: 所有者名称
        :param namespace: 命名空间名称
        :param zk_info: zookeeper信息
        :return:

        """

        uri = "/api/sys/mqs/base/cluster"

        data = {
            "name": name,
            "type": "zookeeper",
            "projectId": project_id,
            "cceClusterId": cce_cluster_id,
            "cceClusterName": cce_cluster_name,
            "ownerId": owner_id,
            "owner": owner_name,
            "namespace": namespace,
            "replicas": zk_info['replicas'],
            "version": zk_info['version'] if 'version' in zk_info.keys() else "3.6.3",
            "cpu": {
                "request": int(zk_info['cpu_info']['request']) * 1000,
                "limit": int(zk_info['cpu_info']['limit']) * 1000,
            },
            "memory": {
                "request": int(zk_info['memory_info']['request'])
                * 1024
                * 1024
                * 1024
                * 1000,
                "limit": int(zk_info['memory_info']['limit'])
                * 1024
                * 1024
                * 1024
                * 1000,
            },
            "storage": {
                "type": "storageclass",
                "name": zk_info['storage_info']['name'],
                "size": zk_info['storage_info']['size'],
            },
            "externalAccess": kwargs['external_access'] if 'external_access' in kwargs.keys() else False,
            "monitorInterval": zk_info['monitor_interval'],
            "alertConfig": {
                "methods": ["email"] if 'email' in kwargs.keys() else [],
                "period": "4h",
                "sendResolved": False,
                "contactUsers": []
            }
        }

        response = self._post(uri=uri, json=data)
        return response

    def get_mqs_cluster(self, **kwargs):
        """
        查询集群列表

        :param kwargs: 例如，type=kafka，
        :return:

        """

        uri = "/api/sys/mqs/base/cluster"

        if kwargs:
            uri = uri + '?' + urlencode(kwargs)
        return self._get(uri=uri)

    def delete_mqs_cluster(self, mqs_cluster_id):
        """
        删除中间件集群

        :param mqs_cluster_id: 中间件集群ID
        :return:
        """
        uri = "/api/sys/mqs/base/cluster/" + mqs_cluster_id
        return self._delete(uri=uri)

    def get_license_permit(self,**kwargs):
        """
        获取授权信息

        :param kwargs:
        """
        uri = '/api/sys/license/v1/permit/detailwithsn'
        if kwargs:
            uri += '?' + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_root_user_list(self, page=1, pagesize=100, **kwargs):
        """获取root组织用户列表，name关键字参数为精确查找"""
        project_id = "9052ae85792143ff955c35c52e8e41bd"
        uri = f'/api/sys/oapi/v2/projects/{project_id}/users?page={page}&pagesize={pagesize}&'
        if kwargs:
            uri += urlencode(kwargs)
        response = self._get(uri=uri)
        return response