# import allure
import allure
import urllib3
import datetime

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings()


class RestAPIBase(object):
    """
    特性基类, 封装底层Requests接口
    """

    def __init__(self, user):
        self.base_url = None
        self.ss = None
        self._paas_init(user)

    def _paas_init(self, user):
        self.base_url = 'https://' + user.login_ip + ":" + user.login_port
        self.ss = user.ss

    def _get(self, uri, headers=None):
        url = self.base_url + uri
        if headers is None:
            headers = self.ss.headers
        response = self.ss.get(url, headers=headers, verify=False)
        self._allure_attach(url, response, method="GET", headers=headers, data=None)
        return response

    def _post(self, uri, json=None, data=None, headers=None):
        url = self.base_url + uri
        if headers is None:
            headers = self.ss.headers
        response = self.ss.post(
            url, json=json, data=data, headers=headers, verify=False
        )
        if json is None:
            self._allure_attach(url, response, headers=headers, data=data)
        if data is None:
            self._allure_attach(url, response, method="POST", headers=headers, data=json)
        return response

    def _put(self, uri, json=None, data=None, headers=None):
        url = self.base_url + uri
        if headers is None:
            headers = self.ss.headers
        response = self.ss.put(url, json=json, data=data, headers=headers, verify=False)
        body = json if bool(json) else data
        self._allure_attach(url, response, method="PUT", headers=headers, data=body)
        return response

    def _delete(self, uri, data=None, headers=None):
        url = self.base_url + uri
        if headers is None:
            headers = self.ss.headers
        response = self.ss.delete(url, json=data, headers=headers, verify=False)
        self._allure_attach(url, response, method="DELETE", headers=headers, data=data)
        return response

    def _patch(self, uri, data, headers=None):
        url = self.base_url + uri
        if headers is None:
            headers = self.ss.headers
        response = self.ss.patch(url, json=data, headers=headers, verify=False)
        self._allure_attach(url, response, headers=headers, data=data)
        return response

    def _get_file(self, uri, headers=None):
        url = self.base_url + uri
        if headers is None:
            headers = self.ss.headers
        response = self.ss.get(url, headers=headers, verify=False)
        self._allure_attach(url, response, headers=headers, data=None)
        return response

    def _allure_attach(self, url, response, method=None, headers=None, data=None):
        body = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        ) + "\n\nURL：     {0}\n状态码： {1}\n请求类型： {2}\n请求头： {3}\n请求体： {4}\n响应体： {5}".format(
            url, response.status_code, method, headers, data, response.text
        )
        allure.attach(body=body, name="请求详细信息")
