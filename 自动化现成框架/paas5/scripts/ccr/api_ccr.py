from asyncio.log import logger
from resource.base.rest_api_base import RestAPIBase
from urllib.parse import urlencode
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from resource.utils.common import get_random_string


class CCRAPI(RestAPIBase):
    def get_image_orgs(self, page=1, size=10, name=''):
        """镜像仓库--私有仓库--项目"""
        uri = f"/api/cloud/hcr/v1.0/projects?page={page}&size={size}&name={name}"
        return self._get(uri)

    def get_imgs_by_imgProject(self, img_project, page=1, size=20, img_name=None):
        """查询指定镜像组织的所有镜像
        eg: imgAlias=war 查询指定镜像"""
        uri = f"/api/cloud/hcr/v1.0/images/versions?harborProjectName={img_project}&page={page}&size={size}&type=private"
        if img_name:
            uri = uri + f'&imgAlias={img_name}'
        return self._get(uri)

    def get_public_images(self, page=1, size=20, img_name=None):

        uri = f"/api/cloud/hcr/v1.0/images/versions?type=public&page={page}&size={size}"
        if img_name:
            uri = uri + f'&imgAlias={img_name}'
        return self._get(uri)

    def get_image_type(self, name=''):
        """查看镜像类型"""
        uri = f"/api/cloud/hcr/v1.0/types?name={name}"
        return self._get(uri)

    def get_public_img_detail_info(self, name, org_id):
        """查看公有镜像详情"""
        uri = f"/api/cloud/hcr/v1.0/image/versions?name={name}&type=public&tentantId={org_id}&harborProjectName=library"
        return self._get(uri)

    def get_private_img_detail_info(self, name, tentantid, img_org_name):
        uri = f"/api/cloud/hcr/v1.0/image/versions?name={name}&type=private&tentantId={tentantid}&imgType=&harborProjectName={img_org_name}"
        return self._get(uri)

    def get_access_token(self, page=1, size=10, username=''):
        """获取访问凭证列表
           可以指定name= 参数 查询特定用户的访问凭证
        Returns:
            _type_: _description_
        """
        uri = f"/api/cloud/hcr/v1.0/harbor/users?page={page}&size={size}&username={username}"
        return self._get(uri)

    def reset_accessToken_passwd(self, harboId, uuid, passwd):
        uri = f'/api/cloud/hcr/v1.0/harbor/users/password/{harboId}/{uuid}'
        data = {"newPassword": passwd, "confirmPassword": passwd}
        return self._put(uri, data)

    def create_image_org(self, name):
        """新建镜像组织"""
        uri = "/api/cloud/hcr/v1.0/harbor/projects"
        data = {"projectName": name}
        return self._post(uri, data)

    def create_image_type(self, name):
        uri = "/api/cloud/hcr/v1.0/types"
        data = {"name": name}
        return self._post(uri, data)

    def create_access_token(self, name, full_name, mail, passwd, comment=""):
        uri = "/api/cloud/hcr/v1.0/harbor/addHarborUser"
        data = {
            "userName": name,
            "realName": full_name,
            "email": mail,
            "comment": comment,
            "password": passwd,
            "confirmPassword": passwd,
        }
        return self._post(uri, data)

    def upload_public_image(self, img_name, img_type, img_version, user_id, data):
        uri = "/api/cloud/hcr/v1.0/images/load"
        encoder = MultipartEncoder(fields=data)
        m = MultipartEncoderMonitor(encoder)
        header = {"projectName": ""}
        header["Content-Type"] = encoder.content_type
        header["imgName"] = img_name
        header["imgType"] = img_type
        header["type"] = "public"
        header["version"] = img_version
        header["userUuid"] = user_id
        header["fileFlag"] = "ui9W7e2Ib9"
        header["Accept"] = "*/*"
        header["Accept-encoding"] = "gzip, deflate, br"

        return self._post(uri, data=m, headers=header)

    def upload_private_image(
        self, img_project_name, img_name, version, user_id, data, img_type_id
    ):
        encoder = MultipartEncoder(fields=data)
        uri = "/api/cloud/hcr/v1.0/images/load"
        header = {
            "projectName": img_project_name,
            "Content-Type": encoder.content_type,
            "Content-Length": str(encoder.len),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "imgName": img_name,
            'imgType': img_type_id,
            "type": "private",
            "version": version,
            "userUuid": user_id,
            "fileFlag": get_random_string(10, char_type=3),
        }
        logger.info(encoder.len)
        return self._post(uri, data=encoder, headers=header)

    def delete_public_image(self, data):
        uri = "/api/cloud/hcr/v1.0/images/versions"
        return self._post(uri, json=data)

    def delete_private_image(self, data):
        uri = '/api/cloud/hcr/v1.0/images/versions'
        return self._post(uri, json=data)

    def delete_access_token(self, uuid, harborId):
        uri = f"/api/cloud/hcr/v1.0/harbor/users/{uuid}/{harborId}"
        return self._delete(uri)

    def delete_image_org(self, org_id):
        uri = f"/api/cloud/hcr/v1.0/projects/{org_id}"
        return self._delete(uri)

    def delete_image_type(self, type_id):
        uri = f"/api/cloud/hcr/v1.0/types/{type_id}"
        return self._delete(uri)

    def check_img_org_name(self, name):
        uri = f"/api/cloud/hcr/v1.0/harbor/projects/check/{name}"
        return self._get(uri)

    def public_private_image(self, img_name, img_url, img_group_id, img_type_id):
        uri = "/api/cloud/hcr/v1.0/images/public?apply=True"
        data = {
            "imgName": img_name,
            "imgGroupId": img_group_id,
            "imgAlias": img_name,
            "imageIds": "",
            "imgLogo": "",
            "description": "",
            "type": "private",
            "imgType": img_type_id,
            "outImageUrls": img_url,
        }
        return self._post(uri, data)

    def build_image(
        self,
        dockerfile: str,
        name,
        img_type_id,
        img_project_name,
        project_name,
        project_id,
        img_class,
        version,
        description,
    ):
        fileflag = get_random_string(10)
        data = {
            "dockerfile": dockerfile,
            "imgName": name,
            "version": version,
            "imgType": img_type_id,
            "description": description,
            "type": img_class,
            "fileFlag": fileflag,
            "project": img_project_name,
            "tentantID": project_id,
            "tentantName": project_name,
        }
        uri = '/api/cloud/hcr/v1.0/images/build'
        return self._post(uri, data)

    def del_published_image(self):
        pass
