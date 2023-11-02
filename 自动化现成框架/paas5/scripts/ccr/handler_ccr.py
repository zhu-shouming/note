import os

from resource.base.client import PAASClient
from resource.utils.common import *
from scripts.sys.handler_sys import *


def get_img_info_by_name(user: PAASClient, name):
    org_id = user.login_info.default_project_id
    all_info = user.ccr_client.get_public_img_detail_info(name, org_id)
    check_status_code(all_info, 200)

    status = get_value_from_json(all_info, "$.status")
    httpCode = get_value_from_json(all_info, "$.httpCode")
    data = get_value_from_json(all_info, "$.data")
    assert status == True
    assert httpCode == 200
    return data


def upload_public_img(
    user: PAASClient, img_path, img_name, img_version, img_type='Default'
):
    user_id = user.login_info.user_id
    file_size = str(os.path.getsize(img_path))
    file_name = os.path.basename(img_path)
    with open(img_path, "rb") as f:
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
        "file": (file_name, file_data, "application/octet-stream"),
    }
    resp = user.ccr_client.get_image_type(img_type)
    check_status_code(resp)
    img_type_id = get_value_from_json(resp, "$..uuid")
    res = user.ccr_client.upload_public_image(
        img_name, img_type_id, img_version, user_id, data
    )
    check_status_code(res, 200)
    cnt = 0
    while cnt < 15:
        sleep(10)
        r = user.ccr_client.get_public_images(img_name=img_name)
        if get_value_from_json(r, "$..total") == 1:
            break
        else:
            cnt = cnt + 1
    assert cnt < 10, "超时：上传公有镜像失败"


def del_img_project(user: PAASClient, img_project):
    r = user.ccr_client.get_image_orgs(name=img_project)
    check_status_code(r)
    img_project_id = get_value_from_json(r, "$..project_id")
    assert img_project_id, f"查询私有镜像组织{img_project}失败"
    resp = user.ccr_client.get_imgs_by_imgProject(img_project)
    check_status_code(resp)
    img_list = get_value_from_json(resp, "$.data.data")
    if not img_list:
        pass
    else:
        for img in img_list:
            img_group_id = img['uuid']
            img_name = img['imageName']
            tentand_id = img['tentantId']
            user_id = img['userId']
            r = user.ccr_client.get_private_img_detail_info(
                img_name, tentand_id, img_project
            )
            check_status_code(r, 200)
            img_url = get_value_from_json(r, "$.data.images..imgUrl")
            img_type = get_value_from_json(r, "$.data.images..imgType")
            data = {
                "images": [
                    {
                        "id": "",
                        "imgUrl": img_url,
                        "tentantID": tentand_id,
                        "userID": user_id,
                    }
                ],
                "tagCount": 1,
                "imgType": img_type,
                "projectName": img_project,
                "imageName": img_name,
                "imageGroupId": img_group_id,
            }
            r_del = user.ccr_client.delete_private_image(data)
            check_status_code(r_del, 200)
            cnt = 0
            while cnt < 5:
                sleep(6)
                r = user.ccr_client.get_imgs_by_imgProject(
                    img_project, img_name=img_name
                )
                if get_value_from_json(r, "$..total") == 0:
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, f"删除镜像{img_name}失败"
    resp = user.ccr_client.delete_image_org(img_project_id)
    check_status_code(resp)
    time.sleep(3)
    check = user.ccr_client.get_image_orgs(name=img_project)
    assert get_value_from_json(check, "$..total") == 0, f"删除镜像组织{img_project}失败"


