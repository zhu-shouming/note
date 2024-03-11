import datetime
from operator import truediv
from re import T

import allure
import urllib3
import yaml
from _pytest import pathlib
from py.path import local

from resource.utils.common import *

import base64
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA

urllib3.disable_warnings()


config_dir = local(pathlib.Path(__file__).parent.parent.parent).join('config')
config_file = config_dir.join("env.yml")
with open(config_file, 'r', encoding="utf-8") as f:
    envs = yaml.load(f, Loader=yaml.FullLoader)


class PAASLogin:

    def __init__(self, username, password, login_ip, login_port):
        self.username = username
        self.password = password
        self.login_ip = login_ip
        self.login_port = login_port
        self.ss = requests.Session()
        self.ss.trust_env = False
        self.user_id = None
        self.user_role = None
        self.default_project_id = None
        self._login()

    def _login(self):
        """
        登录用户控制台用户类
        用户的身份信息包括：用户名，密码，登录IP和登录端口
        """

        url = f"https://{self.login_ip}:{self.login_port}/api/sys/oapi/v1/double_factor/login"
        payload = {
            "password": self._gen_pwd(self.password),
            "domain": "default",
            "rsa": True,
            "username": self.username
        }
        login_response = requests.post(url, json=payload, verify=False)
        self._allure_attach(url, login_response, data=payload)
        check_status_code(login_response)
        token = get_value_from_json(login_response, "$..token")
        self.ss.headers.update({"X-Auth-Token": token})
        self.user_id = get_value_from_json(login_response, "$..id")
        self.user_role = get_value_from_json(login_response, "$..role_name")
        self.default_project_id = get_value_from_json(login_response, "$..default_project_id")

    def _gen_pwd(self, pwd):
        """
        生成加密后的登录密码

        :param pwd: 明文密码
        :return:
        """
        public_key = envs['PUBLIC_KEY']
        key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
        rsakey = RSA.importKey(key)
        cipher = Cipher_pksc1_v1_5.new(rsakey)
        encrypt_text = cipher.encrypt(pwd.encode())
        cipher_text_tmp = base64.b64encode(encrypt_text)
        encrypt_res = cipher_text_tmp.decode()
        return encrypt_res

    def _allure_attach(self, url, response, headers=None, data=None):
        body = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        ) + "\n\nURL：     {0}\n状态码： {1}\n请求头： {2}\n请求体： {3}\n响应体： {4}".format(
            url, response.status_code, headers, data, response.text
        )
        allure.attach(body=body, name="请求详细信息")