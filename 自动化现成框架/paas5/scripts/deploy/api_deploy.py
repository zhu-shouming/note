from requests_toolbelt import *
from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode

from resource.utils.common import *


class DeployAPI(RestAPIBase):
    def get_deploy_packages_list(self, pkg_type, visible=True, page=1, size=10, **kwargs):
        """
        获取应用仓库列表

        :param pkg_type: 应用包类型
        :param visible: 公有仓库（True）/ 私有仓库（False）
        :param page: 页码
        :param size: 数据量
        :param kwargs:
        :return:
        """
        uri = f"/api/cloud/deploy/v1.0/packages?visible={str(visible)}&pkgType={pkg_type}&page={str(page)}&size={str(size)}"

        if kwargs:
            uri += "&" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_packages_list(self, page=1, size=10, visible=True, **kwargs):
        """
        获取应用仓库列表

        :param page: 页码
        :param size: 数据量
        :param visible: 仓库类型。公有（True）/ 私有（False）
        :param kwargs: 如，label（应用包名称）
        :return:
        """
        uri = f"/api/cloud/deploy/v1.0/packages?page={str(page)}&size={str(size)}&visible={str(visible)}&updated_at_sort=descending"
        if kwargs:
            uri += "&" + urlencode(kwargs)
        response = self._get(uri=uri)
        return response

    def get_tags_list(self, tag_type="software"):
        """
        获取应用仓库分类列表

        :param tag_type:
        :return:
        """
        uri = f"/api/cloud/deploy/v1.0/tags?type={tag_type}"
        response = self._get(uri=uri)
        return response

    def check_tag_name(self, tag_name):
        """
        分类重名校验

        :param tag_name: 分类名称
        :return:
        """
        uri = "/api/cloud/deploy/v1.0/tags/checkName"

        data = {
            "name": tag_name
        }

        response = self._post(uri=uri, json=data)
        return response

    def create_tag(self, tag_name):
        """
        创建分类

        :param tag_name: 分类名称
        :return:
        """
        uri = "/api/cloud/deploy/v1.0/tags"

        response = self._post(uri=uri, data=tag_name)
        return response

    def delete_tag(self, tag_id):
        """
        删除分类

        :param tag_id: 分类ID
        :return:
        """
        uri = f"/api/cloud/deploy/v1.0/tags/{tag_id}"

        response = self._delete(uri=uri)
        return response

    def upload_package(self, name, version, tag_id, file_name, pkg_type, total_size, file_rb, visible=True, label="",
                       **kwargs):
        """
        创建应用组


        :param name: 应用包名称
        :param version: 应用包版本
        :param tag_id: 应用包分类
        :param file_name: 上传应用包的带后缀的包名。例如，xxx.zip
        :param pkg_type: 应用包类型。例如，war/ jar/ helm/ 前端包
        :param total_size: 文件大小
        :param file_rb: 文件的二进制内容
        :param visible: 仓库类型。缺省为“公有”
        :param label: 显示名称
        :param kwargs:
        :return:
        """

        uri = "/api/cloud/deploy/v1.0/packages"

        file_names_list = file_name.split(".")
        temp_file_name = ""
        for i in range(0, len(file_names_list)):
            temp_file_name += file_names_list[i]
        identifier = str(total_size) + "-" + temp_file_name

        data = {
            "chunkNumber": "1",
            "chunkSize": "204800000",
            "currentChunkSize": str(total_size),
            "totalSize": str(total_size),
            "identifier": identifier,
            "filename": file_name,
            "relativePath": file_name,
            "totalChunks": "1",
            "id": get_random_string(10, char_type=3),
            "name": name,
            "version": version,
            "label": label,
            "description": kwargs['description'] if "description" in kwargs.keys() else "",
            "feature": "",
            "visible": str(visible),
            "tagId": tag_id,
            "pkgType": pkg_type,
            "file": (file_name, file_rb, 'application/x-zip-compressed')
        }

        xx = MultipartEncoder(data)
        m = MultipartEncoderMonitor(xx)

        headers = {
            "Content-Type": xx.content_type,
            "Accept-Encoding": "gzip, deflate, br",
            "tagId": tag_id,
            "version": version
        }

        response = self._post(uri=uri, data=m, headers=headers)
        return response

    def download_package(self, version_id):
        """
        下载应用包

        :param version_id: 应用包版本
        :return:
        """
        uri = f"/api/cloud/deploy/v1.0/package-files/{version_id}"

        response = self._get(uri=uri)
        return response

    def delete_package(self, package_id, version_id):
        """
        删除应用包

        :param package_id: 应用包ID
        :param version_id: 应用包版本ID
        :return:
        """
        uri = f"/api/cloud/deploy/v1.0/packages/{package_id}?versionIds={version_id}"
        response = self._delete(uri=uri)
        print(uri)
        return response

    def publish_package(self, package_id, version_id, apply=False):
        """
        发布安装包到公有仓库。

        :param package_id: 应用包ID
        :param version_id: 应用包版本
        :param apply: 部署标志。缺省为False。为True时表示发布应用包到公有仓库
        :return:
        """

        uri = f"/api/cloud/deploy/v1.0/packages/{package_id}/publish?versionIds={version_id}&apply={str(apply)}"

        data = [version_id]

        response = self._put(uri=uri, json=data)
        return response

    def apply_for_publishing_package(self, package_id, version_id, apply=True):
        """
        申请发布应用包到公有仓库

        :param package_id: 应用包ID
        :param version_id: 应用包版本
        :param apply: 为True时表示项目管理员或普通用户申请发布应用包到公有仓库
        :return:
        """

        uri = f"/api/cloud/deploy/v1.0/packages/{package_id}/publish/bpm?versionIds={version_id}&apply={str(apply)}"

        data = [version_id]

        response = self._put(uri=uri, json=data)
        return response
