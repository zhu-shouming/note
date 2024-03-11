import os
import sys
import pytest

from setup import setup_env

if __name__ == '__main__':
    ####初始化环境
    setup_env()
    # ###执行用例
    length = len(sys.argv)
    if length == 1:
        pytest.main(['-n 2', '--alluredir', './report', '--clean-alluredir'])
    else:
        models = sys.argv[1]
        for item in sys.argv[2:]:
            models += ' or ' + item
        pytest.main(['-n 2', '--alluredir', './report', '-m', models, '--clean-alluredir'])
    # pytest.main(['-n 1', '--alluredir', './report', '-m', "appmgmt and L0", '--clean-alluredir'])
    os.system('allure generate ./report -o ./report/html --clean')

