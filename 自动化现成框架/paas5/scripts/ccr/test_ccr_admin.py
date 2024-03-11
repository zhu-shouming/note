from time import sleep
import pytest, allure, yaml, os, platform
from resource.base.client import PAASClient
from resource.base.login import PAASLogin
from resource.utils.common import *
from scripts.ccr.handler_ccr import *
from config.config import settings


cur_path = os.path.dirname(os.path.realpath(__file__))
if platform.system() == "Windows":
    dataPath = os.path.join(cur_path, 'data_win.yaml')
else:
    dataPath = os.path.join(cur_path, 'data_linux.yaml')
with open(dataPath, encoding="utf-8") as f:
    data = yaml.safe_load(f)


@pytest.mark.Smoke
@pytest.mark.ccr
@allure.feature("镜像仓库")
@allure.story("镜像仓库")
class TestCCR:
    def setup_class(self):
        user = PAASClient(
            PAASLogin(
                settings['USERNAME'],
                settings['PASSWORD'],
                settings['HOST'],
                settings['PORT'],
            )
        )
        name = "auto" + get_random_string(5).lower()
        res = user.ccr_client.create_image_org(name)
        check_status_code(res, 200)
        check = user.ccr_client.get_image_orgs(page=1, size=10, name=name)
        check_status_code(check, 200)
        status = get_value_from_json(check, "$.status")
        num = get_value_from_json(check, "$..total")
        assert status == True
        assert num == 1
        self.img_pro_id = get_value_from_json(check, "$..project_id")
        self.imgProject_name = name
        self.client = user
        img_type_name = 'auto' + get_random_string(4).lower()
        r = self.client.ccr_client.create_image_type(img_type_name)
        check_status_code(r)
        sleep(2)
        check = self.client.ccr_client.get_image_type(img_type_name)
        check_status_code(check)
        self.img_type_id = get_value_from_json(check, f"$..uuid")
        assert self.img_type_id, "新建镜像类型失败"

    def teardown_class(self):
        self.client.ccr_client.delete_image_org(self.img_pro_id)
        self.client.ccr_client.delete_image_type(self.img_type_id)

    @pytest.mark.L5
    @allure.title("上传公有镜像")
    @pytest.mark.parametrize("args", data["upload_public_img"])
    def test_upload_public_img(self, paas_admin_login: PAASClient, args):
        public_img = settings['cce_image']
        description = args["description"]
        version = args["version"]
        user_id = paas_admin_login.login_info.user_id
        resp = paas_admin_login.ccr_client.get_image_type('Default')
        check_status_code(resp)
        img_type_id = get_value_from_json(resp, "$..uuid")
        assert img_type_id, "查询镜像分类失败"
        file_size = str(os.path.getsize(public_img))
        file_name = os.path.basename(public_img)
        with open(public_img, "rb") as f:
            file_data = f.read()
        data = {
            "chunkNumber": "1",
            "chunkSize": "204800000",
            "currentChunkSize": file_size,
            "totalSize": file_size,
            "identifier": str(file_size) + '-' + file_name.replace('.', ''),
            "filename": file_name,
            "relativePath": file_name,
            "totalChunks": "1",
            "description": description,
            "featureInfo": "",
            "file": (file_name, file_data, "application/x-tar"),
        }
        name = 'auto' + get_random_string(4).lower()

        res = paas_admin_login.ccr_client.upload_public_image(
            name, img_type_id, version, user_id, data
        )
        check_status_code(res, 200)
        cnt = 0
        while cnt < 15:
            sleep(10)
            r = paas_admin_login.ccr_client.get_public_images(img_name=name)
            if get_value_from_json(r, "$..total") == 1:
                break
            else:
                cnt = cnt + 1
        assert cnt < 10, "超时：上传公有镜像失败"
        time.sleep(3)
        del_public_img(paas_admin_login, name)

    @pytest.mark.L5
    @allure.title("查询公有镜像列表")
    def test_get_public_imgs(self, paas_admin_login: PAASClient):
        res = paas_admin_login.ccr_client.get_public_images()
        check_status_code(res, 200)
        data = res.json()
        assert data["status"] == True
        assert data["msg"] == "ok"

    @pytest.mark.L5
    @allure.title("查询镜像组织")
    def test_get_img_orgs(self, paas_admin_login: PAASClient):
        res = paas_admin_login.ccr_client.get_image_orgs()
        check_status_code(res, 200)

    @pytest.mark.L5
    @allure.title("查询特定镜像组织的所有镜像")
    def test_get_org_imgs(self, paas_admin_login: PAASClient):
        with allure.step("从列表中选择一个镜像组织"):
            list_res = paas_admin_login.ccr_client.get_image_orgs()
            check_status_code(list_res, 200)

            chose_org = get_value_from_json(list_res, "$.data.data[0].name")
        res = paas_admin_login.ccr_client.get_imgs_by_imgProject(chose_org)
        check_status_code(res, 200)
        status = get_value_from_json(res, "$.status")
        msg = get_value_from_json(res, "$.msg")
        assert status == True
        assert msg == "ok"

    @pytest.mark.L5
    @allure.title("新建镜像组织")
    def test_creat_img_org(self, paas_admin_login: PAASClient):
        with allure.step("新建镜像组织"):
            name = "auto" + get_random_string(4).lower()
            resp = paas_admin_login.ccr_client.create_image_org(name)
            check_status_code(resp, 200)
            data = resp.json()
            assert data["status"] == True, f"请求响应消息不符合预期"
            assert data["msg"] == "ok", f"请求响应消息不符合预期"
        r = paas_admin_login.ccr_client.get_image_orgs()
        check_status_code(r, 200)
        img_org_id = get_value_from_json(
            r, f"$.data.data[?(@.name=='{name}')].project_id"
        )
        sleep(4)
        paas_admin_login.ccr_client.delete_image_org(img_org_id)

    @pytest.mark.L5
    @allure.title("删除镜像组织")
    def test_del_img_org(self, paas_admin_login: PAASClient):
        name = "auto" + get_random_string(5).lower()
        check_name = paas_admin_login.ccr_client.check_img_org_name(name)
        check_status_code(check_name, 200)
        msg = get_value_from_json(check_name, "$..msg")
        assert msg == "ok"
        res = paas_admin_login.ccr_client.create_image_org(name)
        check_status_code(res, 200)
        sleep(5)
        check = paas_admin_login.ccr_client.get_image_orgs(name=name)
        check_status_code(check, 200)
        status = get_value_from_json(check, "$.status")
        num = get_value_from_json(check, "$..total")
        assert status == True
        assert num == 1
        img_org_id = get_value_from_json(check, "$..project_id")
        del_resp = paas_admin_login.ccr_client.delete_image_org(img_org_id)
        check_status_code(del_resp, 200)

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data["creat_access_token"])
    def test_create_access_token(self, paas_admin_login: PAASClient, args):
        allure.dynamic.title(args["title"])
        name = "auto" + get_random_string(4).lower()
        res = paas_admin_login.ccr_client.create_access_token(
            name, args["fullname"], args["mail"], args["passwd"], args["comment"]
        )
        check_status_code(res, 200)
        status = get_value_from_json(res, "$..status")
        httpcode = get_value_from_json(res, "$..httpCode")
        assert status == True
        assert httpcode == 200
        time.sleep(3)
        res = paas_admin_login.ccr_client.get_access_token(username=name)
        uuid = get_value_from_json(res, "$..uuid")
        harborId = get_value_from_json(res, "$..harborId")
        paas_admin_login.ccr_client.delete_access_token(uuid, harborId)

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data["creat_access_token"])
    @allure.title("删除用户访问凭证")
    def test_delete_access_token(self, paas_admin_login: PAASClient, args):
        name = "auto" + get_random_string(4).lower()
        res = paas_admin_login.ccr_client.create_access_token(
            name, args["fullname"], args["mail"], args["passwd"], args["comment"]
        )
        check_status_code(res, 200)
        status = get_value_from_json(res, "$..status")
        httpcode = get_value_from_json(res, "$..httpCode")
        assert status == True
        assert httpcode == 200
        res = paas_admin_login.ccr_client.get_access_token(username=name)
        uuid = get_value_from_json(res, "$..uuid")
        harborId = get_value_from_json(res, "$..harborId")
        del_res = paas_admin_login.ccr_client.delete_access_token(uuid, harborId)
        check_status_code(del_res, 200)
        del_check = paas_admin_login.ccr_client.get_access_token(username=name)
        assert get_value_from_json(del_check, "$..httpCode") == 200
        assert get_value_from_json(del_check, "$..total") == 0, "删除访问凭证失败"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['reset_passwd'])
    def test_reset_accessToken_passwd(self, paas_admin_login: PAASClient, args):
        allure.dynamic.title(args['title'])
        with allure.step("新建用户访问凭证"):
            name = "auto" + get_random_string(4).lower()
            res = paas_admin_login.ccr_client.create_access_token(
                name, args["fullname"], args["mail"], args["passwd"], args["comment"]
            )
            check_status_code(res, 200)
            status = get_value_from_json(res, "$..status")
            httpcode = get_value_from_json(res, "$..httpCode")
            assert status == True
            assert httpcode == 200
            res = paas_admin_login.ccr_client.get_access_token(username=name)
            uuid = get_value_from_json(res, "$..uuid")
            harborId = get_value_from_json(res, "$..harborId")
        with allure.step("重置密码"):
            res = paas_admin_login.ccr_client.reset_accessToken_passwd(
                harborId, uuid, args['NewPasswd']
            )
            check_status_code(res, 200)
            assert get_value_from_json(res, "$..msg") == "ok"
        sleep(2)
        paas_admin_login.ccr_client.delete_access_token(uuid, harborId)

    @pytest.mark.L5
    @allure.title("删除公有镜像")
    @pytest.mark.parametrize("args", data["upload_public_img"])
    def test_del_public_img(self, paas_admin_login: PAASClient, args):
        public_img = settings['cce_image']
        description = args["description"]
        version = args["version"]
        user_id = paas_admin_login.login_info.user_id
        resp = paas_admin_login.ccr_client.get_image_type('Default')
        check_status_code(resp)
        img_type_id = get_value_from_json(resp, "$..uuid")
        file_size = str(os.path.getsize(public_img))
        file_name = os.path.basename(public_img)
        with open(public_img, "rb") as f:
            file_data = f.read()
        data = {
            "chunkNumber": "1",
            "chunkSize": "204800000",
            "currentChunkSize": file_size,
            "totalSize": file_size,
            "identifier": str(file_size) + '-' + file_name.replace('.', ''),
            "filename": file_name,
            "relativePath": file_name,
            "totalChunks": "1",
            "description": description,
            "featureInfo": "",
            "file": (file_name, file_data, "application/x-tar"),
        }
        name = 'auto' + get_random_string(4).lower()
        res = paas_admin_login.ccr_client.upload_public_image(
            name, img_type_id, version, user_id, data
        )
        check_status_code(res, 200)
        sleep(10)
        res = paas_admin_login.ccr_client.get_public_images(img_name=name)
        check_status_code(res, 200)
        img_group_id = get_value_from_json(
            res, f"$.data.data[?(@.imageName=='{name}')].uuid"
        )
        assert img_group_id
        res_detail = paas_admin_login.ccr_client.get_public_img_detail_info(
            name, img_group_id
        )
        check_status_code(res_detail, 200)
        img_id = get_value_from_json(res_detail, f"$.data.images..uuid")
        img_url = get_value_from_json(res_detail, f"$.data.images..imgUrl")
        img_type = get_value_from_json(res_detail, "$..imgType")
        assert img_id
        assert img_url
        data = {
            "images": [
                {
                    "id": img_id,
                    "imgUrl": img_url,
                }
            ],
            "tagCount": 1,
            "imgType": img_type,
            "projectName": "library",
            "imageName": name,
            "imageGroupId": img_group_id,
        }
        res_del = paas_admin_login.ccr_client.delete_public_image(data)
        check_status_code(res_del, 200)
        time.sleep(4)
        check = paas_admin_login.ccr_client.get_public_images(img_name=name)
        assert get_value_from_json(check, "$..total") == 0, "删除公有镜像失败"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['upload_private_img'])
    def test_upload_private_img(self, paas_admin_login: PAASClient, args):
        allure.dynamic.title("admin" + args['title'])
        private_img = settings['cce_image']
        description = args["description"]
        version = args["version"]
        user_id = paas_admin_login.login_info.user_id
        tentantid = paas_admin_login.login_info.default_project_id
        file_size = str(os.path.getsize(private_img))
        file_name = os.path.basename(private_img)
        with open(private_img, "rb") as f:
            file_data = f.read()
        data = {
            "chunkNumber": "1",
            "chunkSize": "204800000",
            "currentChunkSize": file_size,
            "totalSize": file_size,
            "identifier": str(file_size) + '-' + file_name.replace('.', ''),
            "filename": file_name,
            "relativePath": file_name,
            "totalChunks": "1",
            "description": description,
            "featureInfo": "",
            "file": (file_name, file_data, "application/octet-stream"),
        }
        img_name = "auto" + get_random_string(4).lower()
        r = paas_admin_login.ccr_client.upload_private_image(
            self.imgProject_name, img_name, version, user_id, data, self.img_type_id
        )
        check_status_code(r, 200)

        cnt = 0
        while cnt < 6:
            sleep(10)
            check_r = paas_admin_login.ccr_client.get_imgs_by_imgProject(
                self.imgProject_name, img_name=img_name
            )
            if get_value_from_json(check_r, f"$..total") == 1:
                break
            else:
                cnt = cnt + 1
        assert cnt < 6, f"上传镜像失败， 列表中找不到上传的镜像{img_name}"
        sleep(3)
        img_r = paas_admin_login.ccr_client.get_imgs_by_imgProject(
            self.imgProject_name, img_name=img_name
        )
        check_status_code(img_r, 200)
        img_id = get_value_from_json(
            img_r, f"$.data.data[?(@.imageName=='{img_name}')].uuid"
        )
        assert img_id, "获取镜像id失败"
        r = paas_admin_login.ccr_client.get_private_img_detail_info(
            img_name, tentantid, self.imgProject_name
        )
        check_status_code(r, 200)
        img_url = get_value_from_json(r, "$.data.images..imgUrl")
        img_uuid = get_value_from_json(r, "$.data.images..uuid")
        img_type = get_value_from_json(r, "$.data.images..imgType")
        data = {
            "images": [
                {
                    "id": img_uuid,
                    "imgUrl": img_url,
                    "tentantID": tentantid,
                    "userID": paas_admin_login.login_info.user_id,
                }
            ],
            "tagCount": 1,
            "imgType": img_type,
            "projectName": self.imgProject_name,
            "imageName": img_name,
            "imageGroupId": img_id,
        }
        r_del = paas_admin_login.ccr_client.delete_private_image(data)
        check_status_code(r_del, 200)
        cnt = 0
        while cnt < 5:
            sleep(6)
            r = paas_admin_login.ccr_client.get_imgs_by_imgProject(
                self.imgProject_name, img_name=img_name
            )
            if get_value_from_json(r, "$..total") == 0:
                break
            else:
                cnt = cnt + 1
        assert cnt < 5, f"删除镜像{img_name}失败"

    @pytest.mark.L5
    @allure.title("admin删除私有镜像")
    @pytest.mark.parametrize('args', data['upload_private_img'])
    def test_del_private_img(self, paas_admin_login: PAASClient, args):
        with allure.step("上传一个私有镜像"):
            img_name = 'auto' + get_random_string(4).lower()
            user_id = paas_admin_login.login_info.user_id
            tentantid = paas_admin_login.login_info.default_project_id
            file_path=settings['cce_image']
            file_size = str(os.path.getsize(file_path))
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                file_data = f.read()
            data = {
                "chunkNumber": "1",
                "chunkSize": "204800000",
                "currentChunkSize": file_size,
                "totalSize": file_size,
                "identifier": str(file_size) + '-' + file_name.replace('.', ''),
                "filename": file_name,
                "relativePath": file_name,
                "totalChunks": "1",
                "description": "",
                "featureInfo": "",
                "file": (file_name, file_data, "application/x-tar"),
            }
            img_name = get_random_string(5).lower()
            resp = paas_admin_login.ccr_client.upload_private_image(
                self.imgProject_name, img_name, "v1", user_id, data, self.img_type_id
            )
            check_status_code(resp, 200)
            cnt = 0
            while cnt < 6:
                sleep(10)
                check_r = paas_admin_login.ccr_client.get_imgs_by_imgProject(
                    self.imgProject_name
                )
                if get_value_from_json(
                    check_r, f"$.data.data[?(@.imageName=='{img_name}')]"
                ):
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 6, f"上传镜像失败， 列表中找不到上传的镜像{img_name}"
        sleep(10)
        img_r = paas_admin_login.ccr_client.get_imgs_by_imgProject(
            self.imgProject_name, img_name=img_name
        )
        check_status_code(img_r, 200)
        img_id = get_value_from_json(
            img_r, f"$.data.data[?(@.imageName=='{img_name}')].uuid"
        )
        assert img_id, "获取镜像id失败"
        r = paas_admin_login.ccr_client.get_private_img_detail_info(
            img_name, tentantid, self.imgProject_name
        )
        check_status_code(r, 200)
        img_url = get_value_from_json(r, "$.data.images..imgUrl")
        img_type = get_value_from_json(r, "$.data.images..imgType")
        data = {
            "images": [
                {
                    "id": "",
                    "imgUrl": img_url,
                    "tentantID": tentantid,
                    "userID": paas_admin_login.login_info.user_id,
                }
            ],
            "tagCount": 1,
            "imgType": img_type,
            "projectName": self.imgProject_name,
            "imageName": img_name,
            "imageGroupId": img_id,
        }
        r_del = paas_admin_login.ccr_client.delete_private_image(data)
        check_status_code(r_del, 200)
        cnt = 0
        while cnt < 5:
            sleep(6)
            r = paas_admin_login.ccr_client.get_imgs_by_imgProject(
                self.imgProject_name, img_name=img_name
            )
            if get_value_from_json(r, "$..total") == 0:
                break
            else:
                cnt = cnt + 1
        assert cnt < 5, f"删除镜像{img_name}失败"