def del_public_img(user: PAASClient, img_name):
    res = user.ccr_client.get_public_images(img_name=img_name)
    check_status_code(res, 200)
    img_group_id = get_value_from_json(res, f"$..uuid")
    img_type = get_value_from_json(res, "$..imgType")
    assert img_group_id
    res_detail = user.ccr_client.get_public_img_detail_info(img_name, img_group_id)
    check_status_code(res_detail, 200)
    img_id = get_value_from_json(res_detail, f"$.data.images..uuid")
    img_url = get_value_from_json(res_detail, f"$.data.images..imgUrl")
    if img_id:
        tentant_id = get_value_from_json(res_detail, "$..tentantID")
        user_id = get_value_from_json(res_detail, "$..userID")
        data = {
            "images": [
                {
                    "id": img_id,
                    "imgUrl": img_url,
                    "tentantID": tentant_id,
                    "userID": user_id,
                }
            ],
            "tagCount": 1,
            "imgType": img_type,
            "projectName": "library",
            "imageName": img_name,
            "imageGroupId": img_group_id,
        }
    else:
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
            "imageName": img_name,
            "imageGroupId": img_group_id,
        }
    res_del = user.ccr_client.delete_public_image(data)
    check_status_code(res_del, 200)
    time.sleep(4)
    check = user.ccr_client.get_public_images(img_name=img_name)
    assert get_value_from_json(check, "$..total") == 0, "删除公有镜像失败"


def del_private_image_version(user: PAASClient, org_name, img_name):
    img_r = user.ccr_client.get_imgs_by_imgProject(org_name, img_name=img_name)
    check_status_code(img_r, 200)
    img_id = get_value_from_json(img_r, f"$..uuid")
    assert img_id, "获取镜像id失败"
    tentantid = user.login_info.default_project_id
    r = user.ccr_client.get_private_img_detail_info(img_name, tentantid, org_name)
    check_status_code(r, 200)

    img_url = get_value_from_json(r, "$.data.images..imgUrl")
    img_type = get_value_from_json(r, "$.data.images..imgType")
    data = {
        "images": [
            {
                "id": "",
                "imgUrl": img_url,
                "tentantID": tentantid,
                "userID": user.login_info.user_id,
            }
        ],
        "tagCount": 1,
        "imgType": img_type,
        "projectName": org_name,
        "imageName": img_name,
        "imageGroupId": img_id,
    }
    r_del = user.ccr_client.delete_private_image(data)
    check_status_code(r_del, 200)
    cnt = 0
    while cnt < 5:
        sleep(6)
        r = user.ccr_client.get_imgs_by_imgProject(org_name, img_name=img_name)
        if get_value_from_json(r, "$..total") == 0:
            break
        else:
            cnt = cnt + 1
    assert cnt < 5, f"删除镜像{img_name}失败"


def del_private_default_proj_images(user: PAASClient):
    """删除私有镜像默认项目中已auto开头的镜像"""
    img_project="user"
    resp = user.ccr_client.get_imgs_by_imgProject(img_project, page=1, size=100, img_name="auto")
    check_status_code(resp)
    img_list = get_value_from_json(resp, "$.data.data")
    if not img_list:
        pass
    else:
        for img in img_list:
            img_group_id = img['uuid']
            img_name = img['imageName']
            tentand_id = img['tentantId']
            user_id = img['userId']
            r = user.ccr_client.get_private_img_detail_info(
                img_name, tentand_id, img_project
            )
            check_status_code(r, 200)
            img_url = get_value_from_json(r, "$.data.images..imgUrl")
            img_type = get_value_from_json(r, "$.data.images..imgType")
            data = {
                "images": [
                    {
                        "id": "",
                        "imgUrl": img_url,
                        "tentantID": tentand_id,
                        "userID": user_id,
                    }
                ],
                "tagCount": 1,
                "imgType": img_type,
                "projectName": img_project,
                "imageName": img_name,
                "imageGroupId": img_group_id,
            }
            r_del = user.ccr_client.delete_private_image(data)
            check_status_code(r_del, 200)
            cnt = 0
            while cnt < 5:
                sleep(6)
                r = user.ccr_client.get_imgs_by_imgProject(
                    img_project, img_name=img_name
                )
                if get_value_from_json(r, "$..total") == 0:
                    break
                else:
                    cnt = cnt + 1
            assert cnt < 5, f"删除镜像{img_name}失败"