from resource.base.login import PAASLogin
from scripts.app_mgmt.api_app_mgmt import AppMgmtAPI
from scripts.cce.api_cce import CCEAPI
from scripts.deploy.api_deploy import DeployAPI
from scripts.gateway.api_gateway import GatewayAPI
from scripts.msg.api_msg import MsgAPI
from scripts.sys.api_sys import SysAPI
from scripts.ccr.api_ccr import CCRAPI


class PAASClient(object):
    def __init__(self, login_info: PAASLogin):
        self.login_info = login_info
        self.app_mgmt_client = AppMgmtAPI(login_info)
        self.deploy_client = DeployAPI(login_info)
        self.cce_client = CCEAPI(login_info)
        self.msg_client = MsgAPI(login_info)
        self.sys_client = SysAPI(login_info)
        self.ccr_client = CCRAPI(login_info)
        self.gw_client = GatewayAPI(login_info)
