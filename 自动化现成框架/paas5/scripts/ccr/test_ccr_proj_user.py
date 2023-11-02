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


@pytest.mark.ccr
@allure.feature("镜像仓库")
@allure.story("镜像仓库")
class TestCCR:
    def setup_class(self):
        user = PAASClient(
            PAASLogin(
                settings['PROJ_ADMIN'],
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
    @allure.title("普通用户查询公有镜像列表")
    def test_get_public_imgs(self, paas_proj_user_login: PAASClient):
        res = paas_proj_user_login.ccr_client.get_public_images()
        check_status_code(res, 200)
        data = res.json()
        assert data["status"] == True
        assert data["msg"] == "ok"

    @pytest.mark.L5
    @allure.title("普通用户查询镜像组织")
    def test_get_img_orgs(self, paas_proj_user_login: PAASClient):
        res = paas_proj_user_login.ccr_client.get_image_orgs()
        check_status_code(res, 200)

    @pytest.mark.L5
    @allure.title("普通用户查询特定镜像组织的所有镜像")
    def test_get_org_imgs(self, paas_proj_user_login: PAASClient):
        with allure.step("从列表中选择一个镜像组织"):
            list_res = paas_proj_user_login.ccr_client.get_image_orgs()
            check_status_code(list_res, 200)

            chose_org = get_value_from_json(list_res, "$.data.data[0].name")
        res = paas_proj_user_login.ccr_client.get_imgs_by_imgProject(chose_org)
        check_status_code(res, 200)
        status = get_value_from_json(res, "$.status")
        msg = get_value_from_json(res, "$.msg")
        assert status == True
        assert msg == "ok"

    @pytest.mark.L5
    @pytest.mark.parametrize("args", data['upload_private_img'])
    def test_upload_private_img(self, paas_proj_user_login: PAASClient, args):
        allure.dynamic.title("普通用户" + args['title'])
        private_img = settings['cce_image']
        description = args["description"]
        version = args["version"]
        user_id = paas_proj_user_login.login_info.user_id
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
        r = paas_proj_user_login.ccr_client.upload_private_image(
            self.imgProject_name, img_name, version, user_id, data, self.img_type_id
        )
        check_status_code(r, 200)

        cnt = 0
        while cnt < 6:
            sleep(10)
            check_r = paas_proj_user_login.ccr_client.get_imgs_by_imgProject(
                self.imgProject_name, img_name=img_name
            )
            if get_value_from_json(check_r, f"$..total") == 1:
                break
            else:
                cnt = cnt + 1
        assert cnt < 6, f"上传镜像失败， 列表中找不到上传的镜像{img_name}"
        sleep(3)
        del_private_image_version(paas_proj_user_login, self.imgProject_name, img_name)

    @pytest.mark.L5
    @allure.title("普通用户删除私有镜像")
    @pytest.mark.parametrize('args', data['upload_private_img'])
    def test_del_private_img(self, paas_proj_user_login: PAASClient, args):
        with allure.step("上传一个私有镜像"):
            img_name = 'auto' + get_random_string(4).lower()
            user_id = paas_proj_user_login.login_info.user_id
            tentantid = paas_proj_user_login.login_info.default_project_id
            file_path =settings['cce_image']
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
            resp = paas_proj_user_login.ccr_client.upload_private_image(
                self.imgProject_name, img_name, "v1", user_id, data, self.img_type_id
            )
            check_status_code(resp, 200)
            cnt = 0
            while cnt < 6:
                sleep(10)
                check_r = paas_proj_user_login.ccr_client.get_imgs_by_imgProject(
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
        img_r = paas_proj_user_login.ccr_client.get_imgs_by_imgProject(
            self.imgProject_name, img_name=img_name
        )
        check_status_code(img_r, 200)
        img_id = get_value_from_json(
            img_r, f"$.data.data[?(@.imageName=='{img_name}')].uuid"
        )
        assert img_id, "获取镜像id失败"
        r = paas_proj_user_login.ccr_client.get_private_img_detail_info(
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
                    "userID": paas_proj_user_login.login_info.user_id,
                }
            ],
            "tagCount": 1,
            "imgType": img_type,
            "projectName": self.imgProject_name,
            "imageName": img_name,
            "imageGroupId": img_id,
        }
        r_del = paas_proj_user_login.ccr_client.delete_private_image(data)
        check_status_code(r_del, 200)
        cnt = 0
        while cnt < 5:
            sleep(6)
            r = paas_proj_user_login.ccr_client.get_imgs_by_imgProject(
                self.imgProject_name, img_name=img_name
            )
            if get_value_from_json(r, "$..total") == 0:
                break
            else:
                cnt = cnt + 1
        assert cnt < 5, f"删除镜像{img_name}失败"

    @pytest.mark.L5
    @allure.title("普通用户申请发布私有镜像到公有仓库")
    @pytest.mark.parametrize('args', data['upload_private_img'])
    def test_public_private_img(
        self, paas_admin_login: PAASClient, paas_proj_user_login: PAASClient, args
    ):
        with allure.step("新建私有镜像"):
            private_img = settings['cce_image']
            description = args["description"]
            version = args["version"]
            user_id = paas_proj_user_login.login_info.user_id
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
                "file": (file_name, file_data, "application/x-tar"),
            }
            img_name = "auto" + get_random_string(4).lower()
            r = paas_proj_user_login.ccr_client.upload_private_image(
                self.imgProject_name, img_name, version, user_id, data, self.img_type_id
            )
            check_status_code(r, 200)

            cnt = 0
            while cnt < 6:
                sleep(10)
                check_r = paas_proj_user_login.ccr_client.get_imgs_by_imgProject(
                    self.imgProject_name, img_name=img_name
                )
                img_info = get_value_from_json(
                    check_r, f"$.data.data[?(@.imageName=='{img_name}')]"
                )
                if img_info:
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 6, f"上传镜像失败， 列表中找不到上传的镜像{img_name}"
            img_id = img_info['uuid']
            tentantId = paas_proj_user_login.login_info.default_project_id
            r = paas_proj_user_login.ccr_client.get_private_img_detail_info(
                img_name, tentantId, self.imgProject_name
            )
            check_status_code(r, 200)
            img_url = get_value_from_json(r, "$.data.images..imgUrl")
        with allure.step("申请发布镜像到公有仓库"):
            resp = paas_proj_user_login.ccr_client.public_private_image(
                img_name, img_url, self.img_pro_id, self.img_type_id
            )
            check_status_code(resp, 200)
        with allure.step("审批流程"):
            time.sleep(5)
            admin_id = paas_admin_login.login_info.user_id
            r = paas_admin_login.sys_client.get_processes(
                status="PROCESSING", nameLike=img_name, nextCandidateUser=admin_id
            )
            process_id = get_value_from_json(r, "$.data[0].id")
            assert process_id, "获取发布镜像的审批流程失败"
            public_r = paas_admin_login.sys_client.deal_with_process(process_id, True)
            check_status_code(public_r, 200)
            sleep(5)
            cnt = 0
            while cnt < 5:
                sleep(10)
                check = paas_proj_user_login.ccr_client.get_public_images(
                    img_name=img_name
                )
                if get_value_from_json(check, "$..total") == 1:
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, f"发布镜像{img_name}到公有仓库失败"
        sleep(2)
        del_private_image_version(paas_proj_user_login, self.imgProject_name, img_name)
        del_public_img(paas_admin_login, img_name)
