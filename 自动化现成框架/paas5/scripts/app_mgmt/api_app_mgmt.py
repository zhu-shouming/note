import allure

from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode


class AppMgmtAPI(RestAPIBase):

    def create_app_group(self, name, namespace, engine_type="Spring Cloud", svc_engine_id=""):
        """
        创建应用组

        :param name: 应用组名称
        :param engine_type: 微服务引擎类型：Spring Cloud; Istio; others
        :param namespace: 自定义命名空间
        :param svc_engine_id: SpringCloud微服务引擎ID
        :return:
        """
        uri = "/api/cloud/app-mgmt/v1.0/appgroups"

        data = {
            "name": name,
            "type": engine_type,
            "namespace": namespace,
            "svc_engine_id": svc_engine_id
        }

        response = self._post(uri=uri, json=data)
        return response

    def delete_app_group(self, app_group_id, **kwargs):
        """
        删除应用组

        :param app_group_id: 应用组ID
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}"
        if kwargs:
            uri += '?' + urlencode(kwargs)
        response = self._delete(uri=uri)
        return response

    def get_app_group_detail(self, app_group_id):
        """
        获取应用组详情

        :param app_group_id: 应用组ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}"
        response = self._get(uri=uri)
        return response

    def create_app_of_jar(self, app_group_id, app_name, app_version, app_group_ns, resource_type, app_type_info,
                          cluster_type, deploy_type, cluster_id, version_id, jdk_version, container_spec, **kwargs):
        """
        创建jar应用

        :param app_group_id: 应用组ID
        :param app_name: 应用名称
        :param app_version: 应用版本号
        :param app_group_ns: 应用组命名空间
        :param app_type_info: 应用类型的信息
        :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
        :param resource_type: 资源类型。当前缺省为容器集群
        :param cluster_type: 集群类型
        :param cluster_id: 集群ID
        :param container_spec: 容器规格
        :param version_id: 安装包版本ID
        :param jdk_version: JDK版本
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}/apps"

        affinity = {
            "nodeAffinity": {
                "preferred": {
                    "in": kwargs['node_affinity']['preferred'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['preferred'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else []
                },
                "required": {
                    "in": kwargs['node_affinity']['required'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['required'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                }
            },
            "podAffinity": {
                "perferPodAffinityRules": kwargs['pod_affinity'][
                    'perferPodAffinityRules'] if 'pod_affinity' in kwargs.keys() else [],
                "requirePodAffinityRules": kwargs['pod_affinity'][
                    'requirePodAffinityRules'] if 'pod_affinity' in kwargs.keys() else []
            },
            "podAntiAffinity": {
                "perferPodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'perferPodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else [],
                "requirePodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'requirePodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else []
            }
        }

        pvc_resource = {
            "pv": kwargs['pvc_resource']['pv'] if 'pvc_resource' in kwargs.keys() else [],
            "pvc": kwargs['pvc_resource']['pvc'] if 'pvc_resource' in kwargs.keys() else []
        }

        resources = [
            {
                "security": {
                    "capabilities": kwargs['security']['capabilities'] if 'security' in kwargs.keys() else [],
                    "hostIPC": kwargs['security']['hostIPC'] if 'security' in kwargs.keys() else False,
                    "hostNetwork": kwargs['security']['hostNetwork'] if 'security' in kwargs.keys() else False,
                    "hostPID": kwargs['security']['hostPID'] if 'security' in kwargs.keys() else False,
                    "privileged": kwargs['security']['privileged'] if 'security' in kwargs.keys() else False,
                    "readOnlyRootFilesystem": kwargs['security'][
                        'readOnlyRootFilesystem'] if 'security' in kwargs.keys() else False,
                    "runAsUser": kwargs['security']['runAsUser'] if 'security' in kwargs.keys() else '',
                }
            },
            {
                "apiVersion": app_type_info['apiVersion'],
                "kind": app_type_info['kind'],
                "metadata": {
                    "labels": {
                        "app": app_name
                    },
                    "name": app_name,
                    "namespace": app_group_ns
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": app_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": app_name
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "args": None,
                                    "command": None,
                                    "env": [],
                                    "image": '',
                                    "imagePullPolicy": "Always",
                                    "name": app_name,
                                    "ports": [],
                                    "resources": {
                                        "requests": {
                                            "cpu": container_spec['cpu_request'],
                                            "memory": container_spec['mem_request']
                                        },
                                        "limits": {
                                            "cpu": container_spec['cpu_limit'],
                                            "memory": container_spec['mem_limit']
                                        }
                                    },
                                    "securityContext": {
                                        "privileged": True
                                    },
                                    "volumeMounts": kwargs['volume_mounts'] if 'volume_mounts' in kwargs.keys() else []
                                }
                            ],
                            "dnsPolicy": kwargs['svc_access_contro'][
                                'dnsPolicy'] if 'svc_access_contro' in kwargs.keys() else 'ClusterFirst',
                            "initContainers": kwargs['init_containers'] if 'init_containers' in kwargs.keys() else [],
                            "restartPolicy": "Always",
                            "schedulerName": "default-scheduler",
                            "securityContext": {},
                            "serviceAccount": app_name,
                            "serviceAccountName": app_name,
                            "volumes": kwargs['volumes'] if 'volumes' in kwargs.keys() else []
                        }
                    }
                }
            }
        ]
        # 服务访问控制
        if 'svc_access_control_info' in kwargs.keys():
            ports = [
                {
                    "containerPort": kwargs['svc_access_control_info']['port'],
                    "protocol": "TCP"
                }
            ]
            resources[1]['spec']['template']['spec']['containers'][0]['ports'] = ports

            resources_svc_info = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": app_name,
                    "namespace": app_group_ns,
                    "labels": {
                        "app": app_name
                    }
                },
                "spec": {
                    "ports": [
                        {
                            "name": app_name,
                            "protocol": "TCP",
                            "targetPort": kwargs['svc_access_control_info']['targetPort'],
                            "port": kwargs['svc_access_control_info']['port'],
                            "nodePort": kwargs['svc_access_control_info']['nodePort']
                        }
                    ],
                    "selector": {
                        "app": app_name
                    },
                    "sessionAffinity": "None",
                    "type": "NodePort"
                }
            }
            resources.append(resources_svc_info)

        data = {
            "name": app_name,
            "version": app_version,
            "description": kwargs['app_description'] if 'app_description' in kwargs.keys() else '',
            "package_type": 'jar',
            "resource_type": resource_type,
            "cluster_type": cluster_type,
            "workload_type": deploy_type,
            "appEntranceUrl": kwargs['app_entrance_url'] if 'app_entrance_url' in kwargs else '',
            "cluster_id": cluster_id,
            "metadata": {
                "version_id": version_id,
                "jdk_version": jdk_version,
                "env": kwargs['env'] if 'env' in kwargs.keys() else None,
                "jvm_args": kwargs['jvm_args'] if 'jvm_args' in kwargs.keys() else '',
                "logrotateCron": kwargs['logrotateCron'] if 'logrotateCron' in kwargs.keys() else None,
                "is_skywalking": kwargs['sw_info']['is_skywalking'] if 'sw_info' in kwargs.keys() else False,
                "image_metadata": {
                    "metadata": {
                        "affinity": affinity,
                        "pvcResource": pvc_resource,
                        "resources": resources
                    },
                },
                "skywalking_type": kwargs['sw_info']['skywalking_type'] if 'sw_info' in kwargs.keys() else 'public',
                "skywalking_collector_backend_service": kwargs['sw_info']['skywalking_collector_backend_service'] if
                'sw_info' in kwargs.keys() else '',
                "skywalking_version": kwargs['sw_info']['skywalking_version'] if 'sw_info' in kwargs.keys() else '',
                "skywalking_name": kwargs['sw_info']['skywalking_name'] if 'sw_info' in kwargs.keys() else 'default',
                "skywalking_instance_id": kwargs['sw_info'][
                    'skywalking_instance_id'] if 'sw_info' in kwargs.keys() else 'default'
            }
        }

        if cluster_type == "mcpCluster":
            data['mcpPlaintextList'] = kwargs['mcp_plaintext_list']
            data['metadata'].pop("skywalking_type")
            data['metadata'].pop("skywalking_collector_backend_service")
            data['metadata'].pop("skywalking_version")
            data['metadata'].pop("skywalking_name")
            data['metadata'].pop("skywalking_instance_id")

        response = self._post(uri=uri, json=data)
        return response

    def create_app_of_war(self, app_group_id, app_name, app_version, app_group_ns, resource_type, app_type_info,
                          cluster_type, deploy_type, cluster_id, version_id, tomcat_version, jdk_version,
                          container_spec, **kwargs):
        """
        创建war应用

        :param app_group_id: 应用组ID
        :param app_name: 应用名称
        :param app_version: 应用版本号
        :param app_group_ns: 应用组命名空间
        :param app_type_info: 应用类型的信息
        :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
        :param resource_type: 资源类型。当前缺省为容器集群
        :param cluster_type: 集群类型
        :param cluster_id: 集群ID
        :param container_spec: 容器规格
        :param version_id: 安装包版本ID
        :param tomcat_version: TOMCAT版本
        :param jdk_version: JDK版本
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}/apps"

        affinity = {
            "nodeAffinity": {
                "preferred": {
                    "in": kwargs['node_affinity']['preferred'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['preferred'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else []
                },
                "required": {
                    "in": kwargs['node_affinity']['required'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['required'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                }
            },
            "podAffinity": {
                "perferPodAffinityRules": kwargs['pod_affinity'][
                    'perferPodAffinityRules'] if 'pod_affinity' in kwargs.keys() else [],
                "requirePodAffinityRules": kwargs['pod_affinity'][
                    'requirePodAffinityRules'] if 'pod_affinity' in kwargs.keys() else []
            },
            "podAntiAffinity": {
                "perferPodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'perferPodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else [],
                "requirePodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'requirePodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else []
            }
        }

        pvc_resource = {
            "pv": kwargs['pvc_resource']['pv'] if 'pvc_resource' in kwargs.keys() else [],
            "pvc": kwargs['pvc_resource']['pvc'] if 'pvc_resource' in kwargs.keys() else []
        }

        resources = [
            {
                "security": {
                    "capabilities": kwargs['security']['capabilities'] if 'security' in kwargs.keys() else [],
                    "hostIPC": kwargs['security']['hostIPC'] if 'security' in kwargs.keys() else False,
                    "hostNetwork": kwargs['security']['hostNetwork'] if 'security' in kwargs.keys() else False,
                    "hostPID": kwargs['security']['hostPID'] if 'security' in kwargs.keys() else False,
                    "privileged": kwargs['security']['privileged'] if 'security' in kwargs.keys() else False,
                    "readOnlyRootFilesystem": kwargs['security'][
                        'readOnlyRootFilesystem'] if 'security' in kwargs.keys() else False,
                    "runAsUser": kwargs['security']['runAsUser'] if 'security' in kwargs.keys() else '',
                }
            },
            {
                "apiVersion": app_type_info['apiVersion'],
                "kind": app_type_info['kind'],
                "metadata": {
                    "labels": {
                        "app": app_name
                    },
                    "name": app_name,
                    "namespace": app_group_ns
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": app_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": app_name
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "args": None,
                                    "command": None,
                                    "env": [],
                                    "image": '',
                                    "imagePullPolicy": "Always",
                                    "name": app_name,
                                    "ports": [],
                                    "resources": {
                                        "requests": {
                                            "cpu": container_spec['cpu_request'],
                                            "memory": container_spec['mem_request']
                                        },
                                        "limits": {
                                            "cpu": container_spec['cpu_limit'],
                                            "memory": container_spec['mem_limit']
                                        }
                                    },
                                    "securityContext": {
                                        "privileged": True
                                    },
                                    "volumeMounts": kwargs['volume_mounts'] if 'volume_mounts' in kwargs.keys() else []
                                }
                            ],
                            "dnsPolicy": kwargs['svc_access_contro'][
                                'dnsPolicy'] if 'svc_access_contro' in kwargs.keys() else 'ClusterFirst',
                            "initContainers": kwargs['init_containers'] if 'init_containers' in kwargs.keys() else [],
                            "restartPolicy": "Always",
                            "schedulerName": "default-scheduler",
                            "securityContext": {},
                            "serviceAccount": app_name,
                            "serviceAccountName": app_name,
                            "volumes": kwargs['volumes'] if 'volumes' in kwargs.keys() else []
                        }
                    }
                }
            }
        ]
        # 服务访问控制
        if 'svc_access_control_info' in kwargs.keys():
            ports = [
                {
                    "containerPort": kwargs['svc_access_control_info']['port'],
                    "protocol": "TCP"
                }
            ]
            resources[1]['spec']['template']['spec']['containers'][0]['ports'] = ports

            resources_svc_info = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": app_name,
                    "namespace": app_group_ns,
                    "labels": {
                        "app": app_name
                    }
                },
                "spec": {
                    "ports": [
                        {
                            "name": app_name,
                            "protocol": "TCP",
                            "targetPort": kwargs['svc_access_control_info']['targetPort'],
                            "port": kwargs['svc_access_control_info']['port'],
                            "nodePort": kwargs['svc_access_control_info']['nodePort']
                        }
                    ],
                    "selector": {
                        "app": app_name
                    },
                    "sessionAffinity": "None",
                    "type": "NodePort"
                }
            }
            resources.append(resources_svc_info)

        data = {
            "name": app_name,
            "version": app_version,
            "description": kwargs['app_description'] if 'app_description' in kwargs.keys() else '',
            "package_type": 'war',
            "resource_type": resource_type,
            "cluster_type": cluster_type,
            "workload_type": deploy_type,
            "appEntranceUrl": kwargs['app_entrance_url'] if 'app_entrance_url' in kwargs else '',
            "cluster_id": cluster_id,
            "metadata": {
                "version_id": version_id,
                "env": kwargs['env'] if 'env' in kwargs.keys() else None,
                "base_jdk_version": jdk_version,
                "tomcat_version": tomcat_version,
                "jvm_args": kwargs['jvm_args'] if 'jvm_args' in kwargs.keys() else '',
                "logrotateCron": kwargs['logrotateCron'] if 'logrotateCron' in kwargs.keys() else None,
                "setting_file_id": "",
                "is_skywalking": kwargs['sw_info']['is_skywalking'] if 'sw_info' in kwargs.keys() else False,
                "image_metadata": {
                    "metadata": {
                        "affinity": affinity,
                        "pvcResource": pvc_resource,
                        "resources": resources
                    },
                },
                "skywalking_type": kwargs['sw_info']['skywalking_type'] if 'sw_info' in kwargs.keys() else 'public',
                "skywalking_collector_backend_service": kwargs['sw_info']['skywalking_collector_backend_service'] if
                'sw_info' in kwargs.keys() else '',
                "skywalking_version": kwargs['sw_info']['skywalking_version'] if 'sw_info' in kwargs.keys() else '',
                "skywalking_name": kwargs['sw_info']['skywalking_name'] if 'sw_info' in kwargs.keys() else 'default',
                "skywalking_instance_id": kwargs['sw_info'][
                    'skywalking_instance_id'] if 'sw_info' in kwargs.keys() else 'default'
            }
        }

        if cluster_type == "mcpCluster":
            data['mcpPlaintextList'] = kwargs['mcp_plaintext_list']
            resources[1]['spec']['template']['spec']['initContainers'] = kwargs[
                'init_containers'] if 'init_containers' in kwargs.keys() else []
            data['metadata'].pop("skywalking_type")
            data['metadata'].pop("skywalking_collector_backend_service")
            data['metadata'].pop("skywalking_version")
            data['metadata'].pop("skywalking_name")
            data['metadata'].pop("skywalking_instance_id")

        response = self._post(uri=uri, json=data)
        return response

    def create_app_of_front(self, app_group_id, app_name, app_version, app_group_ns, resource_type,
                            app_type_info, cluster_type, deploy_type, cluster_id, version_id, tomcat_version,
                            jdk_version, nginx_version, container_spec, **kwargs):
        """
        创建前端包应用

        :param app_group_id: 应用组ID
        :param app_name: 应用名称
        :param app_version: 应用版本号
        :param app_group_ns: 应用组命名空间
        :param app_type_info: 应用类型的信息
        :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
        :param resource_type: 资源类型。当前缺省为容器集群
        :param cluster_type: 集群类型
        :param cluster_id: 集群ID
        :param container_spec: 容器规格
        :param version_id: 安装包版本ID
        :param tomcat_version: TOMCAT版本
        :param jdk_version: JDK版本
        :param nginx_version: NGINX版本
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}/apps"

        affinity = {
            "nodeAffinity": {
                "preferred": {
                    "in": kwargs['node_affinity']['preferred'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['preferred'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else []
                },
                "required": {
                    "in": kwargs['node_affinity']['required'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['required'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                }
            },
            "podAffinity": {
                "perferPodAffinityRules": kwargs['pod_affinity'][
                    'perferPodAffinityRules'] if 'pod_affinity' in kwargs.keys() else [],
                "requirePodAffinityRules": kwargs['pod_affinity'][
                    'requirePodAffinityRules'] if 'pod_affinity' in kwargs.keys() else []
            },
            "podAntiAffinity": {
                "perferPodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'perferPodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else [],
                "requirePodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'requirePodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else []
            }
        }

        pvc_resource = {
            "pv": kwargs['pvc_resource']['pv'] if 'pvc_resource' in kwargs.keys() else [],
            "pvc": kwargs['pvc_resource']['pvc'] if 'pvc_resource' in kwargs.keys() else []
        }

        resources = [
            {
                "security": {
                    "capabilities": kwargs['security']['capabilities'] if 'security' in kwargs.keys() else [],
                    "hostIPC": kwargs['security']['hostIPC'] if 'security' in kwargs.keys() else False,
                    "hostNetwork": kwargs['security']['hostNetwork'] if 'security' in kwargs.keys() else False,
                    "hostPID": kwargs['security']['hostPID'] if 'security' in kwargs.keys() else False,
                    "privileged": kwargs['security']['privileged'] if 'security' in kwargs.keys() else False,
                    "readOnlyRootFilesystem": kwargs['security'][
                        'readOnlyRootFilesystem'] if 'security' in kwargs.keys() else False,
                    "runAsUser": kwargs['security']['runAsUser'] if 'security' in kwargs.keys() else '',
                }
            },
            {
                "apiVersion": app_type_info['apiVersion'],
                "kind": app_type_info['kind'],
                "metadata": {
                    "labels": {
                        "app": app_name
                    },
                    "name": app_name,
                    "namespace": app_group_ns
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": app_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": app_name
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "args": None,
                                    "command": None,
                                    "env": [],
                                    "image": '',
                                    "imagePullPolicy": "Always",
                                    "name": app_name,
                                    "ports": [],
                                    "resources": {
                                        "requests": {
                                            "cpu": container_spec['cpu_request'],
                                            "memory": container_spec['mem_request']
                                        },
                                        "limits": {
                                            "cpu": container_spec['cpu_limit'],
                                            "memory": container_spec['mem_limit']
                                        }
                                    },
                                    "securityContext": {
                                        "privileged": True
                                    },
                                    "volumeMounts": kwargs['volume_mounts'] if 'volume_mounts' in kwargs.keys() else []
                                }
                            ],
                            "dnsPolicy": kwargs['svc_access_contro'][
                                'dnsPolicy'] if 'svc_access_contro' in kwargs.keys() else 'ClusterFirst',
                            "initContainers": kwargs['init_containers'] if 'init_containers' in kwargs.keys() else [],
                            "restartPolicy": "Always",
                            "schedulerName": "default-scheduler",
                            "securityContext": {},
                            "serviceAccount": app_name,
                            "serviceAccountName": app_name,
                            "volumes": kwargs['volumes'] if 'volumes' in kwargs.keys() else []
                        }
                    }
                }
            }
        ]
        # 服务访问控制
        if 'svc_access_control_info' in kwargs.keys():
            ports = [
                {
                    "containerPort": kwargs['svc_access_control_info']['port'],
                    "protocol": "TCP"
                }
            ]
            resources[1]['spec']['template']['spec']['containers'][0]['ports'] = ports

            resources_svc_info = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": app_name,
                    "namespace": app_group_ns,
                    "labels": {
                        "app": app_name
                    }
                },
                "spec": {
                    "ports": [
                        {
                            "name": app_name,
                            "protocol": "TCP",
                            "targetPort": kwargs['svc_access_control_info']['targetPort'],
                            "port": kwargs['svc_access_control_info']['port'],
                            "nodePort": kwargs['svc_access_control_info']['nodePort']
                        }
                    ],
                    "selector": {
                        "app": app_name
                    },
                    "sessionAffinity": "None",
                    "type": "NodePort"
                }
            }
            resources.append(resources_svc_info)

        data = {
            "name": app_name,
            "version": app_version,
            "description": kwargs['app_description'] if 'app_description' in kwargs.keys() else '',
            "package_type": 'web',
            "resource_type": resource_type,
            "cluster_type": cluster_type,
            "workload_type": deploy_type,
            "appEntranceUrl": kwargs['app_entrance_url'] if 'app_entrance_url' in kwargs else '',
            "cluster_id": cluster_id,
            "metadata": {
                "version_id": version_id,
                "env": kwargs['env'] if 'env' in kwargs.keys() else None,
                "base_jdk_version": jdk_version,
                "tomcat_version": tomcat_version,
                "setting_file_id": "",
                "jvm_args": kwargs['jvm_args'] if 'jvm_args' in kwargs.keys() else '',
                "logrotateCron": kwargs['logrotateCron'] if 'logrotateCron' in kwargs.keys() else None,
                "is_skywalking": False,
                "enable_ssl": kwargs['enable_ssl'] if 'enable_ssl' in kwargs else False,
                "nginx_version": nginx_version,
                "image_metadata": {
                    "metadata": {
                        "affinity": affinity,
                        "pvcResource": pvc_resource,
                        "resources": resources
                    },
                }
            }
        }

        if cluster_type == "mcpCluster":
            data['mcpPlaintextList'] = kwargs['mcp_plaintext_list']
            resources[1]['spec']['template']['spec']['initContainers'] = kwargs[
                'init_containers'] if 'init_containers' in kwargs.keys() else []

        response = self._post(uri=uri, json=data)
        return response

    def create_app_of_helm(self, app_group_id, app_name, app_version, resource_type, cluster_type, cluster_id,
                           version_id, container_spec, **kwargs):
        """
        创建HELM包应用

        :param app_group_id: 应用组ID
        :param app_name: 应用名称
        :param app_version: 应用版本号
        :param resource_type: 资源类型。当前缺省为容器集群
        :param cluster_type: 集群类型
        :param cluster_id: 集群ID
        :param version_id: 安装包版本ID
        :param container_spec: 容器规格
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}/apps"

        data = {
            "name": app_name,
            "version": app_version,
            "description": kwargs['app_description'] if 'app_description' in kwargs.keys() else '',
            "package_type": 'helm',
            "resource_type": resource_type,
            "cluster_type": cluster_type,
            "appEntranceUrl": kwargs['app_entrance_url'] if 'app_entrance_url' in kwargs else '',
            "cluster_id": cluster_id,
            "metadata": {
                "quota_cpu": int(container_spec['quota_cpu']),
                "quota_memory": container_spec['quota_memory'] + "Mi",
                "quota_storage": int(container_spec['quota_storage']),
                "version_id": version_id,
                "cluster_id": cluster_id,
                "chart_config": {
                    "inputs": {}
                }
            }
        }

        response = self._post(uri=uri, json=data)
        return response

    def create_app_of_image(self, app_group_id, app_name, app_version, app_group_ns, resource_type, app_type_info,
                            cluster_type, deploy_type, cluster_id, version_id, container_spec, img_url, **kwargs):
        """
        创建容器镜像包应用

        :param app_group_id: 应用组ID
        :param app_name: 应用名称
        :param app_version: 应用版本号
        :param app_group_ns: 应用组命名空间
        :param app_type_info: 应用类型的信息
        :param deploy_type: 部署方式。传统方式部署/ 通过环境部署
        :param resource_type: 资源类型。当前缺省为容器集群
        :param cluster_type: 集群类型
        :param cluster_id: 集群ID
        :param version_id: 安装包版本ID
        :param container_spec: 容器规格
        :param img_url: 镜像包所在仓库地址
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}/apps"

        affinity = {
            "nodeAffinity": {
                "preferred": {
                    "in": kwargs['node_affinity']['preferred'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['preferred'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'preferred' in kwargs[
                        'node_affinity'].keys() else []
                },
                "required": {
                    "in": kwargs['node_affinity']['required'][
                        'in'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                    "notIn": kwargs['node_affinity']['required'][
                        'notIn'] if 'node_affinity' in kwargs.keys() and 'required' in kwargs[
                        'node_affinity'].keys() else [],
                }
            },
            "podAffinity": {
                "perferPodAffinityRules": kwargs['pod_affinity'][
                    'perferPodAffinityRules'] if 'pod_affinity' in kwargs.keys() else [],
                "requirePodAffinityRules": kwargs['pod_affinity'][
                    'requirePodAffinityRules'] if 'pod_affinity' in kwargs.keys() else []
            },
            "podAntiAffinity": {
                "perferPodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'perferPodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else [],
                "requirePodAntiAffinityRules": kwargs['pod_anti_affinity'][
                    'requirePodAntiAffinityRules'] if 'pod_anti_affinity' in kwargs.keys() else []
            }
        }

        pvc_resource = {
            "pv": kwargs['pvc_resource']['pv'] if 'pvc_resource' in kwargs.keys() else [],
            "pvc": kwargs['pvc_resource']['pvc'] if 'pvc_resource' in kwargs.keys() else []
        }

        resources = [
            {
                "security": {
                    "capabilities": kwargs['security']['capabilities'] if 'security' in kwargs.keys() else [],
                    "hostIPC": kwargs['security']['hostIPC'] if 'security' in kwargs.keys() else False,
                    "hostNetwork": kwargs['security']['hostNetwork'] if 'security' in kwargs.keys() else False,
                    "hostPID": kwargs['security']['hostPID'] if 'security' in kwargs.keys() else False,
                    "privileged": kwargs['security']['privileged'] if 'security' in kwargs.keys() else False,
                    "readOnlyRootFilesystem": kwargs['security'][
                        'readOnlyRootFilesystem'] if 'security' in kwargs.keys() else False,
                    "runAsUser": kwargs['security']['runAsUser'] if 'security' in kwargs.keys() else '',
                }
            },
            {
                "apiVersion": app_type_info['apiVersion'],
                "kind": app_type_info['kind'],
                "metadata": {
                    "labels": {
                        "app": app_name
                    },
                    "name": app_name,
                    "namespace": app_group_ns
                },
                "spec": {
                    "replicas": 1,
                    "selector": {
                        "matchLabels": {
                            "app": app_name
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": app_name
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "args": None,
                                    "command": None,
                                    "env": [],
                                    "image": img_url,
                                    "imagePullPolicy": "Always",
                                    "name": app_name,
                                    "ports": [],
                                    "resources": {
                                        "requests": {
                                            "cpu": container_spec['cpu_request'],
                                            "memory": container_spec['mem_request']
                                        },
                                        "limits": {
                                            "cpu": container_spec['cpu_limit'],
                                            "memory": container_spec['mem_limit']
                                        }
                                    },
                                    "securityContext": {
                                        "privileged": True
                                    },
                                    "volumeMounts": kwargs['volume_mounts'] if 'volume_mounts' in kwargs.keys() else []
                                }
                            ],
                            "dnsPolicy": kwargs['svc_access_contro'][
                                'dnsPolicy'] if 'svc_access_contro' in kwargs.keys() else 'ClusterFirst',
                            "initContainers": kwargs['init_containers'] if 'init_containers' in kwargs.keys() else [],
                            "restartPolicy": "Always",
                            "schedulerName": "default-scheduler",
                            "securityContext": {},
                            "serviceAccount": app_name,
                            "serviceAccountName": app_name,
                            "volumes": kwargs['volumes'] if 'volumes' in kwargs.keys() else []
                        }
                    }
                }
            }
        ]
        # 服务访问控制
        if 'svc_access_control_info' in kwargs.keys():
            ports = [
                {
                    "containerPort": kwargs['svc_access_control_info']['port'],
                    "protocol": "TCP"
                }
            ]
            resources[1]['spec']['template']['spec']['containers'][0]['ports'] = ports

            resources_svc_info = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": app_name,
                    "namespace": app_group_ns,
                    "labels": {
                        "app": app_name
                    }
                },
                "spec": {
                    "ports": [
                        {
                            "name": app_name,
                            "protocol": "TCP",
                            "targetPort": kwargs['svc_access_control_info']['targetPort'],
                            "port": kwargs['svc_access_control_info']['port'],
                            "nodePort": kwargs['svc_access_control_info']['nodePort']
                        }
                    ],
                    "selector": {
                        "app": app_name
                    },
                    "sessionAffinity": "None",
                    "type": "NodePort"
                }
            }
            resources.append(resources_svc_info)

        data = {
            "name": app_name,
            "version": app_version,
            "description": kwargs['app_description'] if 'app_description' in kwargs.keys() else '',
            "package_type": 'image',
            "resource_type": resource_type,
            "cluster_type": cluster_type,
            "workload_type": deploy_type,
            "appEntranceUrl": kwargs['app_entrance_url'] if 'app_entrance_url' in kwargs else '',
            "cluster_id": cluster_id,
            "metadata": {
                "version_id": version_id,
                "image_metadata": {
                    "metadata": {
                        "affinity": affinity,
                        "pvcResource": pvc_resource,
                        "resources": resources
                    },
                }
            }
        }

        if cluster_type == "mcpCluster":
            data['mcpPlaintextList'] = kwargs['mcp_plaintext_list']
            resources[1]['spec']['template']['spec']['initContainers'] = kwargs[
                'init_containers'] if 'init_containers' in kwargs.keys() else []

        response = self._post(uri=uri, json=data)
        return response

    def action_app_group(self, app_group_id, action, **kwargs):
        """
        操作应用组。当前为停止和启动

        :param app_group_id: 应用组ID
        :param action: stop/ start
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}?action={action}"
        if kwargs:
            uri += '&' + urlencode(kwargs)
        response = self._put(uri=uri)
        return response

    def action_app(self, app_id, action, **kwargs):
        """
        操作应用。当前为停止和启动

        :param app_id: 应用组ID
        :param action: stop/ start
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}?action={action}"
        if kwargs:
            uri += '&' + urlencode(kwargs)
        response = self._put(uri=uri)
        return response

    def scale_app(self, app_name, app_id, resources):
        """
        应用的弹性伸缩

        :param app_name: 应用名称
        :param app_id: 应用ID
        :param resources: 规格。包括启动和运行限制
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/resources"

        data = [{
            "name": app_name,
            "resources": {
                "limits": {
                    "cpu": resources['limits']['cpu'],
                    "memory": resources['limits']['memory']
                },
                "requests": {
                    "cpu": resources['requests']['cpu'],
                    "memory": resources['requests']['memory']
                }
            }
        }]

        header = self.ss.headers
        header["content-type"] = "application/json;charset=UTF-8"

        response = self._put(uri=uri, json=data, headers=header)
        return response

    def delete_app(self, app_id, delete_pvc="true", **kwargs):
        """
        删除应用

        :param app_id: 应用ID
        :param delete_pvc: 是否删除PVC
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}?deletePvc={delete_pvc}"
        if kwargs:
            uri += '&' + urlencode(kwargs)
        response = self._delete(uri=uri)
        return response

    def delete_app_patch(self, app_ids, delete_pvc="true"):
        """
        批量删除应用

        :param app_ids: 一组应用ID
        :param delete_pvc: 是否删除PVC
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps?deletePvc={delete_pvc}"
        data = {
            "ids": app_ids
        }
        response = self._delete(uri=uri, data=data)
        return response

    def upgrade_app_of_jar(self, app_id, version_id, app_version, app_detail):
        """
        升级jar包应用

        :param app_id: 应用ID
        :param version_id: 应用包版本号
        :param app_version: 应用目标版本号
        :param app_detail: 应用组详情
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/advanced-config"

        data = {
            "version_id": version_id,
            "version": app_version,
            "strategy": "rolling",
            "env": {},
            "jvm_args": app_detail['data']['metadata']['jvm_args'],
            "logrotateCron": None,
            "jdk_version": app_detail['data']['metadata']['jdk_version'],
            "is_skywalking": app_detail['data']['metadata']['is_skywalking'],
            "service_name": app_detail['data']['metadata']['image_metadata']['metadata']['resources'][2]['metadata'][
                'name'],
            "affinity": app_detail['data']['metadata']['image_metadata']['metadata']['affinity'],
            "pvcResource": app_detail['data']['metadata']['image_metadata']['metadata']['pvcResource'],
            "resources": app_detail['data']['metadata']['image_metadata']['metadata']['resources']
        }

        header = self.ss.headers
        header["content-type"] = "application/json;charset=UTF-8"

        response = self._patch(uri=uri, data=data, headers=header)
        return response

    def rollback_app_of_jar(self, app_id, version_id, version, app_detail):
        """
        回滚jar包应用

        :param app_id: 应用ID
        :param version_id: 应用包版本号
        :param version: 回滚版本号,
        :param app_detail: 应用组详情
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/rollback"

        data = {
            "logrotateCron": None,
            "strategy": "rolling",
            "version_id": version_id,
            "env": {},
            "jvm_args": app_detail['detail']['jvm_args'],
            "jdk_version": app_detail['detail']['jdk_version'],
            "is_skywalking": app_detail['detail']['is_skywalking'],
            "affinity": app_detail['detail']['image_metadata']['metadata']['affinity'],
            "pvcResource": app_detail['detail']['image_metadata']['metadata']['pvcResource'],
            "resources": app_detail['detail']['image_metadata']['metadata']['resources'],
            "version": version
        }

        header = self.ss.headers
        header["content-type"] = "application/json;charset=UTF-8"

        response = self._put(uri=uri, json=data, headers=header)
        return response

    def get_app_history_versions(self, app_id):
        """
        查询应用包历史版本

        :param app_id: 应用ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/history/versions"
        response = self._get(uri=uri)
        return response

    def get_cluster_storage_class(self, cluster_id, cluster_type, has_provisioner=True):
        """
        获取资源配置信息

        :param cluster_id: 集群ID
        :param cluster_type: 集群类型: 共享；独享
        :param has_provisioner:
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/cluster/{cluster_id}/storageclass/getAll?clusterType={cluster_type}&hasProvisioner={has_provisioner}"
        response = self._get(uri=uri)
        return response

    def get_apps_list(self, page=1, size=10, **kwargs):
        """
        获取应用列表并可完成排序，搜索，根据应用组ID查找应用列表的功能

        :param page: 页码
        :param size: 数量
        :param kwargs: 已知可携带的参数：appGroupId/ name/ updated_at=descending
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps?page={str(page)}&size={str(size)}"
        if kwargs:
            uri += "&" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_app_detail(self, app_id):
        """
        获取应用详情

        :param app_id: 应用ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}"
        response = self._get(uri=uri)
        return response

    def get_app_groups_list(self, name="", page=1, page_size=10, **kwargs):
        """
        获取应用组列表，可搜索

        :param page: 页码
        :param page_size: 数据量
        :param name: 应用组名称
        :param kwargs: 已知搜索条件有：projectId
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups?page={str(page)}&pageSize={str(page_size)}&name={name}"
        if kwargs:
            uri += "&" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def check_ns_name_of_app_group(self, name):
        """
        校验创建应用组时命名空间是否重名

        :param name: 名称
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroup/checkNs/{name}"
        response = self._get(uri=uri)
        return response

    def get_app_groups_config_parameters(self, **kwargs):
        """
        获取应用管理--应用组列表参数

        :return:
        """
        uri = "/api/cloud/app-mgmt/v1.0/apps/config/paramters"
        if kwargs:
            uri += "?" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_available_app_groups_list(self, filter_by_privilege="controller"):
        """
        获取创建应用时可选的应用组列表

        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups?filterByPrivilege={filter_by_privilege}"
        response = self._get(uri=uri)
        return response

    def get_clusters_list_by_type(self, cluster_type="kaasCluster"):
        """
        获取集群列表

        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/clusters?type={cluster_type}"
        response = self._get(uri=uri)
        return response

    def get_app_envs(self, page=1, size=9999999):
        """
        获取应用环境变量

        :param page: 页码
        :param size: 数据量
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appenvs?page={str(page)}&size={str(size)}"
        response = self._get(uri=uri)
        return response

    def get_app_group_api_by_cluster_id(self, cluster_id):
        """
        根据cluster id获取api

        :param cluster_id: 集群ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/cluster/{cluster_id}/api"
        response = self._get(uri=uri)
        return response

    def get_cluster_labels(self, cluster_id):
        """
        根据cluster查询标签

        :param cluster_id: 集群ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/cluster/{cluster_id}/labels"
        response = self._get(uri=uri)
        return response

    def get_cluster_configmap_list(self, cluster_id, cluster_type="kaasCluster", app_group_id=""):
        """
        根据cluster查询configmap列表

        :param cluster_id: 集群ID
        :param cluster_type: 集群类型
        :param app_group_id: 应用组ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/cluster/{cluster_id}/configmapList?clusterType={cluster_type}&appGroupId={app_group_id}"
        response = self._get(uri=uri)
        return response

    def get_cluster_secret_list(self, cluster_id, cluster_type="kaasCluster", app_group_id=""):
        """
        根据cluster查询configmap列表

        :param cluster_id: 集群ID
        :param cluster_type: 集群类型
        :param app_group_id: 应用组ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/cluster/{cluster_id}/secretList?clusterType={cluster_type}&appGroupId={app_group_id}"
        response = self._get(uri=uri)
        return response

    def check_app_name_of_app_group(self, app_group_id, app_name):
        """
        检验创建应用时应用重名校验

        :param app_group_id: 应用组ID
        :param app_name: 名称
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/appgroups/{app_group_id}/checkName/{app_name}"
        response = self._get(uri=uri)
        return response

    def check_ports_by_cluster_id(self, cluster_id, port, cluster_type="kaasCluster"):
        """
        根据集群ID校验集群外端口

        :param cluster_id: 集群ID
        :param cluster_type: 集群类型
        :param port: 集群外端口
        :return:
        """

        uri = f"/api/cloud/app-mgmt/v1.0/clusters/{cluster_id}/checkPortsByClusterId?port={str(port)}&clusterType={cluster_type}"

        response = self._get(uri=uri)
        return response

    def get_app_instances_list(self, app_id, duration=1800):
        """
        查询应用包实例列表

        :param app_id: 应用ID
        :param duration: 回溯时间
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/instances?duration={str(duration)}"
        response = self._get(uri=uri)
        return response

    def get_mcp_nodes_list(self, mcp_cluster_id):
        """
        根据mcp cluster id获取mcp集群

        :param mcp_cluster_id: 集群ID
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/mcpMemberClusters?mcpClusterId={mcp_cluster_id}"
        response = self._get(uri=uri)
        return response

    def check_svc_name(self, app_id, svc_name):
        """
        校验应用对外访问服务名

        :param app_id: 应用ID
        :param svc_name: 服务名
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/service/checkname?name={svc_name}"
        response = self._put(uri=uri)
        return response

    def check_port_status(self, app_id, port):
        """
        校验应用对外访问端口

        :param app_id: 应用ID
        :param port: 端口号
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/checkPortStatus?port={port}"
        response = self._get(uri=uri)
        return response

    def set_svc_control(self, app_id, svc_name, port_name, container_port, cluster_port, node_port, node_group_name):
        """
        设置访问方式

        :param app_id: 应用ID
        :param svc_name: 服务名称
        :param port_name: 端口名称
        :param container_port: 容器端口
        :param cluster_port: 集群内端口
        :param node_port: 集群外端口
        :param node_group_name: 边缘节点组名称
        :return:
        """
        uri = f"/api/cloud/app-mgmt/v1.0/apps/{app_id}/service"
        data = {
            "type": "NodePort",
            "service_name": svc_name,
            "port_map_list": [
                {
                    "name": port_name,
                    "protocol": "TCP",
                    "container_port": container_port,
                    "cluster_port": cluster_port,
                    "node_port": node_port
                }
            ],
            "session_keep": False,
            "session_timeout": 10800,
            "labels": {},
            "nodeGroupName": node_group_name
        }
        response = self._post(uri=uri, json=data)
        return response
