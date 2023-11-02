import pytest

from config.config import settings
from resource.base.client import PAASClient
from resource.base.login import PAASLogin


def pytest_addoption(parser):
    parser.addoption(
        "--configfile", action="store", default="config/config.py", help="指定环境配置文件"
    )


@pytest.fixture(autouse=True, scope="function")
def paas_admin_login():
    return PAASClient(PAASLogin(settings['USERNAME'], settings['PASSWORD'], settings['HOST'], settings['PORT']))


@pytest.fixture(autouse=True, scope="function")
def paas_proj_admin_login():
    return PAASClient(PAASLogin(settings['PROJ_ADMIN'], settings['PASSWORD'], settings['HOST'], settings['PORT']))


@pytest.fixture(autouse=True, scope="function")
def paas_proj_user_login():
    return PAASClient(PAASLogin(settings['PROJ_USER'], settings['PASSWORD'], settings['HOST'], settings['PORT']))
