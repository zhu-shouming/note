from resource.base.client import PAASClient
from resource.base.login import PAASLogin
from config.config import settings
from resource.utils.common import get_value_from_json


def check_resource():
    """检查kaas集群信息"""
    admin = PAASClient(PAASLogin(settings['USERNAME'], settings['PASSWORD'], settings['HOST'], settings['PORT']))
    # res = admin.cce_client.get_cce_list()
    # cluster_info = get_value_from_json(res, f"$.data[?(@.name=='{settings.CLUSTER_NAME}')]")
    # assert cluster_info, "kaas集群信息不存在"
    # cluster_id = cluster_info['uuid']
    # assert cluster_id == settings.CLUSTER_ID, "集群ID信息错误"
    # res = admin.cce_client.get_storage_classes(cluster_id)
    # storage_class_info = get_value_from_json(res, f"$..data[?(@.name=='auto')]")    # 数据驱动中名字固定为auto
    # assert storage_class_info, "集群存储信息不存在"

    """检查用户信息"""
    # res = admin.sys_client.get_root_user_list()
    # pro_admin_info = get_value_from_json(res, f"$..res[?(@.name=='{settings.PROJ_ADMIN}')]")
    # assert pro_admin_info, "组织用户不存在"
    # pro_user_info = get_value_from_json(res, f"$..res[?(@.name=='{settings.PROJ_USER}')]")
    # assert pro_user_info, "普通用户不存在"

    """检查应用包信息"""

if __name__ == '__main__':
    check_resource()
